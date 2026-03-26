from datetime import date

from invomatch.domain.matching.features import InvoiceRecord, PaymentRecord
from invomatch.services.matching.features import build_match_features


def test_build_match_features_exact_amount_and_invoice_reference_match() -> None:
    invoice = InvoiceRecord(
        invoice_id="inv_001",
        supplier_name="Nordic Supplies AB",
        invoice_number="INV-2026-001",
        invoice_date=date(2026, 3, 10),
        due_date=date(2026, 3, 20),
        currency="SEK",
        gross_amount=1250.0,
        reference_text="Consulting services March",
        ocr_confidence=0.91,
    )

    payment = PaymentRecord(
        payment_id="pay_001",
        counterparty_name="Nordic Supplies AB",
        payment_date=date(2026, 3, 12),
        currency="SEK",
        amount=1250.0,
        reference_text="Payment INV2026001",
        bank_reference="INV-2026-001",
    )

    features = build_match_features(invoice, payment)

    assert features.amount_exact_match is True
    assert features.amount_delta_absolute == 0.0
    assert features.currency_match is True
    assert features.invoice_number_normalized_match is True
    assert features.invoice_number_in_payment_reference is True
    assert features.supplier_name_exact_match is True
    assert features.combined_reference_signal_score == 1.0
    assert features.date_delta_days == 2
    assert features.payment_before_invoice is False
    assert features.payment_after_due_date is False


def test_build_match_features_detects_amount_and_currency_mismatch() -> None:
    invoice = InvoiceRecord(
        invoice_id="inv_002",
        supplier_name="Acme Consulting AB",
        invoice_number="A-55-900",
        invoice_date=date(2026, 2, 1),
        due_date=date(2026, 2, 15),
        currency="SEK",
        gross_amount=1000.0,
    )

    payment = PaymentRecord(
        payment_id="pay_002",
        counterparty_name="Acme Consulting AB",
        payment_date=date(2026, 2, 28),
        currency="EUR",
        amount=850.0,
        reference_text="Settlement February",
    )

    features = build_match_features(invoice, payment)

    assert features.amount_exact_match is False
    assert features.amount_delta_absolute == 150.0
    assert features.amount_delta_percentage == 0.15
    assert features.currency_match is False
    assert features.payment_after_due_date is True
    assert features.invoice_number_normalized_match is False

    # مهم: اینجا انتظار نداریم صفر باشد، چون supplier overlap وجود دارد
    assert features.reference_token_overlap_score > 0.0
    assert features.combined_reference_signal_score > 0.0


def test_build_match_features_flags_low_ocr_and_duplicate_risk() -> None:
    invoice = InvoiceRecord(
        invoice_id="inv_003",
        supplier_name="Studio Signal AB",
        invoice_number="SIG-77",
        invoice_date=date(2026, 1, 5),
        due_date=None,
        currency="SEK",
        gross_amount=500.0,
        ocr_confidence=0.42,
        duplicate_risk_flags=("duplicate_invoice_candidate",),
    )

    payment = PaymentRecord(
        payment_id="pay_003",
        counterparty_name="Studio Signal AB",
        payment_date=date(2026, 1, 2),
        currency="SEK",
        amount=500.0,
        duplicate_risk_flags=("duplicate_payment_candidate",),
    )

    features = build_match_features(invoice, payment)

    assert features.invoice_ocr_low_confidence_flag is True
    assert features.duplicate_risk_flag is True
    assert features.payment_before_invoice is True
    assert features.payment_after_due_date is None


def test_build_match_features_supplier_name_normalization_handles_punctuation() -> None:
    invoice = InvoiceRecord(
        invoice_id="inv_004",
        supplier_name="North-Star Solutions AB",
        invoice_number="NS-444",
        invoice_date=date(2026, 3, 1),
        due_date=date(2026, 3, 30),
        currency="SEK",
        gross_amount=2200.0,
    )

    payment = PaymentRecord(
        payment_id="pay_004",
        counterparty_name="North Star Solutions AB",
        payment_date=date(2026, 3, 15),
        currency="SEK",
        amount=2200.0,
        reference_text="NS444 March payment",
    )

    features = build_match_features(invoice, payment)

    assert features.supplier_name_exact_match is False
    assert features.supplier_name_normalized_match is True
    assert features.invoice_number_in_payment_reference is True
    assert features.reference_token_overlap_score > 0.0