from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProductRunMatchSummary(BaseModel):
    total_items: int = Field(ge=0)
    matched_items: int = Field(ge=0)
    unmatched_items: int = Field(ge=0)
    ambiguous_items: int = Field(ge=0)


class ProductRunReviewSummary(BaseModel):
    status: str
    total_items: int = Field(ge=0)
    open_items: int = Field(ge=0)
    resolved_items: int = Field(ge=0)


class ProductRunExportSummary(BaseModel):
    status: str
    artifact_count: int = Field(ge=0)


class ProductRunArtifactReference(BaseModel):
    artifact_id: str
    kind: str
    file_name: str
    media_type: str
    size_bytes: int = Field(ge=0)
    created_at: datetime
    download_url: str


class ProductRunView(BaseModel):
    run_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    match_summary: ProductRunMatchSummary
    review_summary: ProductRunReviewSummary
    export_summary: ProductRunExportSummary
    artifacts: list[ProductRunArtifactReference] = Field(default_factory=list)