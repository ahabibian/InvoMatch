from datetime import date

from invomatch.domain.matching.features import InvoiceRecord, PaymentRecord
from invomatch.services.matching.features import build_match_features
from invomatch.services.matching.rules import RuleEngine


def test_rule_engine_scores_strong_exact_match() -> None:
    invoice = InvoiceRecord(
        invoice_id="inv_101",
        supplier_name="Nordic Supplies AB",
        invoice_number="INV-2026-101",
        invoice_date=date(2026, 3, 10),
        due_date=date(2026, 3, 20),
        currency="SEK",
        gross_amount=1500.0,
        reference_text="March consulting",
        ocr_confidence=0.95,
    )

    payment = PaymentRecord(
        payment_id="pay_101",
        counterparty_name="Nordic Supplies AB",
        payment_date=date(2026, 3, 12),
        currency="SEK",
        amount=1500.0,
        reference_text="Payment INV2026101",
        bank_reference="INV-2026-101",
    )

    features = build_match_features(invoice, payment)
    result = RuleEngine().evaluate(features)

    assert result.is_hard_blocked is False
    assert result.normalized_score >= 90.0
    assert "exact_amount_match" in result.reason_codes
    assert "invoice_number_normalized_match" in result.reason_codes
    assert "supplier_name_exact_match" in result.reason_codes


def test_rule_engine_hard_blocks_currency_mismatch() -> None:
    invoice = InvoiceRecord(
        invoice_id="inv_102",
        supplier_name="Acme Consulting AB",
        invoice_number="INV-102",
        invoice_date=date(2026, 2, 1),
        due_date=date(2026, 2, 15),
        currency="SEK",
        gross_amount=1000.0,
    )

    payment = PaymentRecord(
        payment_id="pay_102",
        counterparty_name="Acme Consulting AB",
        payment_date=date(2026, 2, 5),
        currency="EUR",
        amount=1000.0,
        reference_text="INV102",
    )

    features = build_match_features(invoice, payment)
    result = RuleEngine().evaluate(features)

    assert result.is_hard_blocked is True
    assert result.raw_score == 0.0
    assert result.normalized_score == 0.0
    assert "currency_mismatch" in result.hard_block_codes


def test_rule_engine_applies_penalties_for_low_quality_signals() -> None:
    invoice = InvoiceRecord(
        invoice_id="inv_103",
        supplier_name="Studio Signal AB",
        invoice_number="SIG-103",
        invoice_date=date(2026, 1, 10),
        due_date=date(2026, 1, 20),
        currency="SEK",
        gross_amount=500.0,
        ocr_confidence=0.42,
        duplicate_risk_flags=("duplicate_invoice_candidate",),
    )

    payment = PaymentRecord(
        payment_id="pay_103",
        counterparty_name="Studio Signal AB",
        payment_date=date(2026, 1, 5),
        currency="SEK",
        amount=500.0,
        reference_text="SIG103",
        duplicate_risk_flags=("duplicate_payment_candidate",),
    )

    features = build_match_features(invoice, payment)
    result = RuleEngine().evaluate(features)

    assert result.is_hard_blocked is False
    assert "duplicate_risk_flag" in result.penalty_codes
    assert "ocr_low_confidence" in result.penalty_codes
    assert "payment_before_invoice_date" in result.penalty_codes
    assert result.normalized_score < 100.0


def test_rule_engine_penalizes_large_amount_drift() -> None:
    invoice = InvoiceRecord(
        invoice_id="inv_104",
        supplier_name="North Star Solutions AB",
        invoice_number="NS-104",
        invoice_date=date(2026, 3, 1),
        due_date=date(2026, 3, 30),
        currency="SEK",
        gross_amount=2000.0,
    )

    payment = PaymentRecord(
        payment_id="pay_104",
        counterparty_name="North Star Solutions AB",
        payment_date=date(2026, 3, 25),
        currency="SEK",
        amount=1600.0,
        reference_text="March settlement",
    )

    features = build_match_features(invoice, payment)
    result = RuleEngine().evaluate(features)

    assert "high_amount_drift" in result.penalty_codes
    assert result.normalized_score < 40.0