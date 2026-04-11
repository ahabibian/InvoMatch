from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProductInputError(BaseModel):
    type: str
    code: str
    message: str
    field: str | None = None


class ProductInputSubmissionResponse(BaseModel):
    input_id: str
    status: str
    ingestion_batch_id: str | None = None
    run_id: str | None = None
    errors: list[ProductInputError] = Field(default_factory=list)


class ProductInputSessionView(BaseModel):
    input_id: str
    input_type: str
    status: str
    source_filename: str | None = None
    source_size_bytes: int | None = None
    ingestion_batch_id: str | None = None
    run_id: str | None = None
    errors: list[ProductInputError] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime