from __future__ import annotations

from typing import Any

from invomatch.domain.models import ReconciliationRun
from invomatch.services.export.finalized_projection_store import FinalizedProjectionStore
from invomatch.services.export.finalized_projection_writer import FinalizedProjectionWriter


class CompletedRunProjectionService:
    """
    Centralized invariant service for completed-run finalized projections.

    Rule:
    Every completed run that can be exported must have exactly one immutable
    finalized projection, persisted idempotently and tenant-bound.
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

        if self._projection_store is None:
            return

        writer = FinalizedProjectionWriter(
            projection_store=self._projection_store,
            review_store=self._review_store,
        )
        writer.persist_for_completed_run(run)