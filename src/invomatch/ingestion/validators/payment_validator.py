from __future__ import annotations

from invomatch.ingestion.models.raw_models import RawPaymentInput
from invomatch.ingestion.models.validation_models import (
    ValidationError,
    ValidationResult,
    ValidationWarning,
)
from invomatch.ingestion.normalizers import (
    normalize_amount,
    normalize_currency,
    normalize_date,
    normalize_optional_string,
    normalize_payment_reference,
)


def validate_payment_input(raw: RawPaymentInput) -> ValidationResult:
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    payment_reference = normalize_payment_reference(raw.payment_reference)
    payment_date = normalize_date(raw.payment_date)
    amount = normalize_amount(raw.amount)
    currency = normalize_currency(raw.currency)
    counterparty = normalize_optional_string(raw.counterparty)

    if payment_reference is None:
        errors.append(
            ValidationError(
                field="payment_reference",
                code="required_or_invalid",
                message="Payment reference is required and must be valid.",
            )
        )

    if payment_date is None:
        errors.append(
            ValidationError(
                field="payment_date",
                code="required_or_invalid",
                message="Payment date is required and must be valid.",
            )
        )

    if amount is None:
        errors.append(
            ValidationError(
                field="amount",
                code="required_or_invalid",
                message="Amount is required and must be valid.",
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