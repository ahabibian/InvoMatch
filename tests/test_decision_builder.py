from datetime import date

from invomatch.domain.matching.decisioning import CandidateContext
from invomatch.domain.matching.features import InvoiceRecord, PaymentRecord
from invomatch.domain.matching.models import ConfidenceLevel, DecisionStatus, DecisionType
from invomatch.services.matching.decision_builder import DecisionBuilder
from invomatch.services.matching.features import build_match_features
from invomatch.services.matching.rules import RuleEngine


def _build_invoice_payment_pair(
    *,
    invoice_id: str,
    payment_id: str,
    supplier_name: str = "Nordic Supplies AB",
    invoice_number: str = "INV-2026-200",
    invoice_date: date = date(2026, 3, 10),
    due_date: date = date(2026, 3, 20),
    currency: str = "SEK",
    gross_amount: float = 1500.0,
    payment_date: date = date(2026, 3, 12),
    payment_amount: float = 1500.0,
    payment_currency: str = "SEK",
    reference_text: str = "Payment INV2026200",
    bank_reference: str = "INV-2026-200",
) -> tuple[InvoiceRecord, PaymentRecord]:
    invoice = InvoiceRecord(
        invoice_id=invoice_id,
        supplier_name=supplier_name,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        due_date=due_date,
        currency=currency,
        gross_amount=gross_amount,
        reference_text="March consulting",
        ocr_confidence=0.95,
    )

    payment = PaymentRecord(
        payment_id=payment_id,
        counterparty_name=supplier_name,
        payment_date=payment_date,
        currency=payment_currency,
        amount=payment_amount,
        reference_text=reference_text,
        bank_reference=bank_reference,
    )
    return invoice, payment


def test_decision_builder_auto_approves_dominant_high_confidence_match() -> None:
    invoice, payment = _build_invoice_payment_pair(
        invoice_id="inv_201",
        payment_id="pay_201",
    )
    features = build_match_features(invoice, payment)
    score_result = RuleEngine().evaluate(features)

    decision = DecisionBuilder().build(
        decision_id="dec_201",
        run_id="run_201",
        features=features,
        score_result=score_result,
        context=CandidateContext(
            candidate_count=2,
            competing_candidate_count=1,
            top_score_gap=20.0,
        ),
    )

    assert decision.decision_type == DecisionType.ONE_TO_ONE
    assert decision.confidence == ConfidenceLevel.HIGH
    assert decision.status == DecisionStatus.AUTO_APPROVED
    assert decision.auto_action_eligible is True
    assert decision.primary_mismatch_code is None


def test_decision_builder_marks_close_competition_as_ambiguous() -> None:
    invoice, payment = _build_invoice_payment_pair(
        invoice_id="inv_202",
        payment_id="pay_202",
    )
    features = build_match_features(invoice, payment)
    score_result = RuleEngine().evaluate(features)

    decision = DecisionBuilder().build(
        decision_id="dec_202",
        run_id="run_202",
        features=features,
        score_result=score_result,
        context=CandidateContext(
            candidate_count=3,
            competing_candidate_count=2,
            top_score_gap=5.0,
        ),
    )

    assert decision.decision_type == DecisionType.AMBIGUOUS
    assert decision.confidence == ConfidenceLevel.MEDIUM
    assert decision.status == DecisionStatus.PROPOSED
    assert decision.auto_action_eligible is False
    assert decision.primary_mismatch_code == "AMBIGUOUS_MULTIPLE_PAYMENTS"


def test_decision_builder_routes_mid_score_to_review_required() -> None:
    invoice, payment = _build_invoice_payment_pair(
        invoice_id="inv_203",
        payment_id="pay_203",
        gross_amount=1500.0,
        payment_amount=1430.0,
        reference_text="Partial payment INV2026200",
        bank_reference="Settlement batch",
    )
    features = build_match_features(invoice, payment)
    score_result = RuleEngine().evaluate(features)

    decision = DecisionBuilder().build(
        decision_id="dec_203",
        run_id="run_203",
        features=features,
        score_result=score_result,
        context=CandidateContext(
            candidate_count=1,
            competing_candidate_count=0,
            top_score_gap=None,
        ),
    )

    assert decision.decision_type == DecisionType.REVIEW_REQUIRED
    assert decision.confidence == ConfidenceLevel.MEDIUM
    assert decision.status == DecisionStatus.PROPOSED
    assert decision.auto_action_eligible is False
    assert decision.primary_mismatch_code == "WEAK_MATCH_SIGNAL"


def test_decision_builder_converts_hard_block_to_unmatched_rejected() -> None:
    invoice, payment = _build_invoice_payment_pair(
        invoice_id="inv_204",
        payment_id="pay_204",
        currency="SEK",
        payment_currency="EUR",
    )
    features = build_match_features(invoice, payment)
    score_result = RuleEngine().evaluate(features)

    decision = DecisionBuilder().build(
        decision_id="dec_204",
        run_id="run_204",
        features=features,
        score_result=score_result,
        context=CandidateContext(),
    )

    assert decision.decision_type == DecisionType.UNMATCHED
    assert decision.confidence == ConfidenceLevel.REJECTED
    assert decision.status == DecisionStatus.REJECTED
    assert decision.auto_action_eligible is False
    assert decision.primary_mismatch_code == "CURRENCY_POLICY_REJECTED"


def test_decision_builder_marks_low_score_as_unmatched() -> None:
    invoice, payment = _build_invoice_payment_pair(
        invoice_id="inv_205",
        payment_id="pay_205",
        gross_amount=1500.0,
        payment_amount=900.0,
        payment_date=date(2026, 4, 30),
        reference_text="Unclear transfer",
        bank_reference="Misc",
    )
    features = build_match_features(invoice, payment)
    score_result = RuleEngine().evaluate(features)

    decision = DecisionBuilder().build(
        decision_id="dec_205",
        run_id="run_205",
        features=features,
        score_result=score_result,
        context=CandidateContext(
            candidate_count=1,
            competing_candidate_count=0,
            top_score_gap=None,
        ),
    )

    assert decision.decision_type == DecisionType.UNMATCHED
    assert decision.confidence == ConfidenceLevel.LOW
    assert decision.status == DecisionStatus.PROPOSED
    assert decision.auto_action_eligible is False
    assert decision.primary_mismatch_code in {"NO_CANDIDATE_AMOUNT", "NO_CANDIDATE_DATE", "WEAK_REFERENCE_SIGNAL"}