from __future__ import annotations

from invomatch.domain.review.models import (
    DecisionType,
    FeedbackRecord,
    FeedbackStatus,
    ReviewItem,
    ReviewItemStatus,
)
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.handlers.base import BaseActionHandler
from invomatch.services.actions.result import ActionExecutionResult, ActionExecutionStatus
from invomatch.services.review_service import ReviewService


class ResolveReviewActionHandler(BaseActionHandler):
    def __init__(self, review_service: ReviewService | None = None) -> None:
        self._review_service = review_service or ReviewService()

    def handle(self, command: ActionCommand) -> ActionExecutionResult:
        payload = command.payload or {}

        decision_raw = payload.get("decision")
        reviewer_id = payload.get("reviewer_id")
        feedback_id = payload.get("feedback_id")
        review_session_id = payload.get("review_session_id")
        review_item_id = payload.get("review_item_id")
        source_type = payload.get("source_type", "manual_review")
        source_reference = payload.get("source_reference", command.target_id or "unknown")
        feedback_type = payload.get("feedback_type", "review_resolution")
        raw_payload = payload.get("raw_payload", {})
        submitted_by = payload.get("submitted_by", reviewer_id or "system")
        reason = payload.get("reason")
        reviewed_payload = payload.get("reviewed_payload")

        if not decision_raw:
            raise ValueError("payload.decision is required for resolve_review")
        if not reviewer_id:
            raise ValueError("payload.reviewer_id is required for resolve_review")
        if not feedback_id:
            raise ValueError("payload.feedback_id is required for resolve_review")
        if not review_session_id:
            raise ValueError("payload.review_session_id is required for resolve_review")
        if not review_item_id:
            raise ValueError("payload.review_item_id is required for resolve_review")

        decision = DecisionType(str(decision_raw))
        feedback_status = FeedbackStatus(payload.get("feedback_status", FeedbackStatus.UNDER_REVIEW.value))
        review_item_status = ReviewItemStatus(payload.get("review_item_status", ReviewItemStatus.IN_REVIEW.value))

        feedback = FeedbackRecord(
            feedback_id=feedback_id,
            run_id=command.run_id,
            source_type=source_type,
            source_reference=source_reference,
            feedback_type=feedback_type,
            raw_payload=raw_payload,
            submitted_by=submitted_by,
            feedback_status=feedback_status,
        )

        review_item = ReviewItem(
            review_item_id=review_item_id,
            review_session_id=review_session_id,
            feedback_id=feedback_id,
            item_status=review_item_status,
        )

        result = self._review_service.apply_decision(
            feedback=feedback,
            review_item=review_item,
            reviewer_id=reviewer_id,
            decision=decision,
            reason=reason,
            reviewed_payload=reviewed_payload,
        )

        eligibility_status = None
        if result.eligibility_record is not None:
            eligibility_status = result.eligibility_record.eligibility_status.value

        return ActionExecutionResult(
            action_type=command.action_type,
            target_type="review_item",
            target_id=review_item.review_item_id,
            status=ActionExecutionStatus.SUCCESS,
            state_changes=[
                {
                    "entity": "review_item",
                    "before": review_item_status.value,
                    "after": result.review_item.item_status.value,
                },
                {
                    "entity": "feedback",
                    "before": feedback_status.value,
                    "after": feedback.feedback_status.value,
                },
            ],
            side_effects=[
                {
                    "type": "review_decision_event",
                    "decision_event_id": result.decision_event.decision_event_id,
                    "decision": result.decision_event.decision_type.value,
                },
                {
                    "type": "audit_event",
                    "audit_event_id": result.audit_event.audit_event_id,
                    "action_type": result.audit_event.action_type,
                },
                {
                    "type": "learning_eligibility",
                    "eligibility_status": eligibility_status,
                },
            ],
            audit_event_ids=[result.audit_event.audit_event_id],
            response_payload={
                "review_item_id": result.review_item.review_item_id,
                "review_item_status": result.review_item.item_status.value,
                "feedback_status": feedback.feedback_status.value,
                "decision": result.decision_event.decision_type.value,
                "eligibility_status": eligibility_status,
            },
        )