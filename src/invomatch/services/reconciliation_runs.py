from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from invomatch.domain.models import ReconciliationReport, ReconciliationRun, RunStatus, can_transition


DEFAULT_RUN_STORE_PATH = Path("output") / "reconciliation_runs.json"


def _normalize_path_for_storage(path: Path) -> str:
    return path.as_posix()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _read_store(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, list):
        raise ValueError("Reconciliation run store must be a list")
    return payload


def _write_store(path: Path, runs: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(runs, file, indent=2)


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


def _load_runs(store_path: Path) -> list[ReconciliationRun]:
    return [
        ReconciliationRun.model_validate(_backfill_legacy_run_payload(payload))
        for payload in _read_store(store_path)
    ]


def _persist_runs(store_path: Path, runs: list[ReconciliationRun]) -> None:
    _write_store(store_path, [run.model_dump(mode="json") for run in runs])


def create_reconciliation_run(
    invoice_csv_path: Path,
    payment_csv_path: Path,
    store_path: Path = DEFAULT_RUN_STORE_PATH,
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
    runs = _load_runs(store_path)
    runs.append(run)
    _persist_runs(store_path, runs)
    return run


def update_reconciliation_run(
    run_id: str,
    *,
    status: RunStatus,
    report: ReconciliationReport | None = None,
    error_message: str | None = None,
    store_path: Path = DEFAULT_RUN_STORE_PATH,
) -> ReconciliationRun:
    runs = _load_runs(store_path)

    for index, run in enumerate(runs):
        if run.run_id != run_id:
            continue

        if not can_transition(run.status, status):
            raise ValueError(f"Invalid reconciliation run transition: {run.status} -> {status}")

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
        runs[index] = updated_run
        _persist_runs(store_path, runs)
        return updated_run

    raise KeyError(f"Reconciliation run not found: {run_id}")


def save_reconciliation_run(
    report: ReconciliationReport,
    invoice_csv_path: Path,
    payment_csv_path: Path,
    store_path: Path = DEFAULT_RUN_STORE_PATH,
) -> ReconciliationRun:
    run = create_reconciliation_run(
        invoice_csv_path=invoice_csv_path,
        payment_csv_path=payment_csv_path,
        store_path=store_path,
    )
    run = update_reconciliation_run(run.run_id, status="running", store_path=store_path)
    return update_reconciliation_run(
        run.run_id,
        status="completed",
        report=report,
        store_path=store_path,
    )


def load_reconciliation_run(run_id: str, store_path: Path = DEFAULT_RUN_STORE_PATH) -> ReconciliationRun:
    for run in _load_runs(store_path):
        if run.run_id == run_id:
            return run
    raise KeyError(f"Reconciliation run not found: {run_id}")
