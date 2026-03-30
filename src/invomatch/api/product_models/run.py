from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .match_result import ProductMatchResult


class ProductRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(..., description="Stable product-facing run identifier.")
    status: str = Field(..., description="Product-facing run status.")
    created_at: datetime = Field(..., description="Run creation timestamp.")
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last product-visible update timestamp.",
    )
    invoice_count: int = Field(..., ge=0, description="Number of invoices in the run.")
    payment_count: int = Field(..., ge=0, description="Number of payments in the run.")
    match_count: int = Field(..., ge=0, description="Number of produced match results.")
    review_required_count: int = Field(
        default=0,
        ge=0,
        description="Number of cases currently requiring review.",
    )


class ProductRunDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(..., description="Stable product-facing run identifier.")
    status: str = Field(..., description="Product-facing run status.")
    created_at: datetime = Field(..., description="Run creation timestamp.")
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last product-visible update timestamp.",
    )
    invoice_count: int = Field(..., ge=0, description="Number of invoices in the run.")
    payment_count: int = Field(..., ge=0, description="Number of payments in the run.")
    match_count: int = Field(..., ge=0, description="Number of produced match results.")
    review_required_count: int = Field(
        default=0,
        ge=0,
        description="Number of cases currently requiring review.",
    )
    matches: list[ProductMatchResult] = Field(
        default_factory=list,
        description="Product-facing match results for the run.",
    )