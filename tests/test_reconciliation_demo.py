from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import run_reconciliation_demo as demo


def test_demo_dataset_loads_into_domain_models():
    invoices = demo.load_invoices(ROOT_DIR / "sample-data" / "invoices.csv")
    payments = demo.load_payments(ROOT_DIR / "sample-data" / "payments.csv")

    assert len(invoices) == 50
    assert len(payments) == 80
    assert invoices[0].id.startswith("INV-")
    assert payments[0].payment.id.startswith("PAY-")


def test_demo_summary_counts_are_deterministic():
    invoices = demo.load_invoices(ROOT_DIR / "sample-data" / "invoices.csv")
    payments = demo.load_payments(ROOT_DIR / "sample-data" / "payments.csv")

    results = demo.run_reconciliation(invoices, payments)
    summary = demo.summarize_results(results)

    assert summary == {
        "total_invoices": 50,
        "matched": 20,
        "duplicate_detected": 10,
        "partial_match": 10,
        "unmatched": 10,
    }
