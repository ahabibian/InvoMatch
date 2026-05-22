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

class ProductMatchDetailEvidenceItem(BaseModel):
 """Backend-owned display-safe evidence item for Match Detail."""

 evidence_id: str = Field(
 ...,
 description="Backend-owned evidence identifier.",
 )
 evidence_type: str = Field(
 ...,
 description="Backend-owned evidence type.",
 )
 label: str = Field(
 ...,
 description="Human-readable backend-owned evidence label.",
 )
 value: str | None = Field(
 default=None,
 description="Display-safe backend-owned evidence value.",
 )
 source: str | None = Field(
 default=None,
 description="Backend-owned evidence source reference if available.",
 )


class ProductMatchDetailTraceability(BaseModel):
 """Backend-owned audit-safe traceability payload for Match Detail."""

 invoice_id: str | None = Field(
 default=None,
 description="Backend-owned invoice identifier linked to the match.",
 )
 payment_id: str | None = Field(
 default=None,
 description="Backend-owned payment identifier linked to the match.",
 )
 source_references: list[str] = Field(
 default_factory=list,
 description="Backend-owned source references used for audit-safe display.",
 )
 audit_identifiers: list[str] = Field(
 default_factory=list,
 description="Backend-owned audit-safe identifiers.",
 )


class ProductMatchDetailFailure(BaseModel):
 """Product-facing backend-owned failure semantics for Match Detail."""

 code: str = Field(
 ...,
 description="Stable backend-owned failure code.",
 )
 message: str = Field(
 ...,
 description="Display-safe backend-owned failure message.",
 )


class ProductMatchDetailResponse(BaseModel):
 """Product-facing Match Detail / Evidence response owned by the backend."""

 match_id: str = Field(
 ...,
 description="Stable backend-owned match identifier.",
 )
 match_status: str = Field(
 ...,
 description="Backend-owned match status or posture.",
 )
 invoice_summary: dict[str, object] = Field(
 default_factory=dict,
 description="Backend-owned invoice summary for display.",
 )
 payment_summary: dict[str, object] = Field(
 default_factory=dict,
 description="Backend-owned payment summary for display.",
 )
 evidence: list[ProductMatchDetailEvidenceItem] = Field(
 default_factory=list,
 description="Backend-owned evidence payload.",
 )
 traceability: ProductMatchDetailTraceability = Field(
 default_factory=ProductMatchDetailTraceability,
 description="Backend-owned traceability payload.",
 )
 explanation: list[ProductMatchExplanation] = Field(
 default_factory=list,
 description="Backend-owned explanation payload if available.",
 )
 confidence: float | None = Field(
 default=None,
 description="Backend-owned confidence value if available.",
 )
 failure: ProductMatchDetailFailure | None = Field(
 default=None,
 description="Backend-owned failure semantics when detail is not available.",
 )
