from __future__ import annotations

from datetime import datetime, UTC

from invomatch.ingestion.models.ingestion_result import IngestionResult
from invomatch.ingestion.models.normalized_models import NormalizedInvoice
from invomatch.ingestion.models.raw_models import RawInvoiceInput
from invomatch.ingestion.models.traceability_models import RawTraceReference
from invomatch.ingestion.normalizers import (
    normalize_amount,
    normalize_currency,
    normalize_date,
    normalize_external_id,
    normalize_invoice_number,
    normalize_optional_string,
)
from invomatch.ingestion.services.decision_builder import build_ingestion_status
from invomatch.ingestion.utils import (
    build_idempotency_key,
    build_invoice_semantic_key,
    fingerprint_payload,
)
from invomatch.ingestion.validators import validate_invoice_input


_SCHEMA_VERSION = "invoice_input/v1"
_RULE_VERSION = "ingestion_rules/v1"
_PAYLOAD_KIND = "invoice"


def ingest_invoice_input(raw: RawInvoiceInput) -> IngestionResult:
    validation = validate_invoice_input(raw)
    status = build_ingestion_status(validation)

    payload_fingerprint = fingerprint_payload(raw)
    idempotency_key = build_idempotency_key(_PAYLOAD_KIND, payload_fingerprint)

    normalized = None
    semantic_key = None

    if validation.is_valid:
        normalized = NormalizedInvoice(
            external_id=normalize_external_id(raw.external_id),
            invoice_number=normalize_invoice_number(raw.invoice_number),
            issue_date=normalize_date(raw.issue_date),
            due_date=normalize_date(raw.due_date),
            currency=normalize_currency(raw.currency),
            gross_amount=normalize_amount(raw.gross_amount),
            net_amount=normalize_amount(raw.net_amount),
            tax_amount=normalize_amount(raw.tax_amount),
            counterparty=normalize_optional_string(raw.counterparty),
        )
        semantic_key = build_invoice_semantic_key(normalized)

    return IngestionResult(
        status=status,
        validation=validation,
        normalized=normalized,
        raw_reference=RawTraceReference(
            payload_fingerprint=payload_fingerprint,
            payload_kind=_PAYLOAD_KIND,
            schema_version=_SCHEMA_VERSION,
            rule_version=_RULE_VERSION,
        ),
        processed_at=datetime.now(UTC),
        idempotency_key=idempotency_key,
        semantic_key=semantic_key,
        notes=None,
    )