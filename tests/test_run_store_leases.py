from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from invomatch.domain.models import ReconciliationRun
from invomatch.services.reconciliation_errors import (
    ConcurrencyConflictError,
    RunLeaseConflictError,
)
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
        claimed_by=None,
        claimed_at=None,
        lease_expires_at=None,
        attempt_count=0,
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


def test_claim_run_assigns_worker_and_increments_attempt_count(store):
    created = store.create_run(_build_run())
    now = datetime.now(timezone.utc)
    lease_expires_at = now + timedelta(seconds=60)

    claimed = store.claim_run(
        run_id=created.run_id,
        worker_id="worker-a",
        claimed_at=now,
        lease_expires_at=lease_expires_at,
        expected_version=created.version,
    )

    assert claimed.status == "running"
    assert claimed.claimed_by == "worker-a"
    assert claimed.attempt_count == 1
    assert claimed.version == 1
    assert claimed.started_at is not None


def test_claim_run_rejects_second_active_lease(store):
    created = store.create_run(_build_run())
    now = datetime.now(timezone.utc)

    store.claim_run(
        run_id=created.run_id,
        worker_id="worker-a",
        claimed_at=now,
        lease_expires_at=now + timedelta(seconds=60),
        expected_version=created.version,
    )

    fresh = store.get_run(created.run_id)
    assert fresh is not None

    with pytest.raises(RunLeaseConflictError):
        store.claim_run(
            run_id=created.run_id,
            worker_id="worker-b",
            claimed_at=now + timedelta(seconds=1),
            lease_expires_at=now + timedelta(seconds=61),
            expected_version=fresh.version,
        )


def test_claim_run_allows_reclaim_after_lease_expiry(store):
    created = store.create_run(_build_run())
    now = datetime.now(timezone.utc)

    first = store.claim_run(
        run_id=created.run_id,
        worker_id="worker-a",
        claimed_at=now,
        lease_expires_at=now + timedelta(seconds=10),
        expected_version=created.version,
    )

    reclaimed = store.claim_run(
        run_id=created.run_id,
        worker_id="worker-b",
        claimed_at=now + timedelta(seconds=11),
        lease_expires_at=now + timedelta(seconds=71),
        expected_version=first.version,
    )

    assert reclaimed.claimed_by == "worker-b"
    assert reclaimed.attempt_count == 2
    assert reclaimed.version == 2


def test_heartbeat_run_extends_lease_for_owner(store):
    created = store.create_run(_build_run())
    now = datetime.now(timezone.utc)

    claimed = store.claim_run(
        run_id=created.run_id,
        worker_id="worker-a",
        claimed_at=now,
        lease_expires_at=now + timedelta(seconds=60),
        expected_version=created.version,
    )

    heartbeated = store.heartbeat_run(
        run_id=created.run_id,
        worker_id="worker-a",
        lease_expires_at=now + timedelta(seconds=120),
        expected_version=claimed.version,
    )

    assert heartbeated.version == claimed.version + 1
    assert heartbeated.lease_expires_at == now + timedelta(seconds=120)


def test_heartbeat_run_rejects_non_owner(store):
    created = store.create_run(_build_run())
    now = datetime.now(timezone.utc)

    claimed = store.claim_run(
        run_id=created.run_id,
        worker_id="worker-a",
        claimed_at=now,
        lease_expires_at=now + timedelta(seconds=60),
        expected_version=created.version,
    )

    with pytest.raises(RunLeaseConflictError):
        store.heartbeat_run(
            run_id=created.run_id,
            worker_id="worker-b",
            lease_expires_at=now + timedelta(seconds=120),
            expected_version=claimed.version,
        )


def test_claim_run_rejects_stale_version(store):
    created = store.create_run(_build_run())
    now = datetime.now(timezone.utc)

    first = store.claim_run(
        run_id=created.run_id,
        worker_id="worker-a",
        claimed_at=now,
        lease_expires_at=now + timedelta(seconds=60),
        expected_version=created.version,
    )

    with pytest.raises(ConcurrencyConflictError):
        store.claim_run(
            run_id=created.run_id,
            worker_id="worker-b",
            claimed_at=now + timedelta(seconds=61),
            lease_expires_at=now + timedelta(seconds=121),
            expected_version=created.version,
        )

    assert first.version == 1
