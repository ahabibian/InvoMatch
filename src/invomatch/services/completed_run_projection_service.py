from __future__ import annotations

from typing import Any

from invomatch.domain.models import ReconciliationRun
from invomatch.services.export.finalized_projection_store import FinalizedProjectionStore
from invomatch.services.export.finalized_projection_writer import FinalizedProjectionWriter


class CompletedRunProjectionIntegrityError(RuntimeError):
    """Raised when a completed run cannot be guaranteed to have a readable finalized projection."""


class CompletedRunProjectionService:
    """
    Centralized invariant service for completed-run finalized projections.

    Rule:
    Every completed run that can become product-completed must have exactly one
    immutable finalized projection, persisted idempotently, tenant-bound, and
    readable before the completed state is persisted.
    """

    def __init__(
        self,
        *,
        projection_store: FinalizedProjectionStore | None,
        review_store: Any,
    ) -> None:
        self._projection_store = projection_store
        self._review_store = review_store

    def persist_if_completed(self, run: ReconciliationRun) -> None:
        if str(getattr(run, "status", "")) != "completed":
            return
        self.ensure_for_completed_run(run)

    def ensure_for_completed_run(self, run: ReconciliationRun) -> None:
        if str(getattr(run, "status", "")) != "completed":
            raise CompletedRunProjectionIntegrityError(
                f"projection integrity can only be enforced for completed runs: "
                f"tenant_id={getattr(run, 'tenant_id', None)}, run_id={getattr(run, 'run_id', None)}, "
                f"status={getattr(run, 'status', None)}"
            )

        if self._projection_store is None:
            raise CompletedRunProjectionIntegrityError(
                f"completed run requires finalized projection store before completion: "
                f"tenant_id={run.tenant_id}, run_id={run.run_id}"
            )

        writer = FinalizedProjectionWriter(
            projection_store=self._projection_store,
            review_store=self._review_store,
        )
        writer.persist_for_completed_run(run)

        results = self._projection_store.get_results(
            tenant_id=run.tenant_id,
            run_id=run.run_id,
        )
        if not results:
            raise CompletedRunProjectionIntegrityError(
                f"completed run finalized projection is not readable after persistence: "
                f"tenant_id={run.tenant_id}, run_id={run.run_id}"
            )