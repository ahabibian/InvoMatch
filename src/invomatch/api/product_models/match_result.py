from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductMatchExplanation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., description="Stable explanation code for product-facing reasoning.")
    message: str = Field(..., description="Human-readable explanation text.")
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional normalized confidence for this explanation item.",
    )


class ProductMatchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    match_id: str = Field(..., description="Stable product-facing match identifier.")
    invoice_id: str = Field(..., description="Product-facing invoice identifier.")
    payment_id: Optional[str] = Field(
        default=None,
        description="Product-facing payment identifier if a payment is linked.",
    )
    status: Literal["matched", "partial_match", "duplicate_detected", "unmatched"] = Field(
        ...,
        description="Product-facing match status.",
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional normalized confidence for the overall match result.",
    )
    explanation: list[ProductMatchExplanation] = Field(
        default_factory=list,
        description="Product-facing explanation fragments.",
    )