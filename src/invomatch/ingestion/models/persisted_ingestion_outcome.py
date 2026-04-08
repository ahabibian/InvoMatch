from __future__ import annotations

from pydantic import BaseModel

from invomatch.ingestion.models.duplicate_models import DuplicateCheckResult
from invomatch.ingestion.models.ingestion_record import IngestionRecord


class PersistedIngestionOutcome(BaseModel):
    record: IngestionRecord
    duplicate_check: DuplicateCheckResult