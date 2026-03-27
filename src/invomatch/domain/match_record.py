from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


MatchRecordStatus = Literal["matched", "duplicate_detected", "partial_match", "unmatched"]


class MatchRecord(BaseModel):
    match_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    invoice_id: str = Field(min_length=1)

    status: MatchRecordStatus
    selected_payment_id: str | None = None
    candidate_payment_ids: list[str] = Field(default_factory=list)

    confidence_score: float = Field(ge=0.0, le=1.0)
    confidence_explanation: str = Field(min_length=1)
    mismatch_reasons: list[str] = Field(default_factory=list)

    created_at: datetime