from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .match_result import ProductMatchExplanation


class ProductReviewQueueItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(..., description="Stable product-facing review case identifier.")
    run_id: str = Field(..., description="Associated product-facing run identifier.")
    status: Literal["open", "resolved", "dismissed"] = Field(
        ...,
        description="Product-facing review case status.",
    )
    reason_code: str = Field(..., description="Reason why this case entered review.")
    priority: Optional[str] = Field(
        default=None,
        description="Optional product-facing priority label.",
    )


class ProductReviewCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(..., description="Stable product-facing review case identifier.")
    run_id: str = Field(..., description="Associated product-facing run identifier.")
    status: Literal["open", "resolved", "dismissed"] = Field(
        ...,
        description="Product-facing review case status.",
    )
    reason_code: str = Field(..., description="Reason why this case entered review.")
    match_id: Optional[str] = Field(
        default=None,
        description="Associated product-facing match identifier if present.",
    )
    explanation: list[ProductMatchExplanation] = Field(
        default_factory=list,
        description="Product-facing explanation for why review is needed.",
    )
    recommended_action: Optional[str] = Field(
        default=None,
        description="Optional suggested product-facing user action.",
    )