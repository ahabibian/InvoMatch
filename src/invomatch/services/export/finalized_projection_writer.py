from __future__ import annotations

from typing import Any

from invomatch.domain.models import ReconciliationRun
from invomatch.services.export.finalized_projection import FinalizedResultProjection
from invomatch.services.export.finalized_projection_store import FinalizedProjectionStore
from invomatch.services.export.source_loader import ExportSourceLoader


class FinalizedProjectionWriter:
    def __init__(
        self,
        *,
        projection_store: FinalizedProjectionStore,
        source_loader: ExportSourceLoader | None = None,
        projection_builder: FinalizedResultProjection | None = None,
        review_store: Any,
    ) -> None:
        self._projection_store = projection_store
        self._source_loader = source_loader or ExportSourceLoader()
        self._projection_builder = projection_builder or FinalizedResultProjection()
        self._review_store = review_store

    def persist_for_completed_run(self, run: ReconciliationRun) -> None:
        if run.status != "completed":
            return

        if self._projection_store.exists(
            tenant_id=run.tenant_id,
            run_id=run.run_id,
        ):
            return

        source_snapshot = self._source_loader.load_sources_for_run(run)
        results = self._projection_builder.build_results_for_run(
            run=run,
            source_snapshot=source_snapshot,
            review_store=self._review_store,
        )

        self._projection_store.save_results(
            tenant_id=run.tenant_id,
            run_id=run.run_id,
            results=results,
        )
