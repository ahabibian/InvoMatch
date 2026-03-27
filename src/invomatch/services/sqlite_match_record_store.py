from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from invomatch.domain.match_record import MatchRecord
from invomatch.services.reconciliation_errors import RunStorageError

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS reconciliation_match_records (
    match_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    invoice_id TEXT NOT NULL,
    status TEXT NOT NULL,
    selected_payment_id TEXT NULL,
    candidate_payment_ids_json TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    confidence_explanation TEXT NOT NULL,
    mismatch_reasons_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reconciliation_match_records_run_id
    ON reconciliation_match_records (run_id, created_at, match_id);

CREATE INDEX IF NOT EXISTS idx_reconciliation_match_records_invoice_id
    ON reconciliation_match_records (invoice_id, created_at, match_id);
"""


class SqliteMatchRecordStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self._bootstrap_schema()

    def save_many(self, records: list[MatchRecord]) -> None:
        if not records:
            return

        rows = [
            (
                record.match_id,
                record.run_id,
                record.invoice_id,
                record.status,
                record.selected_payment_id,
                json.dumps(record.candidate_payment_ids, separators=(",", ":")),
                record.confidence_score,
                record.confidence_explanation,
                json.dumps(record.mismatch_reasons, separators=(",", ":")),
                record.created_at.isoformat(),
            )
            for record in records
        ]

        try:
            with self._connect() as connection:
                connection.executemany(
                    """
                    INSERT INTO reconciliation_match_records (
                        match_id,
                        run_id,
                        invoice_id,
                        status,
                        selected_payment_id,
                        candidate_payment_ids_json,
                        confidence_score,
                        confidence_explanation,
                        mismatch_reasons_json,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    rows,
                )
                connection.commit()
        except sqlite3.Error as exc:
            raise RunStorageError(f"Failed to persist match records: {exc}") from exc

    def list_by_run(self, run_id: str) -> list[MatchRecord]:
        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        match_id,
                        run_id,
                        invoice_id,
                        status,
                        selected_payment_id,
                        candidate_payment_ids_json,
                        confidence_score,
                        confidence_explanation,
                        mismatch_reasons_json,
                        created_at
                    FROM reconciliation_match_records
                    WHERE run_id = ?
                    ORDER BY created_at, match_id
                    """,
                    (run_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise RunStorageError(f"Failed to load match records: {exc}", run_id=run_id) from exc

        return [self._deserialize_row(row) for row in rows]

    def _bootstrap_schema(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(SCHEMA_SQL)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _deserialize_row(row: sqlite3.Row) -> MatchRecord:
        return MatchRecord.model_validate(
            {
                "match_id": row["match_id"],
                "run_id": row["run_id"],
                "invoice_id": row["invoice_id"],
                "status": row["status"],
                "selected_payment_id": row["selected_payment_id"],
                "candidate_payment_ids": json.loads(row["candidate_payment_ids_json"]),
                "confidence_score": row["confidence_score"],
                "confidence_explanation": row["confidence_explanation"],
                "mismatch_reasons": json.loads(row["mismatch_reasons_json"]),
                "created_at": row["created_at"],
            }
        )