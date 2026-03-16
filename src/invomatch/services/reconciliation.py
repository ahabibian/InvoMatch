from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from invomatch.domain.models import (
    MatchResult,
    Payment,
    ReconciliationReport,
    ReconciliationResult,
)
from invomatch.services.ingestion import load_invoices_from_csv, parse_payment_row
from invomatch.services.matching_engine import match


def _load_payments_by_invoice(path: Path) -> dict[str, list[Payment]]:
    payments_by_invoice: dict[str, list[Payment]] = {}
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            invoice_id = (row.get("invoice_id") or "").strip() or None
            if invoice_id is None:
                continue
            payments_by_invoice.setdefault(invoice_id, []).append(parse_payment_row(row))
    return payments_by_invoice


def _summarize(results: list[ReconciliationResult]) -> dict[str, int]:
    status_counts = Counter(result.match_result.status for result in results)
    return {
        "total_invoices": len(results),
        "matched": status_counts.get("matched", 0),
        "duplicate_detected": status_counts.get("duplicate_detected", 0),
        "partial_match": status_counts.get("partial_match", 0),
        "unmatched": status_counts.get("unmatched", 0),
    }


def reconcile(invoice_csv_path: Path, payment_csv_path: Path) -> ReconciliationReport:
    invoices = load_invoices_from_csv(invoice_csv_path)
    payments_by_invoice = _load_payments_by_invoice(payment_csv_path)

    results: list[ReconciliationResult] = []
    for invoice in invoices:
        match_result: MatchResult = match(invoice, payments_by_invoice.get(invoice.id, []))
        results.append(
            ReconciliationResult(
                invoice_id=invoice.id,
                match_result=match_result,
            )
        )

    summary = _summarize(results)
    return ReconciliationReport(results=results, **summary)
