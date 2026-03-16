from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from invomatch.domain.models import ReconciliationReport, ReconciliationRun


DEFAULT_RUN_STORE_PATH = Path("output") / "reconciliation_runs.json"


def _read_store(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, list):
        raise ValueError("Reconciliation run store must be a list")
    return payload


def _write_store(path: Path, runs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(runs, file, indent=2)


def save_reconciliation_run(
    report: ReconciliationReport,
    invoice_csv_path: Path,
    payment_csv_path: Path,
    store_path: Path = DEFAULT_RUN_STORE_PATH,
) -> ReconciliationRun:
    run = ReconciliationRun(
        run_id=uuid.uuid4().hex,
        created_at=datetime.now(timezone.utc),
        invoice_csv_path=str(invoice_csv_path),
        payment_csv_path=str(payment_csv_path),
        report=report,
    )
    runs = _read_store(store_path)
    runs.append(run.model_dump(mode="json"))
    _write_store(store_path, runs)
    return run


def load_reconciliation_run(run_id: str, store_path: Path = DEFAULT_RUN_STORE_PATH) -> ReconciliationRun:
    for run_payload in _read_store(store_path):
        if run_payload.get("run_id") == run_id:
            return ReconciliationRun.model_validate(run_payload)
    raise KeyError(f"Reconciliation run not found: {run_id}")
