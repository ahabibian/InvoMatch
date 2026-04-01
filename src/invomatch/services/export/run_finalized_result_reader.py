from __future__ import annotations

from typing import Any

from invomatch.domain.export import FinalizedResult
from invomatch.services.export.errors import RunNotExportableError
from invomatch.services.export.finalized_projection import FinalizedResultProjection
from invomatch.services.export.source_loader import ExportSourceLoader
from invomatch.services.reconciliation_runs import load_reconciliation_run
from invomatch.services.run_store import RunStore


class RunFinalizedResultReader:
    def __init__(
        self,
        *,
        run_store: RunStore | None = None,
        source_loader: ExportSourceLoader | None = None,
        projection: FinalizedResultProjection | None = None,
        review_store: Any | None = None,
    ) -> None:
        self._run_store = run_store
        self._source_loader = source_loader or ExportSourceLoader()
        self._projection = projection or FinalizedResultProjection()
        self._review_store = review_store

    def read(self, *, run_id: str) -> list[FinalizedResult]:
        run = self._load_run(run_id)

        if str(run.status) != "completed":
            raise RunNotExportableError(
                f"run is not exportable in status={run.status}"
            )

        source_snapshot = self._source_loader.load_sources_for_run(run)

        results = self._projection.build_results_for_run(
            run=run,
            source_snapshot=source_snapshot,
            review_store=self._review_store,
        )

        return results

    def _load_run(self, run_id: str):
        if self._run_store is None:
            return load_reconciliation_run(run_id)

        return load_reconciliation_run(run_id, run_store=self._run_store)
