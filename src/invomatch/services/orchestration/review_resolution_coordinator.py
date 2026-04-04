from __future__ import annotations

from typing import Optional

from invomatch.domain.models import ReconciliationRun
from invomatch.domain.review.models import DecisionType
from invomatch.services.orchestration.run_orchestration_service import (
    RunOrchestrationService,
)
from invomatch.services.review_service import ReviewDecisionResult, ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import RunStore


class ReviewResolutionCoordinator:
    def __init__(
        self,
        *,
        review_store: InMemoryReviewStore,
        review_service: Optional[ReviewService] = None,
        run_orchestration_service: Optional[RunOrchestrationService] = None,
    ) -> None:
        self._review_store = review_store
        self._review_service = review_service or ReviewService()
        self._run_orchestration_service = (
            run_orchestration_service
            or RunOrchestrationService(
                review_store=review_store,
                review_service=self._review_service,
            )
        )

    def resolve_and_reconcile(
        self,
        *,
        run_id: str,
        review_item_id: str,
        feedback_id: str,
        reviewer_id: str,
        decision: DecisionType,
        run_store: RunStore,
        reason: str | None = None,
        reviewed_payload: dict | None = None,
    ) -> tuple[ReviewDecisionResult, ReconciliationRun]:
        review_item = self._review_store.get_review_item(review_item_id)
        if review_item is None:
            raise KeyError(f"Review item not found: {review_item_id}")

        feedback = self._review_store.get_feedback(feedback_id)
        if feedback is None:
            raise KeyError(f"Feedback not found: {feedback_id}")

        result = self._review_service.apply_decision(
            feedback=feedback,
            review_item=review_item,
            reviewer_id=reviewer_id,
            decision=decision,
            reason=reason,
            reviewed_payload=reviewed_payload,
        )

        self._review_store.save_feedback(feedback)
        self._review_store.save_review_item(result.review_item)
        self._review_store.save_decision_event(result.decision_event)
        self._review_store.save_audit_event(result.audit_event)

        if result.eligibility_record is not None:
            self._review_store.save_eligibility_record(result.eligibility_record)

        _, persisted_run = self._run_orchestration_service.orchestrate_and_persist_post_review_resolution(
            run_id=run_id,
            matching_completed=True,
            run_store=run_store,
        )

        return result, persisted_run