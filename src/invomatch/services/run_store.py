from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, Protocol

from invomatch.domain.models import ReconciliationRun, RunStatus

SortOrder = Literal["asc", "desc"]


class RunStore(Protocol):
    def create_run(self, run: ReconciliationRun) -> ReconciliationRun:
        """Persist a newly created reconciliation run."""
        ...

    def update_run(self, run: ReconciliationRun) -> ReconciliationRun:
        """Persist an updated reconciliation run."""
        ...

    def get_run(self, run_id: str) -> ReconciliationRun | None:
        """Load a persisted reconciliation run by id."""
        ...

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = "desc",
    ) -> tuple[list[ReconciliationRun], int]:
        """List persisted runs with filtering and pagination."""
        ...


class JsonRunStore:
    def __init__(self, path: Path):
        self.path = path

    def create_run(self, run: ReconciliationRun) -> ReconciliationRun:
        runs = self._load_all_runs()
        runs.append(run)
        self._write_runs(runs)
        return run.model_copy(deep=True)

    def update_run(self, run: ReconciliationRun) -> ReconciliationRun:
        runs = self._load_all_runs()
        for index, existing_run in enumerate(runs):
            if existing_run.run_id == run.run_id:
                runs[index] = run
                self._write_runs(runs)
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
        runs = self._load_all_runs()
        if status is not None:
            runs = [run for run in runs if run.status == status]

        reverse = sort_order == "desc"
        runs.sort(key=lambda run: run.created_at, reverse=reverse)

        total = len(runs)
        return runs[offset : offset + limit], total

    def _load_all_runs(self) -> list[ReconciliationRun]:
        return [
            ReconciliationRun.model_validate(self._backfill_legacy_run_payload(payload))
            for payload in self._read_payload()
        ]

    def _write_runs(self, runs: list[ReconciliationRun]) -> None:
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
        self._runs = list(runs or [])

    def create_run(self, run: ReconciliationRun) -> ReconciliationRun:
        stored_run = run.model_copy(deep=True)
        self._runs.append(stored_run)
        return stored_run.model_copy(deep=True)

    def update_run(self, run: ReconciliationRun) -> ReconciliationRun:
        stored_run = run.model_copy(deep=True)
        for index, existing_run in enumerate(self._runs):
            if existing_run.run_id == run.run_id:
                self._runs[index] = stored_run
                return stored_run.model_copy(deep=True)
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
        runs = [run.model_copy(deep=True) for run in self._runs]
        if status is not None:
            runs = [run for run in runs if run.status == status]

        reverse = sort_order == "desc"
        runs.sort(key=lambda run: run.created_at, reverse=reverse)

        total = len(runs)
        return runs[offset : offset + limit], total
