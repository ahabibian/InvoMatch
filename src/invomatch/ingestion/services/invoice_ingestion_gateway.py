from __future__ import annotations

from invomatch.ingestion.models.persisted_ingestion_outcome import PersistedIngestionOutcome
from invomatch.ingestion.models.raw_models import RawInvoiceInput
from invomatch.ingestion.repositories.ingestion_repository import IngestionRepository
from invomatch.ingestion.services.duplicate_classifier import classify_invoice_duplicate
from invomatch.ingestion.services.invoice_ingestion_service import ingest_invoice_input


class InvoiceIngestionGateway:
    def __init__(self, repository: IngestionRepository) -> None:
        self._repository = repository

    def ingest(self, raw: RawInvoiceInput) -> PersistedIngestionOutcome:
        result = ingest_invoice_input(raw)

        existing = self._repository.find_by_idempotency_key(result.idempotency_key)
        if existing is None and result.semantic_key is not None:
            existing = self._repository.find_latest_by_semantic_key(result.semantic_key)
        if existing is None and result.identity_key is not None:
            existing = self._repository.find_latest_by_identity_key(result.identity_key)

        existing_result = existing.result if existing is not None else None
        duplicate_check = classify_invoice_duplicate(
            current=result,
            existing=existing_result,
        )

        record = self._repository.save_result(result)

        return PersistedIngestionOutcome(
            record=record,
            duplicate_check=duplicate_check,
        )