from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from invomatch.domain.models import ReconciliationReport, ReconciliationRun, RunStatus
from invomatch.domain.run_lifecycle import InvalidRunStateTransition, assert_transition_allowed
from invomatch.services.run_store import JsonRunStore, RunStore


DEFAULT_RUN_STORE_PATH = Path("output") / "reconciliation_runs.json"
DEFAULT_RUN_STORE = JsonRunStore(DEFAULT_RUN_STORE_PATH)


def _normalize_path_for_storage(path: Path) -> str:
    return path.as_posix()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_reconciliation_run(
    invoice_csv_path: Path,
    payment_csv_path: Path,
    run_store: RunStore = DEFAULT_RUN_STORE,
) -> ReconciliationRun:
    now = _utcnow()
    run = ReconciliationRun(
        run_id=uuid.uuid4().hex,
        status="pending",
        created_at=now,
        updated_at=now,
        started_at=None,
        finished_at=None,
        invoice_csv_path=_normalize_path_for_storage(invoice_csv_path),
        payment_csv_path=_normalize_path_for_storage(payment_csv_path),
        error_message=None,
        report=None,
    )
    return run_store.create_run(run)


def update_reconciliation_run(
    run_id: str,
    *,
    status: RunStatus,
    report: ReconciliationReport | None = None,
    error_message: str | None = None,
    run_store: RunStore = DEFAULT_RUN_STORE,
) -> ReconciliationRun:
    run = run_store.get_run(run_id)
    if run is None:
        raise KeyError(f"Reconciliation run not found: {run_id}")

    try:
        assert_transition_allowed(run.status, status)
    except InvalidRunStateTransition as exc:
        raise ValueError(
            f"Invalid reconciliation run transition: {run.status} -> {status}"
        ) from exc

    now = _utcnow()
    started_at = run.started_at
    finished_at = run.finished_at

    if status == "running" and started_at is None:
        started_at = now
    if status in {"completed", "failed"}:
        if started_at is None:
            started_at = now
        finished_at = now

    updated_run = run.model_copy(
        update={
            "status": status,
            "updated_at": now,
            "started_at": started_at,
            "finished_at": finished_at,
            "error_message": error_message,
            "report": report,
        }
    )
    return run_store.update_run(updated_run)


def save_reconciliation_run(
    report: ReconciliationReport,
    invoice_csv_path: Path,
    payment_csv_path: Path,
    run_store: RunStore = DEFAULT_RUN_STORE,
) -> ReconciliationRun:
    run = create_reconciliation_run(
        invoice_csv_path=invoice_csv_path,
        payment_csv_path=payment_csv_path,
        run_store=run_store,
    )
    run = update_reconciliation_run(run.run_id, status="running", run_store=run_store)
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
