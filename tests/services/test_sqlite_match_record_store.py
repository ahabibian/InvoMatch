from __future__ import annotations

from datetime import datetime, timezone

from invomatch.domain.match_record import MatchRecord
from invomatch.services.sqlite_match_record_store import SCHEMA_SQL, SqliteMatchRecordStore


def test_match_record_store_roundtrip(tmp_path) -> None:
    store = SqliteMatchRecordStore(tmp_path / "match_records.sqlite3")

    record = MatchRecord(
        match_id="match-001",
        run_id="run-001",
        invoice_id="invoice-001",
        status="matched",
        selected_payment_id="payment-001",
        candidate_payment_ids=["payment-001"],
        confidence_score=0.98,
        confidence_explanation="Exact candidate selected.",
        mismatch_reasons=["amount_match", "reference_match"],
        created_at=datetime.now(timezone.utc),
    )

    store.save_many([record])

    loaded = store.list_by_run("run-001")

    assert len(loaded) == 1
    assert loaded[0].match_id == "match-001"
    assert loaded[0].selected_payment_id == "payment-001"


def test_match_record_store_schema_contains_required_table() -> None:
    assert "reconciliation_match_records" in SCHEMA_SQL