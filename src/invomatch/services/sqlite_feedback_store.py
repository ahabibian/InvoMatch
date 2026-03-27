from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List

from invomatch.domain.feedback import FeedbackRecord
from invomatch.services.feedback_store import FeedbackStore


class SqliteFeedbackStore(FeedbackStore):
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback_records (
                    feedback_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    match_id TEXT NOT NULL,
                    original_status TEXT NOT NULL,
                    corrected_status TEXT NOT NULL,
                    selected_payment_id TEXT NULL,
                    action TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_feedback_run_id ON feedback_records(run_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_feedback_match_id ON feedback_records(match_id)"
            )
            conn.commit()

    def create_feedback(self, record: FeedbackRecord) -> FeedbackRecord:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO feedback_records (
                    feedback_id,
                    run_id,
                    match_id,
                    original_status,
                    corrected_status,
                    selected_payment_id,
                    action,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.feedback_id,
                    record.run_id,
                    record.match_id,
                    record.original_status,
                    record.corrected_status,
                    record.selected_payment_id,
                    record.action,
                    record.created_at.isoformat(),
                ),
            )
            conn.commit()
        return record

    def list_by_run(self, run_id: str) -> List[FeedbackRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    feedback_id,
                    run_id,
                    match_id,
                    original_status,
                    corrected_status,
                    selected_payment_id,
                    action,
                    created_at
                FROM feedback_records
                WHERE run_id = ?
                ORDER BY created_at, feedback_id
                """,
                (run_id,),
            ).fetchall()

        return [self._row_to_model(row) for row in rows]

    def list_by_match(self, match_id: str) -> List[FeedbackRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    feedback_id,
                    run_id,
                    match_id,
                    original_status,
                    corrected_status,
                    selected_payment_id,
                    action,
                    created_at
                FROM feedback_records
                WHERE match_id = ?
                ORDER BY created_at, feedback_id
                """,
                (match_id,),
            ).fetchall()

        return [self._row_to_model(row) for row in rows]

    @staticmethod
    def _row_to_model(row: sqlite3.Row) -> FeedbackRecord:
        return FeedbackRecord(
            feedback_id=row["feedback_id"],
            run_id=row["run_id"],
            match_id=row["match_id"],
            original_status=row["original_status"],
            corrected_status=row["corrected_status"],
            selected_payment_id=row["selected_payment_id"],
            action=row["action"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )