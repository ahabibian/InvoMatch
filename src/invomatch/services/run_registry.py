from __future__ import annotations

from typing import Literal

from invomatch.domain.models import ReconciliationRun, RunStatus
from invomatch.services.reconciliation_runs import DEFAULT_RUN_STORE
from invomatch.services.run_store import RunStore

SortOrder = Literal["asc", "desc"]


class RunRegistry:
    def __init__(self, run_store: RunStore = DEFAULT_RUN_STORE):
        self._run_store = run_store

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        tenant_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = "desc",
    ) -> tuple[list[ReconciliationRun], int]:
        return self._run_store.list_runs(
            status=status,
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            sort_order=sort_order,
        )

    def get_run(
        self,
        run_id: str,
        *,
        tenant_id: str | None = None
    ) -> ReconciliationRun | None:
        return self._run_store.get_run(run_id, tenant_id=tenant_id)
