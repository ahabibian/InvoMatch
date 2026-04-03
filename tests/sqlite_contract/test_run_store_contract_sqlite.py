from __future__ import annotations

import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from invomatch.domain.models import ReconciliationRun
from invomatch.services.reconciliation_errors import (
    ConcurrencyConflictError,
    RunLeaseConflictError,
)
from invomatch.services.sqlite_run_store import SqliteRunStore


UTC = timezone.utc


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


class SqliteRunStoreContractAdapter:
    def __init__(self, db_path: Path) -> None:
        self._store = SqliteRunStore(db_path)
        self._awaiting_review_run_ids: set[str] = set()
        self._max_retries_by_run_id: dict[str, int] = {}
        self._retry_count_by_run_id: dict[str, int] = {}

    def create_run(self, run: dict[str, Any] | ReconciliationRun) -> str:
        model = self._normalize_run(run)
        self._store.create_run(model)

        if isinstance(run, dict):
            self._max_retries_by_run_id[model.run_id] = int(run.get("max_retries", 0))
            self._retry_count_by_run_id[model.run_id] = int(run.get("retry_count", 0))
        else:
            self._max_retries_by_run_id.setdefault(model.run_id, 0)
            self._retry_count_by_run_id.setdefault(model.run_id, 0)

        return model.run_id

    def get_run(self, run_id: str) -> ReconciliationRun | None:
        return self._store.get_run(run_id)

    def list_runs(self, limit: int = 100) -> list[ReconciliationRun]:
        runs, _total = self._store.list_runs(limit=limit, offset=0, sort_order="asc")
        return runs

    def claim_next_eligible_run(
        self,
        *,
        worker_id: str,
        now: datetime,
        lease_seconds: int,
    ) -> ReconciliationRun | None:
        runs, _total = self._store.list_runs(limit=1000, offset=0, sort_order="asc")
        lease_expires_at = now + timedelta(seconds=lease_seconds)

        for run in runs:
            if not self._is_claimable(run, now):
                continue

            try:
                claimed = self._store.claim_run(
                    run_id=run.run_id,
                    worker_id=worker_id,
                    claimed_at=now,
                    lease_expires_at=lease_expires_at,
                    expected_version=run.version,
                )
                self._retry_count_by_run_id[run.run_id] = claimed.attempt_count
                return claimed
            except (ConcurrencyConflictError, RunLeaseConflictError):
                continue

        return None

    def renew_claim(
        self,
        *,
        run_id: str,
        worker_id: str,
        now: datetime,
        lease_seconds: int,
    ) -> bool:
        run = self._store.get_run(run_id)
        if run is None:
            return False

        try:
            self._store.heartbeat_run(
                run_id=run_id,
                worker_id=worker_id,
                lease_expires_at=now + timedelta(seconds=lease_seconds),
                expected_version=run.version,
            )
            return True
        except (KeyError, ConcurrencyConflictError, RunLeaseConflictError):
            return False

    def release_claim(self, run_id: str, worker_id: str) -> bool:
        run = self._store.get_run(run_id)
        if run is None:
            return False
        if run.claimed_by != worker_id:
            return False

        released = run.model_copy(
            update={
                "status": "queued",
                "version": run.version + 1,
                "claimed_by": None,
                "claimed_at": None,
                "lease_expires_at": None,
                "updated_at": utc_now(),
            }
        )
        self._store.update_run(released, expected_version=run.version)
        return True

    def mark_awaiting_review(self, run_id: str) -> bool:
        run = self._store.get_run(run_id)
        if run is None:
            return False

        base_status = "queued" if str(run.status) == "processing" else str(run.status)
        updated = run.model_copy(
            update={
                "status": base_status,
                "version": run.version + 1,
                "claimed_by": None,
                "claimed_at": None,
                "lease_expires_at": None,
                "updated_at": utc_now(),
            }
        )
        self._store.update_run(updated, expected_version=run.version)
        self._awaiting_review_run_ids.add(run_id)
        return True

    def mark_completed(self, run_id: str, result_uri: str) -> bool:
        run = self._store.get_run(run_id)
        if run is None:
            return False

        now = utc_now()
        updated = run.model_copy(
            update={
                "status": "completed",
                "version": run.version + 1,
                "finished_at": now,
                "claimed_by": None,
                "claimed_at": None,
                "lease_expires_at": None,
                "updated_at": now,
            }
        )
        self._store.update_run(updated, expected_version=run.version)
        self._awaiting_review_run_ids.discard(run_id)
        return True

    def mark_failed(self, run_id: str, error_code: str, error_message: str) -> bool:
        run = self._store.get_run(run_id)
        if run is None:
            return False

        now = utc_now()
        updated = run.model_copy(
            update={
                "status": "failed",
                "version": run.version + 1,
                "finished_at": now,
                "error_message": error_message,
                "claimed_by": None,
                "claimed_at": None,
                "lease_expires_at": None,
                "updated_at": now,
            }
        )
        self._store.update_run(updated, expected_version=run.version)
        self._awaiting_review_run_ids.discard(run_id)
        return True

    def is_retry_allowed(self, run_id: str) -> bool:
        run = self._store.get_run(run_id)
        if run is None:
            return False

        if run_id in self._awaiting_review_run_ids:
            return False

        if str(run.status) == "completed":
            return False

        max_retries = self._max_retries_by_run_id.get(run_id, 0)
        retry_count = self._retry_count_by_run_id.get(run_id, 0)
        return retry_count < max_retries

    def increment_retry(self, run_id: str) -> bool:
        run = self._store.get_run(run_id)
        if run is None:
            return False

        current_retry = self._retry_count_by_run_id.get(run_id, run.attempt_count)
        max_retries = self._max_retries_by_run_id.get(run_id, 0)

        if current_retry >= max_retries:
            return False

        updated = run.model_copy(
            update={
                "version": run.version + 1,
                "updated_at": utc_now(),
            }
        )
        self._store.update_run(updated, expected_version=run.version)
        self._retry_count_by_run_id[run_id] = current_retry + 1
        return True

    def update_progress(
        self,
        *,
        run_id: str,
        status: str,
        stage: str | None = None,
        current_stage: str | None = None,
    ) -> bool:
        run = self._store.get_run(run_id)
        if run is None:
            return False

        if str(run.status) in {"completed", "failed"}:
            return False

        updated = run.model_copy(
            update={
                "status": status,
                "version": run.version + 1,
                "updated_at": utc_now(),
            }
        )
        self._store.update_run(updated, expected_version=run.version)
        return True

    def _is_claimable(self, run: ReconciliationRun, now: datetime) -> bool:
        if run.run_id in self._awaiting_review_run_ids:
            return False

        if str(run.status) in {"completed", "failed"}:
            return False

        if run.claimed_by is None:
            return True

        if run.lease_expires_at is None:
            return True

        return run.lease_expires_at < now

    @staticmethod
    def _normalize_run(run: dict[str, Any] | ReconciliationRun) -> ReconciliationRun:
        if isinstance(run, ReconciliationRun):
            return run

        payload = dict(run)

        created_at = payload["created_at"]
        updated_at = payload.get("updated_at", created_at)
        finished_at = payload.get("finished_at", payload.get("completed_at"))
        lease_expires_at = payload.get("lease_expires_at", payload.get("claim_expires_at"))

        normalized = {
            "run_id": payload["run_id"],
            "status": payload.get("status", "queued"),
            "version": payload.get("version", 0),
            "created_at": created_at,
            "updated_at": updated_at,
            "started_at": payload.get("started_at"),
            "finished_at": finished_at,
            "claimed_by": payload.get("claimed_by"),
            "claimed_at": payload.get("claimed_at"),
            "lease_expires_at": lease_expires_at,
            "attempt_count": payload.get("attempt_count", payload.get("retry_count", 0)),
            "invoice_csv_path": payload["invoice_csv_path"],
            "payment_csv_path": payload["payment_csv_path"],
            "error_message": payload.get("error_message"),
            "report": payload.get("report"),
        }

        return ReconciliationRun.model_validate(normalized)


_contract_path = Path(__file__).resolve().parents[1] / "test_run_store_contract.py"
_spec = importlib.util.spec_from_file_location("run_store_contract_module", _contract_path)
_contract = importlib.util.module_from_spec(_spec)
assert _spec is not None
assert _spec.loader is not None
_spec.loader.exec_module(_contract)


@pytest.fixture
def run_store(tmp_path: Path) -> SqliteRunStoreContractAdapter:
    return SqliteRunStoreContractAdapter(tmp_path / "run_store_contract.sqlite3")


sample_run = _contract.sample_run

for _name, _value in vars(_contract).items():
    if _name.startswith("test_"):
        globals()[_name] = _value

pytestmark = pytest.mark.sqlite_contract