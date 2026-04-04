from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from invomatch.services.orchestration.review_integration_service import (
    ReviewIntegrationService,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import RunStore


@dataclass(frozen=True)
class ExportReadinessResult:
    is_export_ready: bool
    reason: str


class ExportReadinessEvaluator:
    def __init__(
        self,
        *,
        run_store: RunStore,
        review_store: Optional[InMemoryReviewStore] = None,
        review_service: Optional[ReviewService] = None,
    ) -> None:
        self._run_store = run_store
        self._review_integration_service = ReviewIntegrationService(
            review_service=review_service or ReviewService(),
            review_store=review_store or InMemoryReviewStore(),
        )

    def evaluate(self, run_id: str) -> ExportReadinessResult:
        run = self._run_store.get_run(run_id)
        if run is None:
            return ExportReadinessResult(
                is_export_ready=False,
                reason="run_not_found",
            )

        if run.status != "completed":
            return ExportReadinessResult(
                is_export_ready=False,
                reason=f"run_status_not_completed:{run.status}",
            )

        active_cases = [
            case
            for case in self._review_integration_service.get_active_cases()
            if case.get("run_id") == run_id and case.get("blocking", True)
        ]

        if active_cases:
            return ExportReadinessResult(
                is_export_ready=False,
                reason="active_blocking_review_cases_present",
            )

        return ExportReadinessResult(
            is_export_ready=True,
            reason="export_allowed",
        )