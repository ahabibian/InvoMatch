from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class FeedbackStatus(str, Enum):
    CAPTURED = "CAPTURED"
    QUEUED_FOR_REVIEW = "QUEUED_FOR_REVIEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    REVIEWED = "REVIEWED"
    CLOSED = "CLOSED"


class ReviewSessionStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ReviewItemStatus(str, Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"
    DEFERRED = "DEFERRED"
    CLOSED = "CLOSED"


class DecisionType(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    MODIFY = "MODIFY"
    DEFER = "DEFER"
    REOPEN = "REOPEN"


class EligibilityStatus(str, Enum):
    PENDING = "PENDING"
    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"
    INVALIDATED = "INVALIDATED"


@dataclass(slots=True)
class FeedbackRecord:
    feedback_id: str
    run_id: str
    source_type: str
    source_reference: str
    feedback_type: str
    raw_payload: dict[str, Any]
    submitted_by: str
    submitted_at: datetime = field(default_factory=utc_now)
    feedback_status: FeedbackStatus = FeedbackStatus.CAPTURED

    def mark_queued_for_review(self) -> None:
        self.feedback_status = FeedbackStatus.QUEUED_FOR_REVIEW

    def mark_under_review(self) -> None:
        self.feedback_status = FeedbackStatus.UNDER_REVIEW

    def mark_reviewed(self) -> None:
        self.feedback_status = FeedbackStatus.REVIEWED

    def close(self) -> None:
        self.feedback_status = FeedbackStatus.CLOSED


@dataclass(slots=True)
class ReviewSession:
    review_session_id: str
    created_by: str
    created_at: datetime = field(default_factory=utc_now)
    session_status: ReviewSessionStatus = ReviewSessionStatus.OPEN
    assigned_reviewer_id: Optional[str] = None
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    session_notes: Optional[str] = None

    def assign(self, reviewer_id: str) -> None:
        self.assigned_reviewer_id = reviewer_id
        self.assigned_at = utc_now()
        if self.session_status == ReviewSessionStatus.OPEN:
            self.session_status = ReviewSessionStatus.IN_PROGRESS

    def mark_partially_resolved(self) -> None:
        self.session_status = ReviewSessionStatus.PARTIALLY_RESOLVED

    def complete(self) -> None:
        self.session_status = ReviewSessionStatus.COMPLETED
        self.completed_at = utc_now()

    def cancel(self) -> None:
        self.session_status = ReviewSessionStatus.CANCELLED
        self.completed_at = utc_now()


@dataclass(slots=True)
class ReviewItem:
    review_item_id: str
    review_session_id: str
    feedback_id: str
    item_status: ReviewItemStatus = ReviewItemStatus.PENDING
    current_decision: Optional[DecisionType] = None
    decision_reason: Optional[str] = None
    reviewed_payload: Optional[dict[str, Any]] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    requires_followup: bool = False
    learning_eligible: bool = False

    def start_review(self) -> None:
        self.item_status = ReviewItemStatus.IN_REVIEW

    def apply_decision(
        self,
        decision: DecisionType,
        reviewer_id: str,
        reason: Optional[str] = None,
        reviewed_payload: Optional[dict[str, Any]] = None,
    ) -> None:
        self.current_decision = decision
        self.decision_reason = reason
        self.reviewed_by = reviewer_id
        self.reviewed_at = utc_now()

        if decision == DecisionType.APPROVE:
            self.item_status = ReviewItemStatus.APPROVED
            self.learning_eligible = True
            self.requires_followup = False
            self.reviewed_payload = None

        elif decision == DecisionType.REJECT:
            self.item_status = ReviewItemStatus.REJECTED
            self.learning_eligible = False
            self.requires_followup = False
            self.reviewed_payload = None

        elif decision == DecisionType.MODIFY:
            if reviewed_payload is None:
                raise ValueError("reviewed_payload is required for MODIFY decisions")
            self.item_status = ReviewItemStatus.MODIFIED
            self.learning_eligible = True
            self.requires_followup = False
            self.reviewed_payload = reviewed_payload

        elif decision == DecisionType.DEFER:
            self.item_status = ReviewItemStatus.DEFERRED
            self.learning_eligible = False
            self.requires_followup = True

        elif decision == DecisionType.REOPEN:
            self.item_status = ReviewItemStatus.IN_REVIEW
            self.learning_eligible = False
            self.requires_followup = True

        else:
            raise ValueError(f"Unsupported decision type: {decision}")

    def close(self) -> None:
        self.item_status = ReviewItemStatus.CLOSED


@dataclass(slots=True)
class ReviewDecisionEvent:
    decision_event_id: str
    review_item_id: str
    decision_type: DecisionType
    actor_id: str
    previous_state: str
    new_state: str
    created_at: datetime = field(default_factory=utc_now)
    decision_reason: Optional[str] = None
    decision_payload: Optional[dict[str, Any]] = None


@dataclass(slots=True)
class AuditEvent:
    audit_event_id: str
    entity_type: str
    entity_id: str
    action_type: str
    actor_id: str
    occurred_at: datetime = field(default_factory=utc_now)
    context_reference: Optional[str] = None
    event_payload: Optional[dict[str, Any]] = None


@dataclass(slots=True)
class LearningEligibilityRecord:
    eligibility_id: str
    review_item_id: str
    feedback_id: str
    eligibility_status: EligibilityStatus
    eligibility_reason: Optional[str] = None
    derived_payload: Optional[dict[str, Any]] = None
    created_at: datetime = field(default_factory=utc_now)
    created_by_system: str = "review_service"
    invalidated_at: Optional[datetime] = None

    def invalidate(self) -> None:
        self.eligibility_status = EligibilityStatus.INVALIDATED
        self.invalidated_at = utc_now()