from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from invomatch.domain.models import ReconciliationReport, ReconciliationRun, RunError, RunStatus
from invomatch.domain.tenant import TenantContext
from invomatch.services.lifecycle import (
    InvalidRunStateError,
    InvalidRunTransitionError,
    RunLifecycleService,
    TerminalRunStateError,
)
from invomatch.services.run_store import JsonRunStore, RunStore


DEFAULT_RUN_STORE_PATH = Path("output") / "reconciliation_runs.json"
DEFAULT_RUN_STORE = JsonRunStore(DEFAULT_RUN_STORE_PATH)
DEFAULT_LEASE_SECONDS = 60


def _normalize_path_for_storage(path: Path) -> str:
    return path.as_posix()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_reconciliation_run(
    invoice_csv_path: Path,
    payment_csv_path: Path,
    *,
    tenant_id: str = "tenant-demo",
    tenant_context: TenantContext | None = None,
    run_store: RunStore = DEFAULT_RUN_STORE,
) -> ReconciliationRun:
    effective_tenant_id = tenant_context.tenant_id if tenant_context is not None else tenant_id
    now = _utcnow()
    run = ReconciliationRun(
        run_id=uuid.uuid4().hex,
        tenant_id=effective_tenant_id,
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
        invoice_csv_path=_normalize_path_for_storage(invoice_csv_path),
        payment_csv_path=_normalize_path_for_storage(payment_csv_path),
        error_message=None,
        report=None,
    )
    return run_store.create_run(run)


def claim_reconciliation_run(
    run_id: str,
    *,
    worker_id: str,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    run_store: RunStore = DEFAULT_RUN_STORE,
    now: datetime | None = None,
) -> ReconciliationRun:
    run = run_store.get_run(run_id)
    if run is None:
        raise KeyError(f"Reconciliation run not found: {run_id}")

    effective_now = now or _utcnow()
    lease_expires_at = effective_now + timedelta(seconds=lease_seconds)

    return run_store.claim_run(
        run_id=run_id,
        worker_id=worker_id,
        claimed_at=effective_now,
        lease_expires_at=lease_expires_at,
        expected_version=run.version,
    )


def heartbeat_reconciliation_run(
    run_id: str,
    *,
    worker_id: str,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    run_store: RunStore = DEFAULT_RUN_STORE,
) -> ReconciliationRun:
    run = run_store.get_run(run_id)
    if run is None:
        raise KeyError(f"Reconciliation run not found: {run_id}")

    lease_expires_at = _utcnow() + timedelta(seconds=lease_seconds)
    return run_store.heartbeat_run(
        run_id=run_id,
        worker_id=worker_id,
        lease_expires_at=lease_expires_at,
        expected_version=run.version,
    )


def update_reconciliation_run(
    run_id: str,
    *,
    status: RunStatus,
    report: ReconciliationReport | None = None,
    error: RunError | None = None,
    error_message: str | None = None,
    run_store: RunStore = DEFAULT_RUN_STORE,
) -> ReconciliationRun:
    run = run_store.get_run(run_id)
    if run is None:
        raise KeyError(f"Reconciliation run not found: {run_id}")

    try:
        RunLifecycleService.validate_transition(run.status, status)
    except (InvalidRunStateError, InvalidRunTransitionError, TerminalRunStateError) as exc:
        raise ValueError(
            f"Invalid reconciliation run transition: {run.status} -> {status}"
        ) from exc

    now = _utcnow()
    started_at = run.started_at
    finished_at = run.finished_at

    if status == "processing" and started_at is None:
        started_at = now

    if status in {"completed", "failed", "cancelled"}:
        if started_at is None:
            started_at = now
        finished_at = now

    updated_run = run.model_copy(
        update={
            "status": status,
            "version": run.version + 1,
            "updated_at": now,
            "started_at": started_at,
            "finished_at": finished_at,
            "error": error,
            "error_message": error_message or (error.message if error is not None else None),
            "report": report if report is not None else run.report,
        }
    )
    return run_store.update_run(updated_run, expected_version=run.version)


def save_reconciliation_run(
    report: ReconciliationReport,
    invoice_csv_path: Path,
    payment_csv_path: Path,
    *,
    tenant_id: str = "tenant-demo",
    tenant_context: TenantContext | None = None,
    run_store: RunStore = DEFAULT_RUN_STORE,
) -> ReconciliationRun:
    run = create_reconciliation_run(
        invoice_csv_path=invoice_csv_path,
        payment_csv_path=payment_csv_path,
        tenant_id=tenant_id,
        tenant_context=tenant_context,
        run_store=run_store,
    )
    run = update_reconciliation_run(run.run_id, status="processing", run_store=run_store)
    return update_reconciliation_run(
        run.run_id,
        status="completed",
        report=report,
        run_store=run_store,
    )


def load_reconciliation_run(
    run_id: str,
    run_store: RunStore = DEFAULT_RUN_STORE,
) -> ReconciliationRun:
    run = run_store.get_run(run_id)
    if run is None:
        raise KeyError(f"Reconciliation run not found: {run_id}")
    return run