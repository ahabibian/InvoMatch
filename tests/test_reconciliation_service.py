from pathlib import Path

import pytest

from invomatch.services.reconciliation import reconcile, reconcile_and_save
from invomatch.services.reconciliation_runs import load_reconciliation_run

ROOT_DIR = Path(__file__).resolve().parents[1]


def test_reconcile_returns_typed_report_with_summary_counts():
    report = reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )

    assert report.total_invoices == 50
    assert report.matched == 20
    assert report.duplicate_detected == 10
    assert report.partial_match == 10
    assert report.unmatched == 10


def test_reconcile_results_are_bound_to_invoice_ids():
    report = reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )

    assert len(report.results) == report.total_invoices
    assert all(result.invoice_id.startswith("INV-") for result in report.results)
    assert all(result.match_result.status in {"matched", "duplicate_detected", "partial_match", "unmatched"} for result in report.results)


def test_reconcile_and_save_moves_run_through_completed_lifecycle(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"

    run = reconcile_and_save(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
        store_path=store_path,
    )

    persisted_run = load_reconciliation_run(run.run_id, store_path=store_path)

    assert run.status == "completed"
    assert run.started_at is not None
    assert run.finished_at is not None
    assert run.updated_at >= run.created_at
    assert run.report is not None
    assert run.error_message is None
    assert persisted_run.status == "completed"
    assert persisted_run.report is not None


def test_reconcile_and_save_marks_run_failed_when_execution_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    store_path = tmp_path / "reconciliation_runs.json"

    def boom(invoice_csv_path: Path, payment_csv_path: Path):
        raise RuntimeError("reconciliation exploded")

    monkeypatch.setattr("invomatch.services.reconciliation.reconcile", boom)

    with pytest.raises(RuntimeError, match="reconciliation exploded"):
        reconcile_and_save(
            ROOT_DIR / "sample-data" / "invoices.csv",
            ROOT_DIR / "sample-data" / "payments.csv",
            store_path=store_path,
        )

    persisted_runs = __import__("json").loads(store_path.read_text(encoding="utf-8"))
    assert len(persisted_runs) == 1
    failed_run = persisted_runs[0]
    assert failed_run["status"] == "failed"
    assert failed_run["started_at"] is not None
    assert failed_run["finished_at"] is not None
    assert failed_run["error_message"] == "reconciliation exploded"
    assert failed_run["report"] is None
