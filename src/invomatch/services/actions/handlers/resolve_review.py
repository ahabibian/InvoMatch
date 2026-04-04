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
from invomatch.services.orchestration.review_resolution_coordinator import (
    ReviewResolutionCoordinator,
)
from invomatch.services.orchestration.run_orchestration_service import (
    RunOrchestrationService,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import RunStore


_TERMINAL_STATES = {
    ReviewItemStatus.APPROVED,
    ReviewItemStatus.REJECTED,
    ReviewItemStatus.MODIFIED,
    ReviewItemStatus.DEFERRED,
    ReviewItemStatus.CLOSED,
}

_DECISION_TO_STATUS = {
    DecisionType.APPROVE: ReviewItemStatus.APPROVED,
    DecisionType.REJECT: ReviewItemStatus.REJECTED,
    DecisionType.MODIFY: ReviewItemStatus.MODIFIED,
    DecisionType.DEFER: ReviewItemStatus.DEFERRED,
    DecisionType.REOPEN: ReviewItemStatus.IN_REVIEW,
}


class ResolveReviewActionHandler(BaseActionHandler):
    def __init__(
        self,
        review_service: ReviewService | None = None,
        review_store: InMemoryReviewStore | None = None,
        run_store: RunStore | None = None,
        run_orchestration_service: RunOrchestrationService | None = None,
    ) -> None:
        self._review_service = review_service or ReviewService()
        self._review_store = review_store
        self._run_store = run_store
        self._run_orchestration_service = run_orchestration_service

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
        current_decision_raw = payload.get("current_decision")

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
        feedback_status = FeedbackStatus(
            payload.get("feedback_status", FeedbackStatus.UNDER_REVIEW.value)
        )
        review_item_status = ReviewItemStatus(
            payload.get("review_item_status", ReviewItemStatus.IN_REVIEW.value)
        )
        current_decision = (
            DecisionType(str(current_decision_raw)) if current_decision_raw else None
        )

        expected_status = _DECISION_TO_STATUS[decision]

        if review_item_status in _TERMINAL_STATES:
            if current_decision == decision and review_item_status == expected_status:
                return ActionExecutionResult(
                    action_type=command.action_type,
                    target_type="review_item",
                    target_id=review_item_id,
                    status=ActionExecutionStatus.NO_OP,
                    state_changes=[],
                    side_effects=[],
                    audit_event_ids=[],
                    response_payload={
                        "review_item_id": review_item_id,
                        "review_item_status": review_item_status.value,
                        "feedback_status": feedback_status.value,
                        "decision": decision.value,
                        "eligibility_status": payload.get("eligibility_status"),
                    },
                )

            return ActionExecutionResult(
                action_type=command.action_type,
                target_type="review_item",
                target_id=review_item_id,
                status=ActionExecutionStatus.CONFLICT,
                state_changes=[],
                side_effects=[],
                audit_event_ids=[],
                response_payload={
                    "review_item_id": review_item_id,
                    "review_item_status": review_item_status.value,
                    "feedback_status": feedback_status.value,
                    "decision": current_decision.value if current_decision else None,
                },
            )

        if review_item_status not in {ReviewItemStatus.PENDING, ReviewItemStatus.IN_REVIEW}:
            raise ValueError(
                f"resolve_review is not allowed from state={review_item_status.value}"
            )

        if (
            self._review_store is not None
            and self._run_store is not None
        ):
            persisted_review_item = self._review_store.get_review_item(review_item_id)
            persisted_feedback = self._review_store.get_feedback(feedback_id)

            if persisted_review_item is not None and persisted_feedback is not None:
                coordinator = ReviewResolutionCoordinator(
                    review_store=self._review_store,
                    review_service=self._review_service,
                    run_orchestration_service=(
                        self._run_orchestration_service
                        or RunOrchestrationService(
                            review_store=self._review_store,
                            review_service=self._review_service,
                        )
                    ),
                )

                result, persisted_run = coordinator.resolve_and_reconcile(
                    run_id=command.run_id,
                    review_item_id=review_item_id,
                    feedback_id=feedback_id,
                    reviewer_id=reviewer_id,
                    decision=decision,
                    reason=reason,
                    reviewed_payload=reviewed_payload,
                    run_store=self._run_store,
                )

                eligibility_status = None
                if result.eligibility_record is not None:
                    eligibility_status = result.eligibility_record.eligibility_status.value

                return ActionExecutionResult(
                    action_type=command.action_type,
                    target_type="review_item",
                    target_id=result.review_item.review_item_id,
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
                            "after": persisted_feedback.feedback_status.value,
                        },
                        {
                            "entity": "run",
                            "before": "review_required",
                            "after": persisted_run.status,
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
                        {
                            "type": "run_reconciliation",
                            "run_id": persisted_run.run_id,
                            "run_status": persisted_run.status,
                        },
                    ],
                    audit_event_ids=[result.audit_event.audit_event_id],
                    response_payload={
                        "review_item_id": result.review_item.review_item_id,
                        "review_item_status": result.review_item.item_status.value,
                        "feedback_status": persisted_feedback.feedback_status.value,
                        "decision": result.decision_event.decision_type.value,
                        "eligibility_status": eligibility_status,
                        "run_status": persisted_run.status,
                    },
                )

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
            current_decision=current_decision,
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