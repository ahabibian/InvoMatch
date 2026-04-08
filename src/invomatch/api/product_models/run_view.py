from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductRunError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., description="Stable product-safe error code.")
    message: str = Field(..., description="Product-safe error message.")
    retryable: bool = Field(..., description="Whether retry is allowed by runtime policy.")
    terminal: bool = Field(..., description="Whether the failure is terminal.")


class ProductRunMatchSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_items: int = Field(..., ge=0)
    matched_items: int = Field(..., ge=0)
    unmatched_items: int = Field(..., ge=0)
    ambiguous_items: int = Field(..., ge=0)


class ProductRunReviewSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Product-facing review summary status.")
    total_items: int = Field(..., ge=0)
    open_items: int = Field(..., ge=0)
    resolved_items: int = Field(..., ge=0)


class ProductRunExportSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Product-facing export summary status.")
    artifact_count: int = Field(..., ge=0)


class ProductRunArtifactReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: str = Field(..., description="Stable product-facing artifact identifier.")
    kind: str = Field(..., description="Product-facing artifact kind.")
    file_name: str = Field(..., description="Artifact file name.")
    media_type: str = Field(..., description="Artifact media type.")
    size_bytes: int = Field(..., ge=0, description="Artifact size in bytes.")
    created_at: datetime = Field(..., description="Artifact creation timestamp.")
    download_url: Optional[str] = Field(
        default=None,
        description="Download URL when artifact is ready and downloadable.",
    )


class ProductRunView(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(..., description="Stable product-facing run identifier.")
    status: str = Field(..., description="Product-facing run status.")
    created_at: datetime = Field(..., description="Run creation timestamp.")
    updated_at: datetime = Field(..., description="Last product-visible update timestamp.")
    error: Optional[ProductRunError] = Field(
        default=None,
        description="Structured product-safe runtime failure information when present.",
    )
    match_summary: ProductRunMatchSummary
    review_summary: ProductRunReviewSummary
    export_summary: ProductRunExportSummary
    artifacts: list[ProductRunArtifactReference] = Field(default_factory=list)