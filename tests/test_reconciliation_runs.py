import json
from pathlib import Path

import pytest

from invomatch.domain.models import ReconciliationReport, can_transition, is_terminal_status
from invomatch.services.reconciliation import reconcile
from invomatch.services.reconciliation_runs import (
    create_reconciliation_run,
    load_reconciliation_run,
    save_reconciliation_run,
    update_reconciliation_run,
)

ROOT_DIR = Path(__file__).resolve().parents[1]


def test_lifecycle_helpers_enforce_terminal_status_and_valid_transitions():
    assert is_terminal_status("completed") is True
    assert is_terminal_status("failed") is True
    assert is_terminal_status("pending") is False
    assert can_transition("pending", "running") is True
    assert can_transition("running", "completed") is True
    assert can_transition("completed", "running") is False


def test_create_reconciliation_run_persists_pending_lifecycle(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"

    run = create_reconciliation_run(
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        store_path=store_path,
    )

    assert run.status == "pending"
    assert run.created_at == run.updated_at
    assert run.started_at is None
    assert run.finished_at is None
    assert run.error_message is None
    assert run.report is None
    assert store_path.exists()


def test_update_reconciliation_run_persists_all_lifecycle_fields(tmp_path: Path):
    report = reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )
    store_path = tmp_path / "reconciliation_runs.json"

    run = create_reconciliation_run(
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        store_path=store_path,
    )
    running_run = update_reconciliation_run(run.run_id, status="running", store_path=store_path)
    completed_run = update_reconciliation_run(
        run.run_id,
        status="completed",
        report=report,
        store_path=store_path,
    )
    loaded_run = load_reconciliation_run(run.run_id, store_path=store_path)

    assert running_run.status == "running"
    assert running_run.started_at is not None
    assert running_run.finished_at is None
    assert completed_run.status == "completed"
    assert completed_run.started_at is not None
    assert completed_run.finished_at is not None
    assert completed_run.error_message is None
    assert isinstance(loaded_run.report, ReconciliationReport)
    assert loaded_run.report.total_invoices == report.total_invoices
    assert loaded_run.report.matched == report.matched
    assert loaded_run.report.duplicate_detected == report.duplicate_detected
    assert loaded_run.report.partial_match == report.partial_match
    assert loaded_run.report.unmatched == report.unmatched
    assert len(loaded_run.report.results) == len(report.results)


def test_update_reconciliation_run_rejects_invalid_transition(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    run = create_reconciliation_run(
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        store_path=store_path,
    )
    update_reconciliation_run(run.run_id, status="running", store_path=store_path)
    update_reconciliation_run(run.run_id, status="completed", report=None, store_path=store_path)

    with pytest.raises(ValueError, match="Invalid reconciliation run transition"):
        update_reconciliation_run(run.run_id, status="running", store_path=store_path)


def test_load_reconciliation_run_backfills_legacy_completed_payload(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    report = reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )
    legacy_payload = [
        {
            "run_id": "legacy-run",
            "created_at": "2026-03-18T10:00:00Z",
            "invoice_csv_path": "sample-data/invoices.csv",
            "payment_csv_path": "sample-data/payments.csv",
            "report": report.model_dump(mode="json"),
        }
    ]
    store_path.write_text(json.dumps(legacy_payload), encoding="utf-8")

    loaded_run = load_reconciliation_run("legacy-run", store_path=store_path)

    assert loaded_run.status == "completed"
    assert loaded_run.updated_at == loaded_run.created_at
    assert loaded_run.started_at == loaded_run.created_at
    assert loaded_run.finished_at == loaded_run.created_at
    assert loaded_run.error_message is None
    assert loaded_run.report is not None


def test_save_reconciliation_run_preserves_summary_and_result_structure(tmp_path: Path):
    report = reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )
    store_path = tmp_path / "reconciliation_runs.json"

    saved_run = save_reconciliation_run(
        report=report,
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        store_path=store_path,
    )
    loaded_run = load_reconciliation_run(saved_run.run_id, store_path=store_path)

    assert loaded_run.status == "completed"
    assert loaded_run.report is not None
    first_result = loaded_run.report.results[0]
    assert first_result.invoice_id.startswith("INV-")
    assert first_result.match_result.status in {
        "matched",
        "duplicate_detected",
        "partial_match",
        "unmatched",
    }
