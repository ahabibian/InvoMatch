from __future__ import annotations

from datetime import datetime, UTC

from invomatch.ingestion.models.ingestion_result import IngestionResult
from invomatch.ingestion.models.normalized_models import NormalizedPayment
from invomatch.ingestion.models.raw_models import RawPaymentInput
from invomatch.ingestion.normalizers import (
    normalize_amount,
    normalize_currency,
    normalize_date,
    normalize_external_id,
    normalize_optional_string,
    normalize_payment_reference,
)
from invomatch.ingestion.services.decision_builder import build_ingestion_status
from invomatch.ingestion.validators import validate_payment_input


def ingest_payment_input(raw: RawPaymentInput) -> IngestionResult:
    validation = validate_payment_input(raw)
    status = build_ingestion_status(validation)

    normalized = None
    if validation.is_valid:
        normalized = NormalizedPayment(
            external_id=normalize_external_id(raw.external_id),
            payment_reference=normalize_payment_reference(raw.payment_reference),
            payment_date=normalize_date(raw.payment_date),
            amount=normalize_amount(raw.amount),
            currency=normalize_currency(raw.currency),
            counterparty=normalize_optional_string(raw.counterparty),
        )

    return IngestionResult(
        status=status,
        validation=validation,
        normalized=normalized,
        raw_reference=None,
        processed_at=datetime.now(UTC),
        idempotency_key=None,
        notes=None,
    )