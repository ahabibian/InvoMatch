from __future__ import annotations

from pathlib import Path

from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.sqlite_match_record_store import SqliteMatchRecordStore
from invomatch.services.sqlite_run_store import SqliteRunStore


def test_reconcile_and_save_persists_match_records(tmp_path: Path) -> None:
    invoice_csv = tmp_path / "invoices.csv"
    payment_csv = tmp_path / "payments.csv"
    run_db = tmp_path / "runs.sqlite3"
    match_db = tmp_path / "match_records.sqlite3"

    invoice_csv.write_text(
        "id,date,amount,reference\n"
        "inv-001,2026-03-01,100.00,ABC-1\n",
        encoding="utf-8",
    )

    payment_csv.write_text(
        "invoice_id,id,date,amount,reference\n"
        "inv-001,pay-001,2026-03-02,100.00,ABC-1\n",
        encoding="utf-8",
    )

    run_store = SqliteRunStore(run_db)
    match_store = SqliteMatchRecordStore(match_db)

    run = reconcile_and_save(
        invoice_csv_path=invoice_csv,
        payment_csv_path=payment_csv,
        run_store=run_store,
        match_record_store=match_store,
    )

    records = match_store.list_by_run(run.run_id)

    assert run.status == "completed"
    assert len(records) == 1
    assert records[0].run_id == run.run_id
    assert records[0].invoice_id == "inv-001"