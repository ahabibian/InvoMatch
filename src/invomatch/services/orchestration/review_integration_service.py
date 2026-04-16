from __future__ import annotations

from typing import Any, Dict, List, Optional

from invomatch.domain.review.models import FeedbackRecord, ReviewItemStatus
from invomatch.services.review_service import ReviewService, new_id
from invomatch.services.review_store import InMemoryReviewStore


_ACTIVE_REVIEW_ITEM_STATUSES = {
    ReviewItemStatus.PENDING,
    ReviewItemStatus.IN_REVIEW,
    ReviewItemStatus.DEFERRED,
}


class ReviewIntegrationService:
    def __init__(
        self,
        review_service: Optional[ReviewService] = None,
        review_store: Optional[InMemoryReviewStore] = None,
    ) -> None:
        self._review_service = review_service or ReviewService()
        self._review_store = review_store or InMemoryReviewStore()

    def create_cases(
        self,
        *,
        run_id: str,
        review_cases: List[Dict[str, Any]],
        created_by: str,
    ) -> None:
        if not review_cases:
            return

        review_session = self._review_service.create_review_session(
            created_by=created_by,
            session_notes=f"Run orchestration session for {run_id}",
        )
        self._review_store.save_review_session(review_session)

        for case in review_cases:
            invoice_id = case["invoice_id"]

            if self._has_active_case_for_run_invoice(
                run_id=run_id,
                invoice_id=invoice_id,
            ):
                continue

            feedback = FeedbackRecord(
                feedback_id=new_id("feedback"),
                run_id=run_id,
                source_type="run_orchestration",
                source_reference=invoice_id,
                feedback_type="REVIEW_CASE",
                raw_payload=case,
                submitted_by=created_by,
            )
            self._review_store.save_feedback(feedback)

            review_item, audit_event = self._review_service.create_review_item(
                feedback=feedback,
                review_session=review_session,
            )
            self._review_store.save_review_item(review_item)
            self._review_store.save_audit_event(audit_event)

    def get_active_cases(self) -> List[Dict[str, Any]]:
        active_cases: List[Dict[str, Any]] = []

        for review_item in self._review_store.list_review_items():
            if review_item.item_status not in _ACTIVE_REVIEW_ITEM_STATUSES:
                continue

            feedback = self._review_store.get_feedback(review_item.feedback_id)
            if feedback is None:
                continue

            raw_payload = feedback.raw_payload or {}

            active_cases.append(
                {
                    "invoice_id": feedback.source_reference,
                    "status": review_item.item_status.value,
                    "blocking": raw_payload.get("blocking", True),
                    "reason": raw_payload.get("reason", "manual_review_required"),
                    "confidence": raw_payload.get("confidence"),
                    "candidates": raw_payload.get("candidates", []),
                    "source_status": raw_payload.get("source_status"),
                    "run_id": feedback.run_id,
                }
            )

        return active_cases

    def _has_active_case_for_run_invoice(
        self,
        *,
        run_id: str,
        invoice_id: str,
    ) -> bool:
        for review_item in self._review_store.list_review_items():
            if review_item.item_status not in _ACTIVE_REVIEW_ITEM_STATUSES:
                continue

            feedback = self._review_store.get_feedback(review_item.feedback_id)
            if feedback is None:
                continue

            if feedback.run_id == run_id and feedback.source_reference == invoice_id:
                return True

        return False