from __future__ import annotations

from pathlib import Path
from typing import Literal

from invomatch.domain.models import ReconciliationRun, RunStatus
from invomatch.services.reconciliation_runs import DEFAULT_RUN_STORE_PATH, _load_runs

SortOrder = Literal["asc", "desc"]


class RunRegistry:
    def __init__(self, store_path: Path = DEFAULT_RUN_STORE_PATH):
        self._store_path = store_path

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = "desc",
    ) -> tuple[list[ReconciliationRun], int]:
        runs = _load_runs(self._store_path)

        if status is not None:
            runs = [run for run in runs if run.status == status]

        reverse = sort_order == "desc"
        runs.sort(key=lambda run: run.created_at, reverse=reverse)

        total = len(runs)
        return runs[offset : offset + limit], total

    def get_run(self, run_id: str) -> ReconciliationRun | None:
        for run in _load_runs(self._store_path):
            if run.run_id == run_id:
                return run
        return None
