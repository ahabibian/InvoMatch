from __future__ import annotations

from typing import Optional

from invomatch.ingestion.models.duplicate_models import (
    DuplicateCheckResult,
    DuplicateClassification,
)
from invomatch.ingestion.models.ingestion_result import IngestionResult
from invomatch.ingestion.models.normalized_models import NormalizedInvoice, NormalizedPayment
from invomatch.ingestion.utils import build_invoice_semantic_key, build_payment_semantic_key


def classify_invoice_duplicate(
    current: IngestionResult,
    existing: Optional[IngestionResult],
) -> DuplicateCheckResult:
    if existing is None:
        return DuplicateCheckResult(
            classification=DuplicateClassification.UNIQUE,
            reason="No existing ingestion result found.",
            semantic_key=_invoice_semantic_key_or_none(current),
            compared_against_idempotency_key=None,
        )

    if current.idempotency_key == existing.idempotency_key:
        return DuplicateCheckResult(
            classification=DuplicateClassification.EXACT_REPLAY,
            reason="Incoming invoice matches an existing raw payload fingerprint.",
            semantic_key=_invoice_semantic_key_or_none(current),
            compared_against_idempotency_key=existing.idempotency_key,
        )

    current_semantic = _invoice_semantic_key_or_none(current)
    existing_semantic = _invoice_semantic_key_or_none(existing)

    if current_semantic is not None and current_semantic == existing_semantic:
        return DuplicateCheckResult(
            classification=DuplicateClassification.SEMANTIC_DUPLICATE,
            reason="Incoming invoice matches an existing semantic business identity.",
            semantic_key=current_semantic,
            compared_against_idempotency_key=existing.idempotency_key,
        )

    if _invoice_conflicts(current, existing):
        return DuplicateCheckResult(
            classification=DuplicateClassification.CONFLICT,
            reason="Incoming invoice conflicts with an existing invoice identity.",
            semantic_key=current_semantic,
            compared_against_idempotency_key=existing.idempotency_key,
        )

    return DuplicateCheckResult(
        classification=DuplicateClassification.UNIQUE,
        reason="Incoming invoice is distinct from the existing result.",
        semantic_key=current_semantic,
        compared_against_idempotency_key=existing.idempotency_key,
    )


def classify_payment_duplicate(
    current: IngestionResult,
    existing: Optional[IngestionResult],
) -> DuplicateCheckResult:
    if existing is None:
        return DuplicateCheckResult(
            classification=DuplicateClassification.UNIQUE,
            reason="No existing ingestion result found.",
            semantic_key=_payment_semantic_key_or_none(current),
            compared_against_idempotency_key=None,
        )

    if current.idempotency_key == existing.idempotency_key:
        return DuplicateCheckResult(
            classification=DuplicateClassification.EXACT_REPLAY,
            reason="Incoming payment matches an existing raw payload fingerprint.",
            semantic_key=_payment_semantic_key_or_none(current),
            compared_against_idempotency_key=existing.idempotency_key,
        )

    current_semantic = _payment_semantic_key_or_none(current)
    existing_semantic = _payment_semantic_key_or_none(existing)

    if current_semantic is not None and current_semantic == existing_semantic:
        return DuplicateCheckResult(
            classification=DuplicateClassification.SEMANTIC_DUPLICATE,
            reason="Incoming payment matches an existing semantic business identity.",
            semantic_key=current_semantic,
            compared_against_idempotency_key=existing.idempotency_key,
        )

    if _payment_conflicts(current, existing):
        return DuplicateCheckResult(
            classification=DuplicateClassification.CONFLICT,
            reason="Incoming payment conflicts with an existing payment identity.",
            semantic_key=current_semantic,
            compared_against_idempotency_key=existing.idempotency_key,
        )

    return DuplicateCheckResult(
        classification=DuplicateClassification.UNIQUE,
        reason="Incoming payment is distinct from the existing result.",
        semantic_key=current_semantic,
        compared_against_idempotency_key=existing.idempotency_key,
    )


def _invoice_semantic_key_or_none(result: IngestionResult) -> Optional[str]:
    if not isinstance(result.normalized, NormalizedInvoice):
        return None
    return build_invoice_semantic_key(result.normalized)


def _payment_semantic_key_or_none(result: IngestionResult) -> Optional[str]:
    if not isinstance(result.normalized, NormalizedPayment):
        return None
    return build_payment_semantic_key(result.normalized)


def _invoice_conflicts(current: IngestionResult, existing: IngestionResult) -> bool:
    if not isinstance(current.normalized, NormalizedInvoice):
        return False
    if not isinstance(existing.normalized, NormalizedInvoice):
        return False

    same_identity = (
        current.normalized.invoice_number == existing.normalized.invoice_number
        and current.normalized.issue_date == existing.normalized.issue_date
        and current.normalized.currency == existing.normalized.currency
    )
    different_amount = current.normalized.gross_amount != existing.normalized.gross_amount

    return same_identity and different_amount


def _payment_conflicts(current: IngestionResult, existing: IngestionResult) -> bool:
    if not isinstance(current.normalized, NormalizedPayment):
        return False
    if not isinstance(existing.normalized, NormalizedPayment):
        return False

    same_identity = (
        current.normalized.payment_reference == existing.normalized.payment_reference
        and current.normalized.payment_date == existing.normalized.payment_date
        and current.normalized.currency == existing.normalized.currency
    )
    different_amount = current.normalized.amount != existing.normalized.amount

    return same_identity and different_amount