from __future__ import annotations

from datetime import datetime, UTC
from typing import Optional
from uuid import uuid4

from invomatch.ingestion.models.ingestion_record import IngestionRecord
from invomatch.ingestion.models.ingestion_result import IngestionResult
from invomatch.ingestion.repositories.ingestion_repository import IngestionRepository


class InMemoryIngestionRepository(IngestionRepository):
    def __init__(self) -> None:
        self._records_by_idempotency_key: dict[str, IngestionRecord] = {}
        self._records_by_semantic_key: dict[str, IngestionRecord] = {}

    def save_result(self, result: IngestionResult) -> IngestionRecord:
        record = IngestionRecord(
            record_id=str(uuid4()),
            created_at=datetime.now(UTC),
            result=result,
        )
        self._records_by_idempotency_key[result.idempotency_key] = record
        semantic_key = getattr(result, "semantic_key", None)
        if semantic_key:
            self._records_by_semantic_key[semantic_key] = record
        return record

    def find_by_idempotency_key(self, idempotency_key: str) -> Optional[IngestionRecord]:
        return self._records_by_idempotency_key.get(idempotency_key)

    def find_latest_by_semantic_key(self, semantic_key: str) -> Optional[IngestionRecord]:
        return self._records_by_semantic_key.get(semantic_key)