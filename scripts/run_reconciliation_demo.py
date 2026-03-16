from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from invomatch.domain.models import ReconciliationReport
from invomatch.services.reconciliation import reconcile


def run_reconciliation(invoice_path: Path, payment_path: Path) -> ReconciliationReport:
    return reconcile(invoice_path, payment_path)


def summarize_results(report: ReconciliationReport) -> dict[str, int]:
    return {
        "total_invoices": report.total_invoices,
        "matched": report.matched,
        "duplicate_detected": report.duplicate_detected,
        "partial_match": report.partial_match,
        "unmatched": report.unmatched,
    }


def write_results(path: Path, report: ReconciliationReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "invoice_id",
        "status",
        "payment_id",
        "duplicate_payment_ids",
        "payment_ids",
        "confidence_score",
        "confidence_explanation",
    ]
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for result in report.results:
            match_result = result.match_result
            writer.writerow(
                {
                    "invoice_id": result.invoice_id,
                    "status": match_result.status,
                    "payment_id": match_result.payment_id or "",
                    "duplicate_payment_ids": "|".join(match_result.duplicate_payment_ids or []),
                    "payment_ids": "|".join(match_result.payment_ids or []),
                    "confidence_score": f"{match_result.confidence_score:.2f}",
                    "confidence_explanation": match_result.confidence_explanation,
                }
            )


def main() -> None:
    report = run_reconciliation(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )
    summary = summarize_results(report)

    print("Reconciliation summary")
    for key, value in summary.items():
        print(f"- {key}: {value}")

    write_results(ROOT_DIR / "output" / "reconciliation_results.csv", report)


if __name__ == "__main__":
    main()
