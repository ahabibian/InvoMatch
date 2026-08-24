from __future__ import annotations

from pathlib import Path

from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.export.finalized_projection_store import SqliteFinalizedProjectionStore
from invomatch.services.sqlite_match_record_store import SqliteMatchRecordStore
from invomatch.services.sqlite_run_store import SqliteRunStore
from invomatch.services.sqlite_review_store import SqliteReviewStore
from invomatch.services.review_queries import ReviewQueryService


def test_reconcile_and_save_persists_match_records(tmp_path: Path) -> None:
    invoice_csv = tmp_path / "invoices.csv"
    payment_csv = tmp_path / "payments.csv"
    run_db = tmp_path / "runs.sqlite3"
    match_db = tmp_path / "match_records.sqlite3"
    projection_db = tmp_path / "finalized_projections.sqlite3"

    invoice_csv.write_text(
        "id,date,amount,reference,currency\n"
        "inv-001,2026-03-01,100.00,ABC-1,SEK\n",
        encoding="utf-8",
    )

    payment_csv.write_text(
        "invoice_id,id,date,amount,reference,currency\n"
        "inv-001,pay-001,2026-03-02,100.00,ABC-1,SEK\n",
        encoding="utf-8",
    )

    run_store = SqliteRunStore(run_db)
    match_store = SqliteMatchRecordStore(match_db)
    projection_store = SqliteFinalizedProjectionStore(projection_db)

    run = reconcile_and_save(
        invoice_csv_path=invoice_csv,
        payment_csv_path=payment_csv,
        run_store=run_store,
        match_record_store=match_store,
        projection_store=projection_store,
    )

    records = match_store.list_by_run(run.run_id)

    assert run.status == "completed"
    assert len(records) == 1
    assert records[0].run_id == run.run_id
    assert records[0].invoice_id == "inv-001"


def test_review_required_matches_materialize_backend_owned_review_queue(tmp_path: Path) -> None:
    invoice_csv = tmp_path / "scenario-15-invoices.csv"
    payment_csv = tmp_path / "scenario-15-payments.csv"
    invoice_csv.write_text(
        "id,date,amount,reference,currency\n"
        "scenario-15-invoice,2026-08-24,125.50,PILOT-15,EUR\n",
        encoding="utf-8",
    )
    payment_csv.write_text(
        "invoice_id,id,date,amount,reference,currency\n"
        "scenario-15-invoice,scenario-15-payment-a,2026-08-24,125.50,PILOT-15,EUR\n"
        "scenario-15-invoice,scenario-15-payment-b,2026-08-24,125.50,PILOT-15,EUR\n",
        encoding="utf-8",
    )
    run_store = SqliteRunStore(tmp_path / "runs.sqlite3")
    match_store = SqliteMatchRecordStore(tmp_path / "matches.sqlite3")
    review_store = SqliteReviewStore(tmp_path / "reviews.sqlite3")

    run = reconcile_and_save(
        invoice_csv,
        payment_csv,
        run_store=run_store,
        match_record_store=match_store,
        review_store=review_store,
    )

    query = ReviewQueryService()
    query.init(review_store)
    queue = query.list_review_queue_rows()
    detail = query.list_match_detail_candidates()
    assert run.status == "review_required"
    assert len(queue) == 1
    assert queue[0].run_id == run.run_id
    assert queue[0].match_id
    assert detail[0].match_id == queue[0].match_id
    assert detail[0].invoice_id == "scenario-15-invoice"
    assert detail[0].payment_id in {"scenario-15-payment-a", "scenario-15-payment-b"}
    assert detail[0].source_references == (invoice_csv.as_posix(),)
