from pathlib import Path

from invomatch.services.reconciliation import reconcile

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
