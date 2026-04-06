from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel

from invomatch.ingestion.models.ingestion_result import IngestionResult


class IngestionRecord(BaseModel):
    record_id: str
    created_at: datetime
    result: IngestionResult