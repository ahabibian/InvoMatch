from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, Protocol

from invomatch.domain.models import ReconciliationRun, RunStatus
from invomatch.services.reconciliation_errors import (
    ConcurrencyConflictError,
    RunLeaseConflictError,
)
from invomatch.services.sqlite_run_store import SqliteRunStore

SortOrder = Literal["asc", "desc"]


class RunStore(Protocol):
    def create_run(self, run: ReconciliationRun) -> ReconciliationRun:
        """Persist a newly created reconciliation run."""

    def update_run(self, run: ReconciliationRun, *, expected_version: int) -> ReconciliationRun:
        """Persist changes to an existing reconciliation run with optimistic concurrency."""

    def claim_run(
        self,
        *,
        run_id: str,
        worker_id: str,
        claimed_at: datetime,
        lease_expires_at: datetime,
        expected_version: int,
    ) -> ReconciliationRun:
        """Claim a reconciliation run for execution if it is not actively leased."""

    def heartbeat_run(
        self,
        *,
        run_id: str,
        worker_id: str,
        lease_expires_at: datetime,
        expected_version: int,
    ) -> ReconciliationRun:
        """Extend an active lease for the owning worker."""

    def get_run(self, run_id: str, *, tenant_id: str | None = None) -> ReconciliationRun | None:
        """Load a single reconciliation run by id."""

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        tenant_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = "desc",
    ) -> tuple[list[ReconciliationRun], int]:
        """List persisted reconciliation runs with filtering and pagination."""


def _validate_next_version(run: ReconciliationRun, expected_version: int) -> None:
    if run.version != expected_version + 1:
        raise ValueError(
            f"Updated reconciliation run version must be expected_version + 1; "
            f"expected {expected_version + 1}, got {run.version}"
        )



def _normalize_legacy_run_status(status: Any) -> Any:
    if status == "pending":
        return "queued"
    if status == "running":
        return "processing"
    return status

