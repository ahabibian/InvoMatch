from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_reconciliation_demo as demo


def test_demo_summary_counts_are_deterministic():
    report = demo.run_reconciliation(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )
    summary = demo.summarize_results(report)

    assert summary == {
        "total_invoices": 50,
        "matched": 20,
        "duplicate_detected": 10,
        "partial_match": 10,
        "unmatched": 10,
    }


def test_demo_report_shape_is_stable():
    report = demo.run_reconciliation(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )

    assert report.total_invoices == 50
    assert len(report.results) == 50
    assert report.results[0].invoice_id.startswith("INV-")
