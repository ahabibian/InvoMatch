from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from invomatch.ingestion.models.ingestion_record import IngestionRecord
from invomatch.ingestion.models.ingestion_result import IngestionResult


class IngestionRepository(ABC):
    @abstractmethod
    def save_result(self, result: IngestionResult) -> IngestionRecord:
        raise NotImplementedError

    @abstractmethod
    def find_by_idempotency_key(self, idempotency_key: str) -> Optional[IngestionRecord]:
        raise NotImplementedError

    @abstractmethod
    def find_latest_by_semantic_key(self, semantic_key: str) -> Optional[IngestionRecord]:
        raise NotImplementedError

    @abstractmethod
    def find_latest_by_identity_key(self, identity_key: str) -> Optional[IngestionRecord]:
        raise NotImplementedError