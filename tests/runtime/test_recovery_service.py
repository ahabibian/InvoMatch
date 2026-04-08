from datetime import datetime, timedelta, timezone
from pathlib import Path

from invomatch.domain.models import ReconciliationRun
from invomatch.runtime.runtime_failure import FailureCategory, RuntimeFailure
from invomatch.services.runtime_recovery_service import RuntimeRecoveryService
from invomatch.services.run_store import InMemoryRunStore


def _now() -> datetime:
    return datetime(2026, 4, 8, 12, 0, 0, tzinfo=timezone.utc)


def _processing_run(
    *,
    run_id: str,
    claimed_by: str | None,
    lease_expires_at: datetime | None,
) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        run_id=run_id,
        status="processing",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=None,
        claimed_by=claimed_by,
        claimed_at=now if claimed_by is not None else None,
        lease_expires_at=lease_expires_at,
        attempt_count=1,
        invoice_csv_path="sample-data/invoices.csv",
        payment_csv_path="sample-data/payments.csv",
        error_message=None,
        report=None,
    )


def _queued_run(run_id: str) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        run_id=run_id,
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
        invoice_csv_path="sample-data/invoices.csv",
        payment_csv_path="sample-data/payments.csv",
        error_message=None,
        report=None,
    )


def _failure(
    *,
    category: FailureCategory,
    is_retryable: bool,
    is_terminal: bool,
) -> RuntimeFailure:
    return RuntimeFailure(
        category=category,
        code="test_code",
        message="test_message",
        is_retryable=is_retryable,
        is_terminal=is_terminal,
    )


def test_scan_and_apply_recovery_terminalizes_processing_run_without_owner():
    run_store = InMemoryRunStore()
    run_store.create_run(
        _processing_run(
            run_id="run-fail-no-owner",
            claimed_by=None,
            lease_expires_at=_now() + timedelta(seconds=30),
        )
    )

    service = RuntimeRecoveryService()
    result = service.scan_and_apply_recovery(run_store=run_store, now=_now())

    assert result.scanned_processing_runs == 1
    assert result.failed_run_ids == ["run-fail-no-owner"]
    assert result.reenter_candidate_run_ids == []

    persisted = run_store.get_run("run-fail-no-owner")
    assert persisted is not None
    assert persisted.status == "failed"
    assert persisted.finished_at is not None
    assert persisted.error_message is not None
    assert "[stuck_run]" in persisted.error_message


def test_scan_and_apply_recovery_surfaces_reentry_candidate_without_terminalizing():
    run_store = InMemoryRunStore()
    run_store.create_run(
        _processing_run(
            run_id="run-reenter",
            claimed_by="worker-1",
            lease_expires_at=_now() - timedelta(seconds=5),
        )
    )

    failure_lookup = {
        "run-reenter": _failure(
            category=FailureCategory.DEPENDENCY_FAILURE,
            is_retryable=True,
            is_terminal=False,
        )
    }

    service = RuntimeRecoveryService()
    result = service.scan_and_apply_recovery(
        run_store=run_store,
        failure_lookup=failure_lookup,
        now=_now(),
    )

    assert result.scanned_processing_runs == 1
    assert result.failed_run_ids == []
    assert result.reenter_candidate_run_ids == ["run-reenter"]

    persisted = run_store.get_run("run-reenter")
    assert persisted is not None
    assert persisted.status == "processing"
    assert persisted.finished_at is None
    assert persisted.error_message is None


def test_scan_and_apply_recovery_leaves_active_processing_run_untouched():
    run_store = InMemoryRunStore()
    run_store.create_run(
        _processing_run(
            run_id="run-active",
            claimed_by="worker-1",
            lease_expires_at=_now() + timedelta(seconds=60),
        )
    )

    service = RuntimeRecoveryService()
    result = service.scan_and_apply_recovery(run_store=run_store, now=_now())

    assert result.scanned_processing_runs == 1
    assert result.failed_run_ids == []
    assert result.reenter_candidate_run_ids == []
    assert result.untouched_run_ids == ["run-active"]

    persisted = run_store.get_run("run-active")
    assert persisted is not None
    assert persisted.status == "processing"
    assert persisted.finished_at is None


def test_scan_and_apply_recovery_only_scans_processing_runs():
    run_store = InMemoryRunStore()
    run_store.create_run(_queued_run("run-queued"))
    run_store.create_run(
        _processing_run(
            run_id="run-processing",
            claimed_by=None,
            lease_expires_at=_now() + timedelta(seconds=30),
        )
    )

    service = RuntimeRecoveryService()
    result = service.scan_and_apply_recovery(run_store=run_store, now=_now())

    assert result.scanned_processing_runs == 1

    queued = run_store.get_run("run-queued")
    assert queued is not None
    assert queued.status == "queued"