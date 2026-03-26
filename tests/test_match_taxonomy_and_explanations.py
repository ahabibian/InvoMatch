from datetime import date

from invomatch.domain.matching.decisioning import CandidateContext
from invomatch.domain.matching.features import InvoiceRecord, PaymentRecord
from invomatch.domain.matching.models import DecisionType
from invomatch.services.matching.decision_builder import DecisionBuilder
from invomatch.services.matching.explanations import build_decision_summary
from invomatch.services.matching.features import build_match_features
from invomatch.services.matching.rules import RuleEngine


def _pair(
    *,
    invoice_id: str,
    payment_id: str,
    currency: str = "SEK",
    payment_currency: str = "SEK",
    gross_amount: float = 1000.0,
    payment_amount: float = 1000.0,
    payment_date: date = date(2026, 3, 12),
    reference_text: str = "Payment INV2026300",
    bank_reference: str = "INV-2026-300",
) -> tuple[InvoiceRecord, PaymentRecord]:
    invoice = InvoiceRecord(
        invoice_id=invoice_id,
        supplier_name="Nordic Supplies AB",
        invoice_number="INV-2026-300",
        invoice_date=date(2026, 3, 10),
        due_date=date(2026, 3, 20),
        currency=currency,
        gross_amount=gross_amount,
        reference_text="Monthly consulting",
        ocr_confidence=0.95,
    )

    payment = PaymentRecord(
        payment_id=payment_id,
        counterparty_name="Nordic Supplies AB",
        payment_date=payment_date,
        currency=payment_currency,
        amount=payment_amount,
        reference_text=reference_text,
        bank_reference=bank_reference,
    )

    return invoice, payment


def test_explanation_summary_for_auto_approved_match() -> None:
    invoice, payment = _pair(invoice_id="inv_301", payment_id="pay_301")
    features = build_match_features(invoice, payment)
    score_result = RuleEngine().evaluate(features)

    summary = build_decision_summary(
        decision_type=DecisionType.ONE_TO_ONE,
        score_result=score_result,
        context=CandidateContext(candidate_count=1, competing_candidate_count=0, top_score_gap=20.0),
    )

    assert "auto-approved" in summary


def test_taxonomy_for_hard_block_currency_rejection() -> None:
    invoice, payment = _pair(
        invoice_id="inv_302",
        payment_id="pay_302",
        currency="SEK",
        payment_currency="EUR",
    )
    features = build_match_features(invoice, payment)
    score_result = RuleEngine().evaluate(features)

    decision = DecisionBuilder().build(
        decision_id="dec_302",
        run_id="run_302",
        features=features,
        score_result=score_result,
        context=CandidateContext(),
    )

    assert decision.primary_mismatch_code == "CURRENCY_POLICY_REJECTED"
    assert decision.explanation.summary == "Candidate rejected by policy due to a hard-block rule."


def test_taxonomy_for_ambiguous_candidate() -> None:
    invoice, payment = _pair(invoice_id="inv_303", payment_id="pay_303")
    features = build_match_features(invoice, payment)
    score_result = RuleEngine().evaluate(features)

    decision = DecisionBuilder().build(
        decision_id="dec_303",
        run_id="run_303",
        features=features,
        score_result=score_result,
        context=CandidateContext(candidate_count=3, competing_candidate_count=2, top_score_gap=4.0),
    )

    assert decision.primary_mismatch_code == "AMBIGUOUS_MULTIPLE_PAYMENTS"
    assert "LOW_TOP_SCORE_GAP" in decision.secondary_mismatch_codes


def test_taxonomy_for_review_required_includes_secondary_codes() -> None:
    invoice, payment = _pair(
        invoice_id="inv_304",
        payment_id="pay_304",
        gross_amount=1000.0,
        payment_amount=990.0,
        payment_date=date(2026, 3, 30),
        reference_text="Payment INV2026300 monthly consulting partial",
        bank_reference="INV-2026-300 monthly consulting",
    )
    features = build_match_features(invoice, payment)
    score_result = RuleEngine().evaluate(features)

    decision = DecisionBuilder().build(
        decision_id="dec_304",
        run_id="run_304",
        features=features,
        score_result=score_result,
        context=CandidateContext(),
    )

    assert decision.primary_mismatch_code == "WEAK_MATCH_SIGNAL"
    assert "EXCESSIVE_DATE_DRIFT" in decision.secondary_mismatch_codes