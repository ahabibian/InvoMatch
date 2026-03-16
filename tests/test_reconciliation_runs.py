from pathlib import Path

from invomatch.domain.models import ReconciliationReport
from invomatch.services.reconciliation import reconcile
from invomatch.services.reconciliation_runs import (
    load_reconciliation_run,
    save_reconciliation_run,
)

ROOT_DIR = Path(__file__).resolve().parents[1]


def test_save_reconciliation_run_persists_local_json_store(tmp_path: Path):
    report = reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )
    store_path = tmp_path / "reconciliation_runs.json"

    run = save_reconciliation_run(
        report=report,
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        store_path=store_path,
    )

    assert run.run_id
    assert run.invoice_csv_path.endswith("sample-data/invoices.csv")
    assert run.payment_csv_path.endswith("sample-data/payments.csv")
    assert store_path.exists()


def test_load_reconciliation_run_by_id_returns_typed_run(tmp_path: Path):
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

    assert loaded_run.run_id == saved_run.run_id
    assert isinstance(loaded_run.report, ReconciliationReport)


def test_saved_and_loaded_report_preserves_summary_and_result_structure(tmp_path: Path):
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

    assert loaded_run.report.total_invoices == report.total_invoices
    assert loaded_run.report.matched == report.matched
    assert loaded_run.report.duplicate_detected == report.duplicate_detected
    assert loaded_run.report.partial_match == report.partial_match
    assert loaded_run.report.unmatched == report.unmatched
    assert len(loaded_run.report.results) == len(report.results)

    first_result = loaded_run.report.results[0]
    assert first_result.invoice_id.startswith("INV-")
    assert first_result.match_result.status in {
        "matched",
        "duplicate_detected",
        "partial_match",
        "unmatched",
    }
