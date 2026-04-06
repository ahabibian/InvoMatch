from invomatch.ingestion.models.duplicate_models import DuplicateClassification
from invomatch.ingestion.models.raw_models import RawInvoiceInput, RawPaymentInput
from invomatch.ingestion.services import (
    classify_invoice_duplicate,
    classify_payment_duplicate,
    ingest_invoice_input,
    ingest_payment_input,
)


def test_invoice_duplicate_classification_is_unique_when_no_existing_result():
    current = ingest_invoice_input(
        RawInvoiceInput(
            invoice_number="INV-001",
            issue_date="2026-04-07",
            currency="SEK",
            gross_amount="100.00",
        )
    )

    result = classify_invoice_duplicate(current=current, existing=None)

    assert result.classification == DuplicateClassification.UNIQUE


def test_invoice_duplicate_classification_detects_exact_replay():
    raw = RawInvoiceInput(
        invoice_number="INV-001",
        issue_date="2026-04-07",
        currency="SEK",
        gross_amount="100.00",
    )

    existing = ingest_invoice_input(raw)
    current = ingest_invoice_input(raw)

    result = classify_invoice_duplicate(current=current, existing=existing)

    assert result.classification == DuplicateClassification.EXACT_REPLAY


def test_invoice_duplicate_classification_detects_semantic_duplicate():
    existing = ingest_invoice_input(
        RawInvoiceInput(
            invoice_number="INV 001",
            issue_date="2026-04-07",
            currency="SEK",
            gross_amount="100.00",
            counterparty="Vendor A",
        )
    )
    current = ingest_invoice_input(
        RawInvoiceInput(
            invoice_number="INV001",
            issue_date="2026-04-07",
            currency="sek",
            gross_amount="100.0",
            counterparty="Vendor B",
        )
    )

    result = classify_invoice_duplicate(current=current, existing=existing)

    assert result.classification == DuplicateClassification.SEMANTIC_DUPLICATE


def test_invoice_duplicate_classification_detects_conflict():
    existing = ingest_invoice_input(
        RawInvoiceInput(
            invoice_number="INV-001",
            issue_date="2026-04-07",
            currency="SEK",
            gross_amount="100.00",
        )
    )
    current = ingest_invoice_input(
        RawInvoiceInput(
            invoice_number="INV-001",
            issue_date="2026-04-07",
            currency="SEK",
            gross_amount="120.00",
        )
    )

    result = classify_invoice_duplicate(current=current, existing=existing)

    assert result.classification == DuplicateClassification.CONFLICT


def test_payment_duplicate_classification_detects_exact_replay():
    raw = RawPaymentInput(
        payment_reference="RF12345",
        payment_date="2026-04-07",
        amount="99.50",
        currency="EUR",
    )

    existing = ingest_payment_input(raw)
    current = ingest_payment_input(raw)

    result = classify_payment_duplicate(current=current, existing=existing)

    assert result.classification == DuplicateClassification.EXACT_REPLAY


def test_payment_duplicate_classification_detects_semantic_duplicate():
    existing = ingest_payment_input(
        RawPaymentInput(
            payment_reference="RF 12345",
            payment_date="2026-04-07",
            amount="99.50",
            currency="EUR",
            counterparty="A",
        )
    )
    current = ingest_payment_input(
        RawPaymentInput(
            payment_reference="RF12345",
            payment_date="2026-04-07",
            amount="99.5",
            currency="eur",
            counterparty="B",
        )
    )

    result = classify_payment_duplicate(current=current, existing=existing)

    assert result.classification == DuplicateClassification.SEMANTIC_DUPLICATE


def test_payment_duplicate_classification_detects_conflict():
    existing = ingest_payment_input(
        RawPaymentInput(
            payment_reference="RF12345",
            payment_date="2026-04-07",
            amount="99.50",
            currency="EUR",
        )
    )
    current = ingest_payment_input(
        RawPaymentInput(
            payment_reference="RF12345",
            payment_date="2026-04-07",
            amount="109.50",
            currency="EUR",
        )
    )

    result = classify_payment_duplicate(current=current, existing=existing)

    assert result.classification == DuplicateClassification.CONFLICT