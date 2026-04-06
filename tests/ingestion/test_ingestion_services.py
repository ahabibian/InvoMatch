from decimal import Decimal

from invomatch.ingestion.models.ingestion_result import IngestionStatus
from invomatch.ingestion.models.normalized_models import (
    NormalizedInvoice,
    NormalizedPayment,
)
from invomatch.ingestion.models.raw_models import RawInvoiceInput, RawPaymentInput
from invomatch.ingestion.services import ingest_invoice_input, ingest_payment_input


def test_ingest_invoice_returns_normalized_entity_with_flags_for_missing_optional_fields():
    raw = RawInvoiceInput(
        external_id=" ext-1 ",
        invoice_number=" inv 001 ",
        issue_date="2026-04-07",
        currency="sek",
        gross_amount="100,456",
    )

    result = ingest_invoice_input(raw)

    assert result.status == IngestionStatus.ACCEPTED_WITH_FLAGS
    assert isinstance(result.normalized, NormalizedInvoice)
    assert result.normalized.external_id == "ext-1"
    assert result.normalized.invoice_number == "INV001"
    assert result.normalized.currency == "SEK"
    assert result.normalized.gross_amount == Decimal("100.46")
    assert result.validation.is_valid is True
    assert {warning.field for warning in result.validation.warnings} == {"due_date", "counterparty"}


def test_ingest_invoice_rejects_invalid_required_fields_and_returns_no_normalized_entity():
    raw = RawInvoiceInput(
        invoice_number=None,
        issue_date="not-a-date",
        currency="XXX",
        gross_amount="abc",
    )

    result = ingest_invoice_input(raw)

    assert result.status == IngestionStatus.REJECTED
    assert result.normalized is None
    assert result.validation.is_valid is False
    assert {error.field for error in result.validation.errors} == {
        "invoice_number",
        "issue_date",
        "currency",
        "gross_amount",
    }


def test_ingest_payment_returns_normalized_entity_with_flags_when_counterparty_missing():
    raw = RawPaymentInput(
        external_id=" pay-1 ",
        payment_reference=" rf 12345 ",
        payment_date="2026-04-07",
        amount="99.5",
        currency="eur",
    )

    result = ingest_payment_input(raw)

    assert result.status == IngestionStatus.ACCEPTED_WITH_FLAGS
    assert isinstance(result.normalized, NormalizedPayment)
    assert result.normalized.external_id == "pay-1"
    assert result.normalized.payment_reference == "RF12345"
    assert result.normalized.currency == "EUR"
    assert result.normalized.amount == Decimal("99.50")
    assert result.validation.is_valid is True
    assert [warning.field for warning in result.validation.warnings] == ["counterparty"]


def test_ingest_payment_rejects_invalid_required_fields_and_returns_no_normalized_entity():
    raw = RawPaymentInput(
        payment_reference="",
        payment_date="invalid-date",
        amount="not-a-number",
        currency="bad",
    )

    result = ingest_payment_input(raw)

    assert result.status == IngestionStatus.REJECTED
    assert result.normalized is None
    assert result.validation.is_valid is False
    assert {error.field for error in result.validation.errors} == {
        "payment_reference",
        "payment_date",
        "amount",
        "currency",
    }