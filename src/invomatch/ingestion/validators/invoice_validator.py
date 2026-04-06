from __future__ import annotations

from invomatch.ingestion.models.raw_models import RawInvoiceInput
from invomatch.ingestion.models.validation_models import (
    ValidationError,
    ValidationResult,
    ValidationWarning,
)
from invomatch.ingestion.normalizers import (
    normalize_amount,
    normalize_currency,
    normalize_date,
    normalize_invoice_number,
    normalize_optional_string,
)


def validate_invoice_input(raw: RawInvoiceInput) -> ValidationResult:
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    invoice_number = normalize_invoice_number(raw.invoice_number)
    issue_date = normalize_date(raw.issue_date)
    due_date = normalize_date(raw.due_date)
    currency = normalize_currency(raw.currency)
    gross_amount = normalize_amount(raw.gross_amount)
    counterparty = normalize_optional_string(raw.counterparty)

    if invoice_number is None:
        errors.append(
            ValidationError(
                field="invoice_number",
                code="required_or_invalid",
                message="Invoice number is required and must be valid.",
            )
        )

    if issue_date is None:
        errors.append(
            ValidationError(
                field="issue_date",
                code="required_or_invalid",
                message="Issue date is required and must be valid.",
            )
        )

    if currency is None:
        errors.append(
            ValidationError(
                field="currency",
                code="required_or_invalid",
                message="Currency is required and must be a supported canonical code.",
            )
        )

    if gross_amount is None:
        errors.append(
            ValidationError(
                field="gross_amount",
                code="required_or_invalid",
                message="Gross amount is required and must be valid.",
            )
        )

    if raw.due_date is not None and due_date is None:
        errors.append(
            ValidationError(
                field="due_date",
                code="invalid",
                message="Due date is invalid.",
            )
        )

    if raw.due_date is None:
        warnings.append(
            ValidationWarning(
                field="due_date",
                code="missing_optional",
                message="Due date is missing.",
            )
        )

    if counterparty is None:
        warnings.append(
            ValidationWarning(
                field="counterparty",
                code="missing_optional",
                message="Counterparty is missing.",
            )
        )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )