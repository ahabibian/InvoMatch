from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, Protocol

from invomatch.domain.models import ReconciliationRun, RunStatus

SortOrder = Literal["asc", "desc"]


class RunStore(Protocol):
    def create_run(self, run: ReconciliationRun) -> ReconciliationRun:
        """Persist a newly created reconciliation run."""

    def update_run(self, run: ReconciliationRun) -> ReconciliationRun:
        """Persist changes to an existing reconciliation run."""

    def get_run(self, run_id: str) -> ReconciliationRun | None:
        """Load a single reconciliation run by id."""

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = "desc",
    ) -> tuple[list[ReconciliationRun], int]:
        """List persisted reconciliation runs with filtering and pagination."""


class JsonRunStore:
    def __init__(self, path: Path):
        self.path = path

    def create_run(self, run: ReconciliationRun) -> ReconciliationRun:
        runs = self._load_all_runs()
        runs.append(run)
        self._save_all_runs(runs)
        return run.model_copy(deep=True)

    def update_run(self, run: ReconciliationRun) -> ReconciliationRun:
        runs = self._load_all_runs()
        for index, persisted_run in enumerate(runs):
            if persisted_run.run_id == run.run_id:
                runs[index] = run
                self._save_all_runs(runs)
                return run.model_copy(deep=True)
        raise KeyError(f"Reconciliation run not found: {run.run_id}")

    def get_run(self, run_id: str) -> ReconciliationRun | None:
        for run in self._load_all_runs():
            if run.run_id == run_id:
                return run
        return None

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = "desc",
    ) -> tuple[list[ReconciliationRun], int]:
        return _query_runs(
            self._load_all_runs(),
            status=status,
            limit=limit,
            offset=offset,
            sort_order=sort_order,
        )

    def _load_all_runs(self) -> list[ReconciliationRun]:
        return [
            ReconciliationRun.model_validate(self._backfill_legacy_run_payload(payload))
            for payload in self._read_payload()
        ]

    def _save_all_runs(self, runs: list[ReconciliationRun]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump([run.model_dump(mode="json") for run in runs], file, indent=2)

    def _read_payload(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as file:
            payload = json.load(file)
        if not isinstance(payload, list):
            raise ValueError("Reconciliation run store must be a list")
        return payload

    @staticmethod
    def _backfill_legacy_run_payload(run_payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(run_payload)
        created_at = payload.get("created_at")
        payload.setdefault("status", "completed")
        payload.setdefault("updated_at", created_at)
        payload.setdefault("started_at", created_at)
        payload.setdefault("finished_at", created_at)
        payload.setdefault("error_message", None)
        payload.setdefault("report", None)
        return payload


class InMemoryRunStore:
    def __init__(self, runs: list[ReconciliationRun] | None = None):
        self._runs = [run.model_copy(deep=True) for run in runs or []]

    def create_run(self, run: ReconciliationRun) -> ReconciliationRun:
        self._runs.append(run.model_copy(deep=True))
        return run.model_copy(deep=True)

    def update_run(self, run: ReconciliationRun) -> ReconciliationRun:
        for index, persisted_run in enumerate(self._runs):
            if persisted_run.run_id == run.run_id:
                self._runs[index] = run.model_copy(deep=True)
                return run.model_copy(deep=True)
        raise KeyError(f"Reconciliation run not found: {run.run_id}")

    def get_run(self, run_id: str) -> ReconciliationRun | None:
        for run in self._runs:
            if run.run_id == run_id:
                return run.model_copy(deep=True)
        return None

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = "desc",
    ) -> tuple[list[ReconciliationRun], int]:
        return _query_runs(
            [run.model_copy(deep=True) for run in self._runs],
            status=status,
            limit=limit,
            offset=offset,
            sort_order=sort_order,
        )


def _query_runs(
    runs: list[ReconciliationRun],
    *,
    status: RunStatus | None = None,
    limit: int = 50,
    offset: int = 0,
    sort_order: SortOrder = "desc",
) -> tuple[list[ReconciliationRun], int]:
    if status is not None:
        runs = [run for run in runs if run.status == status]

    reverse = sort_order == "desc"
    runs.sort(key=lambda run: run.created_at, reverse=reverse)

    total = len(runs)
    return runs[offset : offset + limit], total
