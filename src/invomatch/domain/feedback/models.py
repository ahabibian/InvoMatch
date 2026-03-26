from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from invomatch.domain.feedback.enums import (
    CorrectionType,
    PromotionStatus,
    ReasonCode,
    ReviewerAction,
    SignalType,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FeatureSnapshotRef(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    snapshot_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    match_id: str = Field(min_length=1)
    engine_version: str = Field(min_length=1)
    rule_version: str = Field(min_length=1)


class CorrectionEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    correction_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    match_id: str = Field(min_length=1)
    invoice_id: str = Field(min_length=1)

    correction_type: CorrectionType
    reviewer_action: ReviewerAction
    reason_code: ReasonCode

    reviewer_id: str = Field(min_length=1)
    reviewer_role: str = Field(min_length=1)

    occurred_at_utc: datetime = Field(default_factory=utc_now)

    original_decision: str = Field(min_length=1)
    original_confidence: float = Field(ge=0.0, le=1.0)
    corrected_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    previous_payment_id: str | None = None
    corrected_payment_id: str | None = None

    feature_snapshot_ref: FeatureSnapshotRef

    notes: str | None = None
    ui_version: str = Field(min_length=1)
    engine_version: str = Field(min_length=1)
    rule_version: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_replacement_requirements(self) -> "CorrectionEvent":
        if self.correction_type == CorrectionType.REPLACE_MATCH_TARGET:
            if not self.previous_payment_id or not self.corrected_payment_id:
                raise ValueError(
                    "replace_match_target requires both previous_payment_id and corrected_payment_id"
                )

        if self.correction_type == CorrectionType.ACCEPT_MATCH:
            if self.reviewer_action != ReviewerAction.ACCEPT:
                raise ValueError("accept_match must use reviewer action 'accept'")

        if self.correction_type == CorrectionType.REJECT_MATCH:
            if self.reviewer_action != ReviewerAction.REJECT:
                raise ValueError("reject_match must use reviewer action 'reject'")

        return self


class LearningSignal(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    signal_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    signal_type: SignalType

    source_correction_ids: tuple[str, ...] = Field(min_length=1)
    source_match_ids: tuple[str, ...] = Field(min_length=1)
    source_feature_snapshot_ids: tuple[str, ...] = Field(min_length=1)

    evidence_count: int = Field(ge=1)
    consistency_score: float = Field(ge=0.0, le=1.0)
    reviewer_weight_score: float = Field(ge=0.0, le=1.0)

    extracted_at_utc: datetime = Field(default_factory=utc_now)
    extraction_version: str = Field(min_length=1)

    candidate_rule_payload: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_evidence_alignment(self) -> "LearningSignal":
        if self.evidence_count < len(self.source_correction_ids):
            raise ValueError(
                "evidence_count cannot be smaller than the number of source correction ids"
            )
        return self


class CandidateRuleRecommendation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    recommendation_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    signal_id: str = Field(min_length=1)

    status: PromotionStatus = PromotionStatus.DRAFT
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)

    candidate_rule_payload: dict[str, Any] = Field(default_factory=dict)

    minimum_evidence_required: int = Field(ge=1)
    replay_test_passed: bool = False
    approver_id: str | None = None

    created_at_utc: datetime = Field(default_factory=utc_now)
    approved_at_utc: datetime | None = None

    @model_validator(mode="after")
    def validate_status_requirements(self) -> "CandidateRuleRecommendation":
        if self.status in {PromotionStatus.APPROVED, PromotionStatus.ACTIVE}:
            if not self.approver_id:
                raise ValueError("approved or active recommendation requires approver_id")
            if not self.replay_test_passed:
                raise ValueError("approved or active recommendation requires replay_test_passed=True")
        return self