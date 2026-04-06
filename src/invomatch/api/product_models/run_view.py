from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ReviewSummaryStatus = Literal["not_started", "in_review", "completed"]
ExportSummaryStatus = Literal["not_ready", "ready", "exported", "failed"]


class ProductRunMatchSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_items: int = Field(ge=0)
    matched_items: int = Field(ge=0)
    unmatched_items: int = Field(ge=0)
    ambiguous_items: int = Field(ge=0)


class ProductRunReviewSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ReviewSummaryStatus
    total_items: int = Field(ge=0)
    open_items: int = Field(ge=0)
    resolved_items: int = Field(ge=0)


class ProductRunExportSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ExportSummaryStatus
    artifact_count: int = Field(ge=0)


class ProductRunArtifactReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str
    kind: str
    file_name: str
    media_type: str
    size_bytes: int = Field(ge=0)
    created_at: datetime
    download_url: str | None = None


class ProductRunView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    match_summary: ProductRunMatchSummary
    review_summary: ProductRunReviewSummary
    export_summary: ProductRunExportSummary
    artifacts: list[ProductRunArtifactReference] = Field(default_factory=list)