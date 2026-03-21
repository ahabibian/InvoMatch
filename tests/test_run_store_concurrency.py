from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from invomatch.domain.models import ReconciliationRun
from invomatch.services.reconciliation_errors import ConcurrencyConflictError
from invomatch.services.run_store import InMemoryRunStore, JsonRunStore
from invomatch.services.sqlite_run_store import SqliteRunStore


def _build_run(run_id: str = "run-1") -> ReconciliationRun:
    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        run_id=run_id,
        status="pending",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=None,
        finished_at=None,
        invoice_csv_path="invoices.csv",
        payment_csv_path="payments.csv",
        error_message=None,
        report=None,
    )


@pytest.fixture(params=["json", "sqlite", "memory"])
def store(request, tmp_path: Path):
    if request.param == "json":
        return JsonRunStore(tmp_path / "runs.json")
    if request.param == "sqlite":
        return SqliteRunStore(tmp_path / "runs.sqlite3")
    return InMemoryRunStore()


def test_update_run_increments_version_when_expected_version_matches(store):
    created = store.create_run(_build_run())

    updated = created.model_copy(
        update={
            "status": "running",
            "version": created.version + 1,
            "updated_at": datetime.now(timezone.utc),
        }
    )

    persisted = store.update_run(updated, expected_version=created.version)

    assert persisted.version == 1
    loaded = store.get_run(created.run_id)
    assert loaded is not None
    assert loaded.version == 1
    assert loaded.status == "running"


def test_update_run_rejects_stale_version(store):
    created = store.create_run(_build_run())

    first_update = created.model_copy(
        update={
            "status": "running",
            "version": created.version + 1,
            "updated_at": datetime.now(timezone.utc),
        }
    )
    store.update_run(first_update, expected_version=created.version)

    stale_update = created.model_copy(
        update={
            "status": "failed",
            "version": created.version + 1,
            "updated_at": datetime.now(timezone.utc),
            "error_message": "stale write",
        }
    )

    with pytest.raises(ConcurrencyConflictError):
        store.update_run(stale_update, expected_version=created.version)


def test_update_run_requires_next_version(store):
    created = store.create_run(_build_run())

    invalid_update = created.model_copy(
        update={
            "status": "running",
            "version": created.version,
            "updated_at": datetime.now(timezone.utc),
        }
    )

    with pytest.raises(ValueError):
        store.update_run(invalid_update, expected_version=created.version)
