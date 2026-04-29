from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from invomatch.services.export.errors import InconsistentProjectionStateError
from invomatch.services.export.finalized_projection_store import FinalizedProjectionStore
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
        projection_store: FinalizedProjectionStore | None = None,
    ) -> None:
        self._run_store = run_store
        self._review_store = review_store or InMemoryReviewStore()
        self._projection_store = projection_store
        self._review_integration_service = ReviewIntegrationService(
            review_service=review_service or ReviewService(),
            review_store=self._review_store,
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

        if self._projection_store is None:
            return ExportReadinessResult(
                is_export_ready=False,
                reason="finalized_projection_store_unavailable",
            )

        if not self._projection_store.exists(
            tenant_id=run.tenant_id,
            run_id=run_id,
        ):
            raise InconsistentProjectionStateError(
                f"completed run has no finalized projection: tenant_id={run.tenant_id}, run_id={run_id}"
            )

        results = self._projection_store.get_results(
            tenant_id=run.tenant_id,
            run_id=run_id,
        )
        if results is None:
            raise InconsistentProjectionStateError(
                f"completed run has no readable finalized projection: tenant_id={run.tenant_id}, run_id={run_id}"
            )

        return ExportReadinessResult(
            is_export_ready=True,
            reason="export_allowed",
        )
