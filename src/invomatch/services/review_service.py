from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from invomatch.domain.review.models import (
    AuditEvent,
    DecisionType,
    EligibilityStatus,
    FeedbackRecord,
    LearningEligibilityRecord,
    ReviewDecisionEvent,
    ReviewItem,
    ReviewSession,
)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


@dataclass(slots=True)
class ReviewDecisionResult:
    review_item: ReviewItem
    decision_event: ReviewDecisionEvent
    audit_event: AuditEvent
    eligibility_record: Optional[LearningEligibilityRecord]


class ReviewService:
    """
    Application service for review-domain operations.

    Current scope:
    - create review sessions
    - create review items from feedback
    - apply reviewer decisions
    - derive learning eligibility
    - emit audit events

    This version is intentionally in-memory/domain-oriented.
    Persistence is a later step.
    """

    def create_review_session(
        self,
        *,
        created_by: str,
        assigned_reviewer_id: Optional[str] = None,
        session_notes: Optional[str] = None,
    ) -> ReviewSession:
        session = ReviewSession(
            review_session_id=new_id("review_session"),
            created_by=created_by,
            session_notes=session_notes,
        )

        if assigned_reviewer_id:
            session.assign(assigned_reviewer_id)

        return session

    def create_review_item(
        self,
        *,
        feedback: FeedbackRecord,
        review_session: ReviewSession,
    ) -> tuple[ReviewItem, AuditEvent]:
        feedback.mark_queued_for_review()

        review_item = ReviewItem(
            review_item_id=new_id("review_item"),
            review_session_id=review_session.review_session_id,
            feedback_id=feedback.feedback_id,
        )

        audit_event = AuditEvent(
            audit_event_id=new_id("audit"),
            entity_type="review_item",
            entity_id=review_item.review_item_id,
            action_type="REVIEW_ITEM_CREATED",
            actor_id="review_service",
            context_reference=feedback.source_reference,
            event_payload={
                "feedback_id": feedback.feedback_id,
                "review_session_id": review_session.review_session_id,
                "run_id": feedback.run_id,
            },
        )

        return review_item, audit_event

    def start_review(
        self,
        *,
        feedback: FeedbackRecord,
        review_item: ReviewItem,
        reviewer_id: str,
    ) -> AuditEvent:
        feedback.mark_under_review()
        review_item.start_review()

        return AuditEvent(
            audit_event_id=new_id("audit"),
            entity_type="review_item",
            entity_id=review_item.review_item_id,
            action_type="REVIEW_STARTED",
            actor_id=reviewer_id,
            context_reference=feedback.source_reference,
            event_payload={
                "feedback_id": feedback.feedback_id,
                "review_item_status": review_item.item_status.value,
            },
        )

    def apply_decision(
        self,
        *,
        feedback: FeedbackRecord,
        review_item: ReviewItem,
        reviewer_id: str,
        decision: DecisionType,
        reason: Optional[str] = None,
        reviewed_payload: Optional[dict] = None,
    ) -> ReviewDecisionResult:
        previous_state = review_item.item_status.value

        review_item.apply_decision(
            decision=decision,
            reviewer_id=reviewer_id,
            reason=reason,
            reviewed_payload=reviewed_payload,
        )

        decision_event = ReviewDecisionEvent(
            decision_event_id=new_id("decision"),
            review_item_id=review_item.review_item_id,
            decision_type=decision,
            actor_id=reviewer_id,
            previous_state=previous_state,
            new_state=review_item.item_status.value,
            decision_reason=reason,
            decision_payload=reviewed_payload,
        )

        audit_event = AuditEvent(
            audit_event_id=new_id("audit"),
            entity_type="review_item",
            entity_id=review_item.review_item_id,
            action_type=f"REVIEW_DECISION_{decision.value}",
            actor_id=reviewer_id,
            context_reference=feedback.source_reference,
            event_payload={
                "feedback_id": feedback.feedback_id,
                "decision": decision.value,
                "previous_state": previous_state,
                "new_state": review_item.item_status.value,
            },
        )

        eligibility_record = self.derive_learning_eligibility(
            feedback=feedback,
            review_item=review_item,
            reason=reason,
        )

        if decision in (DecisionType.APPROVE, DecisionType.REJECT, DecisionType.MODIFY):
            feedback.mark_reviewed()
        elif decision == DecisionType.DEFER:
            feedback.mark_under_review()
        elif decision == DecisionType.REOPEN:
            feedback.mark_under_review()

        return ReviewDecisionResult(
            review_item=review_item,
            decision_event=decision_event,
            audit_event=audit_event,
            eligibility_record=eligibility_record,
        )

    def derive_learning_eligibility(
        self,
        *,
        feedback: FeedbackRecord,
        review_item: ReviewItem,
        reason: Optional[str] = None,
    ) -> Optional[LearningEligibilityRecord]:
        if review_item.current_decision is None:
            return None

        if review_item.current_decision == DecisionType.APPROVE:
            return LearningEligibilityRecord(
                eligibility_id=new_id("eligibility"),
                review_item_id=review_item.review_item_id,
                feedback_id=feedback.feedback_id,
                eligibility_status=EligibilityStatus.ELIGIBLE,
                eligibility_reason=reason or "Approved by reviewer",
                derived_payload=feedback.raw_payload,
            )

        if review_item.current_decision == DecisionType.MODIFY:
            return LearningEligibilityRecord(
                eligibility_id=new_id("eligibility"),
                review_item_id=review_item.review_item_id,
                feedback_id=feedback.feedback_id,
                eligibility_status=EligibilityStatus.ELIGIBLE,
                eligibility_reason=reason or "Modified and approved by reviewer",
                derived_payload=review_item.reviewed_payload,
            )

        if review_item.current_decision == DecisionType.REJECT:
            return LearningEligibilityRecord(
                eligibility_id=new_id("eligibility"),
                review_item_id=review_item.review_item_id,
                feedback_id=feedback.feedback_id,
                eligibility_status=EligibilityStatus.INELIGIBLE,
                eligibility_reason=reason or "Rejected by reviewer",
                derived_payload=None,
            )

        if review_item.current_decision == DecisionType.DEFER:
            return LearningEligibilityRecord(
                eligibility_id=new_id("eligibility"),
                review_item_id=review_item.review_item_id,
                feedback_id=feedback.feedback_id,
                eligibility_status=EligibilityStatus.PENDING,
                eligibility_reason=reason or "Deferred for later review",
                derived_payload=None,
            )

        if review_item.current_decision == DecisionType.REOPEN:
            return LearningEligibilityRecord(
                eligibility_id=new_id("eligibility"),
                review_item_id=review_item.review_item_id,
                feedback_id=feedback.feedback_id,
                eligibility_status=EligibilityStatus.PENDING,
                eligibility_reason=reason or "Reopened for re-review",
                derived_payload=None,
            )

        return None