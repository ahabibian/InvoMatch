from invomatch.ingestion.models.ingestion_result import IngestionStatus
from invomatch.ingestion.models.raw_models import RawInvoiceInput, RawPaymentInput
from invomatch.ingestion.models.validation_models import (
    ValidationError,
    ValidationResult,
    ValidationWarning,
)
from invomatch.ingestion.services.decision_builder import build_ingestion_status
from invomatch.ingestion.validators import (
    validate_invoice_input,
    validate_payment_input,
)


def test_invoice_validation_accepts_with_flags_when_optional_fields_missing():
    raw = RawInvoiceInput(
        invoice_number="INV 001",
        issue_date="2026-04-07",
        currency="SEK",
        gross_amount="100.00",
    )

    result = validate_invoice_input(raw)

    assert result.is_valid is True
    assert result.errors == []
    assert {warning.field for warning in result.warnings} == {"due_date", "counterparty"}


def test_invoice_validation_rejects_missing_required_fields():
    raw = RawInvoiceInput()

    result = validate_invoice_input(raw)

    assert result.is_valid is False
    assert {error.field for error in result.errors} == {
        "invoice_number",
        "issue_date",
        "currency",
        "gross_amount",
    }


def test_invoice_validation_rejects_invalid_due_date_when_present():
    raw = RawInvoiceInput(
        invoice_number="INV-001",
        issue_date="2026-04-07",
        due_date="not-a-date",
        currency="SEK",
        gross_amount="100.00",
    )

    result = validate_invoice_input(raw)

    assert result.is_valid is False
    assert any(error.field == "due_date" for error in result.errors)


def test_payment_validation_accepts_with_flags_when_optional_counterparty_missing():
    raw = RawPaymentInput(
        payment_reference="RF 12345",
        payment_date="2026-04-07",
        amount="99.50",
        currency="EUR",
    )

    result = validate_payment_input(raw)

    assert result.is_valid is True
    assert result.errors == []
    assert [warning.field for warning in result.warnings] == ["counterparty"]


def test_payment_validation_rejects_missing_required_fields():
    raw = RawPaymentInput()

    result = validate_payment_input(raw)

    assert result.is_valid is False
    assert {error.field for error in result.errors} == {
        "payment_reference",
        "payment_date",
        "amount",
        "currency",
    }


def test_decision_builder_returns_rejected_when_errors_exist():
    validation = ValidationResult(
        is_valid=False,
        errors=[
            ValidationError(
                field="currency",
                code="required_or_invalid",
                message="Currency invalid.",
            )
        ],
        warnings=[],
    )

    assert build_ingestion_status(validation) == IngestionStatus.REJECTED


def test_decision_builder_returns_accepted_with_flags_when_only_warnings_exist():
    validation = ValidationResult(
        is_valid=True,
        errors=[],
        warnings=[
            ValidationWarning(
                field="counterparty",
                code="missing_optional",
                message="Missing counterparty.",
            )
        ],
    )

    assert build_ingestion_status(validation) == IngestionStatus.ACCEPTED_WITH_FLAGS


def test_decision_builder_returns_accepted_clean_when_no_errors_or_warnings_exist():
    validation = ValidationResult(
        is_valid=True,
        errors=[],
        warnings=[],
    )

    assert build_ingestion_status(validation) == IngestionStatus.ACCEPTED_CLEAN