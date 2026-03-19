from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol

from invomatch.domain.models import ReconciliationRun


class RunStore(Protocol):
    def load_runs(self) -> list[ReconciliationRun]:
        """Load all persisted reconciliation runs."""

    def save_runs(self, runs: list[ReconciliationRun]) -> None:
        """Persist the full reconciliation run collection."""


class JsonRunStore:
    def __init__(self, path: Path):
        self.path = path

    def load_runs(self) -> list[ReconciliationRun]:
        return [
            ReconciliationRun.model_validate(self._backfill_legacy_run_payload(payload))
            for payload in self._read_payload()
        ]

    def save_runs(self, runs: list[ReconciliationRun]) -> None:
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

    def load_runs(self) -> list[ReconciliationRun]:
        return [run.model_copy(deep=True) for run in self._runs]

    def save_runs(self, runs: list[ReconciliationRun]) -> None:
        self._runs = [run.model_copy(deep=True) for run in runs]
