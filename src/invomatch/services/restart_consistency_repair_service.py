from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from invomatch.domain.review.models import ReviewItemStatus
from invomatch.services.reconciliation_runs import update_reconciliation_run


_ACTIVE_REVIEW_ITEM_STATUSES = {
    ReviewItemStatus.PENDING,
    ReviewItemStatus.IN_REVIEW,
    ReviewItemStatus.DEFERRED,
}


@dataclass(frozen=True, slots=True)
class RestartConsistencyRepairResult:
    run_id: str
    original_status: str
    repaired_status: str
    reason: str


class RestartConsistencyRepairService:
    def __init__(self, *, run_store: Any, review_store: Any) -> None:
        self._run_store = run_store
        self._review_store = review_store

    def repair_run(self, run_id: str) -> Optional[RestartConsistencyRepairResult]:
        run = self._run_store.get_run(run_id)
        if run is None:
            raise KeyError(f"Reconciliation run not found: {run_id}")

        active_review_exists = self._has_active_review_cases(run_id=run_id)

        if run.status == "processing" and active_review_exists:
            persisted = update_reconciliation_run(
                run_id,
                status="review_required",
                run_store=self._run_store,
            )
            return RestartConsistencyRepairResult(
                run_id=persisted.run_id,
                original_status="processing",
                repaired_status="review_required",
                reason="active_review_cases_present",
            )

        if run.status == "review_required" and not active_review_exists:
            persisted = update_reconciliation_run(
                run_id,
                status="completed",
                run_store=self._run_store,
            )
            return RestartConsistencyRepairResult(
                run_id=persisted.run_id,
                original_status="review_required",
                repaired_status="completed",
                reason="no_active_review_cases_remaining",
            )

        if run.status == "completed" and active_review_exists:
            original_version = run.version
            repaired_run = run.model_copy(
                update={
                    "status": "review_required",
                    "version": original_version + 1,
                }
            )
            persisted = self._run_store.update_run(
                repaired_run,
                expected_version=original_version,
            )
            return RestartConsistencyRepairResult(
                run_id=persisted.run_id,
                original_status="completed",
                repaired_status="review_required",
                reason="active_review_cases_present_for_completed_run",
            )

        return RestartConsistencyRepairResult(
            run_id=run.run_id,
            original_status=run.status,
            repaired_status=run.status,
            reason="no_repair_needed",
        )

    def _has_active_review_cases(self, *, run_id: str) -> bool:
        list_review_items = getattr(self._review_store, "list_review_items", None)
        get_feedback = getattr(self._review_store, "get_feedback", None)

        if list_review_items is None or get_feedback is None:
            return False

        for review_item in list_review_items():
            if review_item.item_status not in _ACTIVE_REVIEW_ITEM_STATUSES:
                continue

            feedback = get_feedback(review_item.feedback_id)
            if feedback is None:
                continue

            if str(getattr(feedback, "run_id", "")) != str(run_id):
                continue

            return True

        return False