from __future__ import annotations

import csv
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from invomatch.domain.match_record import MatchRecord
from invomatch.domain.models import (
    MatchResult,
    Payment,
    ReconciliationReport,
    ReconciliationResult,
    ReconciliationRun,
)
from invomatch.services.ingestion import load_invoices_from_csv, parse_payment_row
from invomatch.services.match_record_store import MatchRecordStore
from invomatch.services.matching_engine import match
from invomatch.services.reconciliation_errors import ReconciliationExecutionError
from invomatch.services.reconciliation_runs import (
    DEFAULT_RUN_STORE,
    create_reconciliation_run,
    update_reconciliation_run,
)
from invomatch.services.reconciliation_validation import validate_reconciliation_execution_paths
from invomatch.services.run_store import RunStore
from invomatch.services.sqlite_match_record_store import SqliteMatchRecordStore


DEFAULT_MATCH_RECORD_STORE_PATH = Path("output") / "reconciliation_match_records.sqlite3"
DEFAULT_MATCH_RECORD_STORE = SqliteMatchRecordStore(DEFAULT_MATCH_RECORD_STORE_PATH)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


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


def _candidate_payment_ids(match_result: MatchResult) -> list[str]:
    candidate_ids: list[str] = []

    if match_result.payment_id is not None:
        candidate_ids.append(match_result.payment_id)

    if match_result.payment_ids:
        for payment_id in match_result.payment_ids:
            if payment_id not in candidate_ids:
                candidate_ids.append(payment_id)

    if match_result.duplicate_payment_ids:
        for payment_id in match_result.duplicate_payment_ids:
            if payment_id not in candidate_ids:
                candidate_ids.append(payment_id)

    return candidate_ids


def _build_match_records_from_report(
    *,
    run_id: str,
    report: ReconciliationReport,
) -> list[MatchRecord]:
    created_at = _utcnow()

    records: list[MatchRecord] = []
    for result in report.results:
        match_result = result.match_result
        records.append(
            MatchRecord(
                match_id=uuid.uuid4().hex,
                run_id=run_id,
                invoice_id=result.invoice_id,
                status=match_result.status,
                selected_payment_id=match_result.payment_id,
                candidate_payment_ids=_candidate_payment_ids(match_result),
                confidence_score=match_result.confidence_score,
                confidence_explanation=match_result.confidence_explanation,
                mismatch_reasons=list(match_result.mismatch_reasons),
                created_at=created_at,
            )
        )

    return records


def reconcile_and_save(
    invoice_csv_path: Path,
    payment_csv_path: Path,
    run_store: RunStore = DEFAULT_RUN_STORE,
    match_record_store: MatchRecordStore = DEFAULT_MATCH_RECORD_STORE,
) -> ReconciliationRun:
    validate_reconciliation_execution_paths(invoice_csv_path, payment_csv_path)

    run = create_reconciliation_run(
        invoice_csv_path=invoice_csv_path,
        payment_csv_path=payment_csv_path,
        run_store=run_store,
    )
    run = update_reconciliation_run(run.run_id, status="processing", run_store=run_store)

    try:
        report = reconcile(invoice_csv_path, payment_csv_path)
        match_records = _build_match_records_from_report(
            run_id=run.run_id,
            report=report,
        )
        match_record_store.save_many(match_records)
    except Exception as exc:
        update_reconciliation_run(
            run.run_id,
            status="failed",
            error_message=str(exc),
            run_store=run_store,
        )
        raise ReconciliationExecutionError(
            f"Reconciliation execution failed: {exc}",
            run_id=run.run_id,
        ) from exc

    return update_reconciliation_run(
        run.run_id,
        status="completed",
        report=report,
        run_store=run_store,
    )