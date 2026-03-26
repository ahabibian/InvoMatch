from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from invomatch.domain.feedback.enums import PromotionStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CorrectionEventRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    correction_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    match_id: str = Field(min_length=1)
    invoice_id: str = Field(min_length=1)

    correction_type: str = Field(min_length=1)
    reviewer_action: str = Field(min_length=1)
    reason_code: str = Field(min_length=1)

    reviewer_id: str = Field(min_length=1)
    reviewer_role: str = Field(min_length=1)

    occurred_at_utc: datetime = Field(default_factory=utc_now)

    original_decision: str = Field(min_length=1)
    original_confidence: float = Field(ge=0.0, le=1.0)
    corrected_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    previous_payment_id: str | None = None
    corrected_payment_id: str | None = None

    feature_snapshot_id: str = Field(min_length=1)
    feature_snapshot_run_id: str = Field(min_length=1)
    feature_snapshot_match_id: str = Field(min_length=1)

    ui_version: str = Field(min_length=1)
    engine_version: str = Field(min_length=1)
    rule_version: str = Field(min_length=1)

    notes: str | None = None
    created_at_utc: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_record_invariants(self) -> "CorrectionEventRecord":
        if self.correction_type == "replace_match_target":
            if not self.previous_payment_id or not self.corrected_payment_id:
                raise ValueError(
                    "replace_match_target record requires previous_payment_id and corrected_payment_id"
                )
        return self


class LearningSignalRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    signal_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    signal_type: str = Field(min_length=1)

    source_correction_ids: tuple[str, ...] = Field(min_length=1)
    source_match_ids: tuple[str, ...] = Field(min_length=1)
    source_feature_snapshot_ids: tuple[str, ...] = Field(min_length=1)

    evidence_count: int = Field(ge=1)
    consistency_score: float = Field(ge=0.0, le=1.0)
    reviewer_weight_score: float = Field(ge=0.0, le=1.0)

    extraction_version: str = Field(min_length=1)
    candidate_rule_payload: dict[str, Any] = Field(default_factory=dict)

    extracted_at_utc: datetime = Field(default_factory=utc_now)
    created_at_utc: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def validate_evidence_count(self) -> "LearningSignalRecord":
        if self.evidence_count < len(self.source_correction_ids):
            raise ValueError(
                "evidence_count cannot be smaller than the number of source correction ids"
            )
        return self


class CandidateRuleRecommendationRecord(BaseModel):
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
    def validate_approval_state(self) -> "CandidateRuleRecommendationRecord":
        if self.status in {PromotionStatus.APPROVED, PromotionStatus.ACTIVE}:
            if not self.approver_id:
                raise ValueError("approved or active record requires approver_id")
            if not self.replay_test_passed:
                raise ValueError("approved or active record requires replay_test_passed=True")
        return self


class RulePromotionRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    promotion_id: str = Field(min_length=1)
    recommendation_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)

    promoted_rule_version: str = Field(min_length=1)
    approver_id: str = Field(min_length=1)

    promoted_at_utc: datetime = Field(default_factory=utc_now)
    created_at_utc: datetime = Field(default_factory=utc_now)


class RuleRollbackRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    rollback_id: str = Field(min_length=1)
    recommendation_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)

    rolled_back_rule_version: str = Field(min_length=1)
    approver_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)

    rolled_back_at_utc: datetime = Field(default_factory=utc_now)
    created_at_utc: datetime = Field(default_factory=utc_now)