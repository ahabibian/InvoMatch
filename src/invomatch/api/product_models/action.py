from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_type: Literal[
        "confirm_match",
        "reject_match",
        "mark_unmatched",
        "resolve_review",
        "export_run",
    ] = Field(..., description="Product-facing action type.")
    target_id: Optional[str] = Field(
        default=None,
        description="Product-facing target identifier for the action.",
    )
    note: Optional[str] = Field(
        default=None,
        description="Optional user-provided note for audit visibility.",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured product-facing action payload.",
    )


class ProductActionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(..., description="Associated product-facing run identifier.")
    action_type: str = Field(..., description="Accepted product-facing action type.")
    accepted: bool = Field(..., description="Whether the action was accepted.")
    status: str = Field(..., description="Product-facing result status after action handling.")
    message: Optional[str] = Field(
        default=None,
        description="Optional product-facing acknowledgement message.",
    )