class JsonRunStore:
    def __init__(self, path: Path):
        self.path = path

    def create_run(self, run: ReconciliationRun) -> ReconciliationRun:
        runs = self._load_all_runs()
        runs.append(run.model_copy(deep=True))
        self._save_all_runs(runs)
        return run.model_copy(deep=True)

    def update_run(self, run: ReconciliationRun, *, expected_version: int) -> ReconciliationRun:
        _validate_next_version(run, expected_version)
        runs = self._load_all_runs()
        for index, persisted_run in enumerate(runs):
            if persisted_run.run_id == run.run_id:
                if persisted_run.version != expected_version:
                    raise ConcurrencyConflictError(
                        f"Reconciliation run version conflict: expected {expected_version}, "
                        f"found {persisted_run.version}",
                        run_id=run.run_id,
                    )
                runs[index] = run.model_copy(deep=True)
                self._save_all_runs(runs)
                return run.model_copy(deep=True)
        raise KeyError(f"Reconciliation run not found: {run.run_id}")

    def claim_run(
        self,
        *,
        run_id: str,
        worker_id: str,
        claimed_at: datetime,
        lease_expires_at: datetime,
        expected_version: int,
    ) -> ReconciliationRun:
        runs = self._load_all_runs()
        for index, persisted_run in enumerate(runs):
            if persisted_run.run_id != run_id:
                continue
            if persisted_run.version != expected_version:
                raise ConcurrencyConflictError(
                    f"Reconciliation run version conflict: expected {expected_version}, "
                    f"found {persisted_run.version}",
                    run_id=run_id,
                )
            if (
                persisted_run.lease_expires_at is not None
                and persisted_run.lease_expires_at >= claimed_at
                and persisted_run.claimed_by is not None
            ):
                raise RunLeaseConflictError(
                    f"Reconciliation run is already leased by {persisted_run.claimed_by}",
                    run_id=run_id,
                )

            updated = persisted_run.model_copy(
                update={
                    "status": "processing",
                    "version": persisted_run.version + 1,
                    "claimed_by": worker_id,
                    "claimed_at": claimed_at,
                    "lease_expires_at": lease_expires_at,
                    "attempt_count": persisted_run.attempt_count + 1,
                    "started_at": persisted_run.started_at or claimed_at,
                    "updated_at": claimed_at,
                }
            )
            runs[index] = updated
            self._save_all_runs(runs)
            return updated.model_copy(deep=True)

        raise KeyError(f"Reconciliation run not found: {run_id}")

    def heartbeat_run(
        self,
        *,
        run_id: str,
        worker_id: str,
        lease_expires_at: datetime,
        expected_version: int,
    ) -> ReconciliationRun:
        runs = self._load_all_runs()
        for index, persisted_run in enumerate(runs):
            if persisted_run.run_id != run_id:
                continue
            if persisted_run.version != expected_version:
                raise ConcurrencyConflictError(
                    f"Reconciliation run version conflict: expected {expected_version}, "
                    f"found {persisted_run.version}",
                    run_id=run_id,
                )
            if persisted_run.claimed_by != worker_id:
                raise RunLeaseConflictError(
                    f"Reconciliation run is not claimed by worker {worker_id}",
                    run_id=run_id,
                )

            updated = persisted_run.model_copy(
                update={
                    "version": persisted_run.version + 1,
                    "lease_expires_at": lease_expires_at,
                    "updated_at": lease_expires_at,
                }
            )
            runs[index] = updated
            self._save_all_runs(runs)
            return updated.model_copy(deep=True)

        raise KeyError(f"Reconciliation run not found: {run_id}")

    def get_run(self, run_id: str, *, tenant_id: str | None = None) -> ReconciliationRun | None:
        for run in self._load_all_runs():
            if run.run_id == run_id and (tenant_id is None or run.tenant_id == tenant_id):
                return run.model_copy(deep=True)
        return None

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        tenant_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = "desc",
    ) -> tuple[list[ReconciliationRun], int]:
        return _query_runs(
            self._load_all_runs(),
            status=status,
            tenant_id=tenant_id,
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
        payload.setdefault("tenant_id", "legacy-tenant")
        payload.setdefault("status", "completed")
        payload.setdefault("version", 0)
        payload.setdefault("claimed_by", None)
        payload.setdefault("claimed_at", None)
        payload.setdefault("lease_expires_at", None)
        payload.setdefault("attempt_count", 0)
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

    def update_run(self, run: ReconciliationRun, *, expected_version: int) -> ReconciliationRun:
        _validate_next_version(run, expected_version)
        for index, persisted_run in enumerate(self._runs):
            if persisted_run.run_id == run.run_id:
                if persisted_run.version != expected_version:
                    raise ConcurrencyConflictError(
                        f"Reconciliation run version conflict: expected {expected_version}, "
                        f"found {persisted_run.version}",
                        run_id=run.run_id,
                    )
                self._runs[index] = run.model_copy(deep=True)
                return run.model_copy(deep=True)
        raise KeyError(f"Reconciliation run not found: {run.run_id}")

    def claim_run(
        self,
        *,
        run_id: str,
        worker_id: str,
        claimed_at: datetime,
        lease_expires_at: datetime,
        expected_version: int,
    ) -> ReconciliationRun:
        for index, persisted_run in enumerate(self._runs):
            if persisted_run.run_id != run_id:
                continue
            if persisted_run.version != expected_version:
                raise ConcurrencyConflictError(
                    f"Reconciliation run version conflict: expected {expected_version}, "
                    f"found {persisted_run.version}",
                    run_id=run_id,
                )
            if (
                persisted_run.lease_expires_at is not None
                and persisted_run.lease_expires_at >= claimed_at
                and persisted_run.claimed_by is not None
            ):
                raise RunLeaseConflictError(
                    f"Reconciliation run is already leased by {persisted_run.claimed_by}",
                    run_id=run_id,
                )

            updated = persisted_run.model_copy(
                update={
                    "status": "processing",
                    "version": persisted_run.version + 1,
                    "claimed_by": worker_id,
                    "claimed_at": claimed_at,
                    "lease_expires_at": lease_expires_at,
                    "attempt_count": persisted_run.attempt_count + 1,
                    "started_at": persisted_run.started_at or claimed_at,
                    "updated_at": claimed_at,
                }
            )
            self._runs[index] = updated
            return updated.model_copy(deep=True)

        raise KeyError(f"Reconciliation run not found: {run_id}")

    def heartbeat_run(
        self,
        *,
        run_id: str,
        worker_id: str,
        lease_expires_at: datetime,
        expected_version: int,
    ) -> ReconciliationRun:
        for index, persisted_run in enumerate(self._runs):
            if persisted_run.run_id != run_id:
                continue
            if persisted_run.version != expected_version:
                raise ConcurrencyConflictError(
                    f"Reconciliation run version conflict: expected {expected_version}, "
                    f"found {persisted_run.version}",
                    run_id=run_id,
                )
            if persisted_run.claimed_by != worker_id:
                raise RunLeaseConflictError(
                    f"Reconciliation run is not claimed by worker {worker_id}",
                    run_id=run_id,
                )

            updated = persisted_run.model_copy(
                update={
                    "version": persisted_run.version + 1,
                    "lease_expires_at": lease_expires_at,
                    "updated_at": lease_expires_at,
                }
            )
            self._runs[index] = updated
            return updated.model_copy(deep=True)

        raise KeyError(f"Reconciliation run not found: {run_id}")

    def get_run(self, run_id: str, *, tenant_id: str | None = None) -> ReconciliationRun | None:
        for run in self._runs:
            if run.run_id == run_id and (tenant_id is None or run.tenant_id == tenant_id):
                return run.model_copy(deep=True)
        return None

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        tenant_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = "desc",
    ) -> tuple[list[ReconciliationRun], int]:
        return _query_runs(
            [run.model_copy(deep=True) for run in self._runs],
            status=status,
            tenant_id=tenant_id,
            limit=limit,
            offset=offset,
            sort_order=sort_order,
        )


def _query_runs(
    runs: list[ReconciliationRun],
    *,
    status: RunStatus | None = None,
        tenant_id: str | None = None,
        limit: int = 50,
    offset: int = 0,
    sort_order: SortOrder = "desc",
) -> tuple[list[ReconciliationRun], int]:
    if tenant_id is not None:
        runs = [run for run in runs if run.tenant_id == tenant_id]

    if status is not None:
        runs = [run for run in runs if run.status == status]

    reverse = sort_order == "desc"
    runs.sort(key=lambda run: (run.created_at, run.run_id), reverse=reverse)

    total = len(runs)
    return runs[offset : offset + limit], total
