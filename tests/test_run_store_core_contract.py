from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from invomatch.domain.models import ReconciliationRun
from invomatch.services.reconciliation_runs import (
    claim_reconciliation_run,
    create_reconciliation_run,
    heartbeat_reconciliation_run,
    load_reconciliation_run,
    update_reconciliation_run,
)
from invomatch.services.reconciliation_errors import (
    ConcurrencyConflictError,
    RunLeaseConflictError,
)
from invomatch.services.run_store import SqliteRunStore


UTC = timezone.utc


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


@pytest.fixture
def run_store(tmp_path: Path) -> SqliteRunStore:
    return SqliteRunStore(tmp_path / "core_contract.sqlite3")


@pytest.fixture
def invoice_path(tmp_path: Path) -> Path:
    path = tmp_path / "invoices.csv"
    path.write_text("id,date,amount,reference`nINV-1,2026-03-26,100.00,REF-1`n", encoding="utf-8")
    return path


@pytest.fixture
def payment_path(tmp_path: Path) -> Path:
    path = tmp_path / "payments.csv"
    path.write_text("id,date,amount,reference`nPAY-1,2026-03-26,100.00,REF-1`n", encoding="utf-8")
    return path


def test_create_then_get_returns_authoritative_run(
    run_store: SqliteRunStore,
    invoice_path: Path,
    payment_path: Path,
) -> None:
    created = create_reconciliation_run(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )

    loaded = load_reconciliation_run(created.run_id, run_store=run_store)

    assert loaded.run_id == created.run_id
    assert loaded.status == "queued"
    assert loaded.invoice_csv_path == invoice_path.as_posix()
    assert loaded.payment_csv_path == payment_path.as_posix()


def test_duplicate_create_is_rejected(run_store: SqliteRunStore, tmp_path: Path) -> None:
    now = utc_now()
    run = ReconciliationRun(
        run_id="run-duplicate",
        status="queued",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=None,
        finished_at=None,
        claimed_by=None,
        claimed_at=None,
        lease_expires_at=None,
        attempt_count=0,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error_message=None,
        report=None,
    )

    run_store.create_run(run)

    with pytest.raises(Exception):
        run_store.create_run(run)


def test_list_runs_is_deterministic(
    run_store: SqliteRunStore,
    invoice_path: Path,
    payment_path: Path,
) -> None:
    created = []
    for _ in range(2):
        created.append(
            create_reconciliation_run(
                invoice_csv_path=invoice_path,
                payment_csv_path=payment_path,
                run_store=run_store,
            )
        )

    first, total_first = run_store.list_runs(sort_order="asc")
    second, total_second = run_store.list_runs(sort_order="asc")

    assert total_first == total_second
    assert [run.run_id for run in first] == [run.run_id for run in second]


def test_not_found_read_returns_none(run_store: SqliteRunStore) -> None:
    assert run_store.get_run("missing-run") is None


def test_claim_known_run_by_id_updates_state(
    run_store: SqliteRunStore,
    invoice_path: Path,
    payment_path: Path,
) -> None:
    run = create_reconciliation_run(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )

    claimed = claim_reconciliation_run(
        run.run_id,
        worker_id="worker-1",
        run_store=run_store,
    )

    assert claimed.run_id == run.run_id
    assert claimed.status == "processing"
    assert claimed.claimed_by == "worker-1"
    assert claimed.lease_expires_at is not None
    assert claimed.version >= 1


def test_claim_conflict_is_visible(
    run_store: SqliteRunStore,
    invoice_path: Path,
    payment_path: Path,
) -> None:
    run = create_reconciliation_run(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )

    claimed = claim_reconciliation_run(
        run.run_id,
        worker_id="worker-1",
        run_store=run_store,
    )

    with pytest.raises((RunLeaseConflictError, ConcurrencyConflictError)):
        run_store.claim_run(
            run_id=run.run_id,
            worker_id="worker-2",
            claimed_at=utc_now(),
            lease_expires_at=utc_now(),
            expected_version=run.version,
        )


def test_heartbeat_succeeds_for_current_owner_only(
    run_store: SqliteRunStore,
    invoice_path: Path,
    payment_path: Path,
) -> None:
    run = create_reconciliation_run(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )

    claimed = claim_reconciliation_run(
        run.run_id,
        worker_id="worker-1",
        run_store=run_store,
    )

    refreshed = heartbeat_reconciliation_run(
        claimed.run_id,
        worker_id="worker-1",
        run_store=run_store,
    )

    assert refreshed.claimed_by == "worker-1"
    assert refreshed.lease_expires_at is not None

    with pytest.raises((RunLeaseConflictError, ConcurrencyConflictError)):
        heartbeat_reconciliation_run(
            claimed.run_id,
            worker_id="worker-2",
            run_store=run_store,
        )


def test_mark_completed_through_update_flow_is_terminal(
    run_store: SqliteRunStore,
    invoice_path: Path,
    payment_path: Path,
) -> None:
    run = create_reconciliation_run(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )

    running = update_reconciliation_run(
        run.run_id,
        status="processing",
        run_store=run_store,
    )
    completed = update_reconciliation_run(
        running.run_id,
        status="completed",
        run_store=run_store,
    )

    assert completed.status == "completed"
    assert completed.finished_at is not None

    with pytest.raises(ValueError):
        update_reconciliation_run(
            completed.run_id,
            status="processing",
            run_store=run_store,
        )


def test_mark_failed_through_update_flow_is_terminal(
    run_store: SqliteRunStore,
    invoice_path: Path,
    payment_path: Path,
) -> None:
    run = create_reconciliation_run(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )

    running = update_reconciliation_run(
        run.run_id,
        status="processing",
        run_store=run_store,
    )
    failed = update_reconciliation_run(
        running.run_id,
        status="failed",
        error_message="simulated failure",
        run_store=run_store,
    )

    assert failed.status == "failed"
    assert failed.finished_at is not None
    assert failed.error_message == "simulated failure"

    with pytest.raises(ValueError):
        update_reconciliation_run(
            failed.run_id,
            status="processing",
            run_store=run_store,
        )