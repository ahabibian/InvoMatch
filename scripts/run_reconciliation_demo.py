from __future__ import annotations

import csv
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from invomatch.domain.models import Invoice, Payment
from invomatch.services.ingestion import load_invoices_from_csv, parse_payment_row
from invomatch.services.matching_engine import match


@dataclass(frozen=True)
class PaymentRecord:
    payment: Payment
    invoice_id: str | None


def load_invoices(path: Path) -> list[Invoice]:
    return load_invoices_from_csv(path)


def load_payments(path: Path) -> list[PaymentRecord]:
    payments: list[PaymentRecord] = []
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            payments.append(
                PaymentRecord(
                    payment=parse_payment_row(row),
                    invoice_id=row["invoice_id"] or None,
                )
            )
    return payments


def run_reconciliation(invoices: list[Invoice], payment_records: list[PaymentRecord]) -> list[dict[str, str]]:
    payments_by_invoice: dict[str, list[Payment]] = {}
    for payment_record in payment_records:
        if payment_record.invoice_id is None:
            continue
        payments_by_invoice.setdefault(payment_record.invoice_id, []).append(payment_record.payment)

    results: list[dict[str, str]] = []
    for invoice in invoices:
        result = match(invoice, payments_by_invoice.get(invoice.id, []))
        results.append(
            {
                "invoice_id": invoice.id,
                "status": result.status,
                "payment_id": result.payment_id or "",
                "duplicate_payment_ids": "|".join(result.duplicate_payment_ids or []),
                "payment_ids": "|".join(result.payment_ids or []),
                "confidence_score": f"{result.confidence_score:.2f}",
                "confidence_explanation": result.confidence_explanation,
            }
        )
    return results


def summarize_results(results: list[dict[str, str]]) -> dict[str, int]:
    status_counts = Counter(result["status"] for result in results)
    return {
        "total_invoices": len(results),
        "matched": status_counts.get("matched", 0),
        "duplicate_detected": status_counts.get("duplicate_detected", 0),
        "partial_match": status_counts.get("partial_match", 0),
        "unmatched": status_counts.get("unmatched", 0),
    }


def write_results(path: Path, results: list[dict[str, str]]) -> None:
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
        writer.writerows(results)


def main() -> None:
    invoices = load_invoices(ROOT_DIR / "sample-data" / "invoices.csv")
    payment_records = load_payments(ROOT_DIR / "sample-data" / "payments.csv")
    results = run_reconciliation(invoices, payment_records)
    summary = summarize_results(results)

    print("Reconciliation summary")
    for key, value in summary.items():
        print(f"- {key}: {value}")

    write_results(ROOT_DIR / "output" / "reconciliation_results.csv", results)


if __name__ == "__main__":
    main()
