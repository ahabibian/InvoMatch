from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping


class DecisionType(StrEnum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"
    UNMATCHED = "unmatched"
    AMBIGUOUS = "ambiguous"
    REVIEW_REQUIRED = "review_required"


class DecisionStatus(StrEnum):
    PROPOSED = "proposed"
    AUTO_APPROVED = "auto_approved"
    USER_CONFIRMED = "user_confirmed"
    USER_CORRECTED = "user_corrected"
    REJECTED = "rejected"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class MatchExplanation:
    summary: str
    reasons: tuple[str, ...] = ()
    penalties: tuple[str, ...] = ()
    key_facts: Mapping[str, object] = field(default_factory=dict)
    competing_candidate_count: int = 0
    top_score_gap: float | None = None

    def __post_init__(self) -> None:
        if not self.summary.strip():
            raise ValueError("MatchExplanation.summary must not be empty.")
        if self.competing_candidate_count < 0:
            raise ValueError("competing_candidate_count must be >= 0.")
        if self.top_score_gap is not None and self.top_score_gap < 0:
            raise ValueError("top_score_gap must be >= 0 when provided.")


@dataclass(frozen=True, slots=True)
class DecisionProvenance:
    match_engine_version: str
    rule_set_version: str
    confidence_policy_version: str
    taxonomy_version: str
    feature_schema_version: str

    def __post_init__(self) -> None:
        for field_name in (
            "match_engine_version",
            "rule_set_version",
            "confidence_policy_version",
            "taxonomy_version",
            "feature_schema_version",
        ):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty.")


@dataclass(frozen=True, slots=True)
class MatchDecision:
    decision_id: str
    run_id: str
    invoice_ids: tuple[str, ...]
    payment_ids: tuple[str, ...]
    decision_type: DecisionType
    status: DecisionStatus
    score: float
    confidence: ConfidenceLevel
    explanation: MatchExplanation
    primary_mismatch_code: str | None = None
    secondary_mismatch_codes: tuple[str, ...] = ()
    auto_action_eligible: bool = False
    provenance: DecisionProvenance | None = None

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("decision_id must not be empty.")
        if not self.run_id.strip():
            raise ValueError("run_id must not be empty.")

        if not self.invoice_ids and not self.payment_ids:
            raise ValueError("At least one invoice_id or payment_id must be present.")

        if any(not item.strip() for item in self.invoice_ids):
            raise ValueError("invoice_ids must not contain empty values.")

        if any(not item.strip() for item in self.payment_ids):
            raise ValueError("payment_ids must not contain empty values.")

        if self.score < 0:
            raise ValueError("score must be >= 0.")

        if self.decision_type == DecisionType.ONE_TO_ONE:
            if len(self.invoice_ids) != 1 or len(self.payment_ids) != 1:
                raise ValueError("ONE_TO_ONE requires exactly 1 invoice_id and 1 payment_id.")

        if self.decision_type == DecisionType.ONE_TO_MANY:
            if len(self.invoice_ids) != 1 or len(self.payment_ids) < 2:
                raise ValueError("ONE_TO_MANY requires 1 invoice_id and at least 2 payment_ids.")

        if self.decision_type == DecisionType.MANY_TO_ONE:
            if len(self.invoice_ids) < 2 or len(self.payment_ids) != 1:
                raise ValueError("MANY_TO_ONE requires at least 2 invoice_ids and exactly 1 payment_id.")

        if self.decision_type == DecisionType.MANY_TO_MANY:
            if len(self.invoice_ids) < 2 or len(self.payment_ids) < 2:
                raise ValueError("MANY_TO_MANY requires at least 2 invoice_ids and 2 payment_ids.")

        if self.decision_type == DecisionType.UNMATCHED:
            if not (self.invoice_ids or self.payment_ids):
                raise ValueError("UNMATCHED requires at least one side to exist.")

        if self.decision_type in (DecisionType.AMBIGUOUS, DecisionType.REVIEW_REQUIRED):
            if self.confidence == ConfidenceLevel.HIGH:
                raise ValueError(
                    f"{self.decision_type.value} cannot use confidence=high."
                )

        if self.confidence == ConfidenceLevel.REJECTED and self.status not in (
            DecisionStatus.REJECTED,
            DecisionStatus.PROPOSED,
        ):
            raise ValueError(
                "confidence=rejected is only valid with status=rejected or proposed."
            )

        if self.auto_action_eligible:
            if self.confidence != ConfidenceLevel.HIGH:
                raise ValueError("auto_action_eligible requires confidence=high.")
            if self.decision_type in (
                DecisionType.UNMATCHED,
                DecisionType.AMBIGUOUS,
                DecisionType.REVIEW_REQUIRED,
            ):
                raise ValueError(
                    "auto_action_eligible cannot be true for unmatched, ambiguous, or review_required decisions."
                )

        if self.primary_mismatch_code:
            if self.decision_type not in (
                DecisionType.UNMATCHED,
                DecisionType.AMBIGUOUS,
                DecisionType.REVIEW_REQUIRED,
            ):
                raise ValueError(
                    "primary_mismatch_code is only valid for unmatched, ambiguous, or review_required decisions."
                )

        if self.secondary_mismatch_codes and not self.primary_mismatch_code:
            raise ValueError(
                "secondary_mismatch_codes require primary_mismatch_code to be present."
            )