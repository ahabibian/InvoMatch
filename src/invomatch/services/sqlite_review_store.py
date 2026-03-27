from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from invomatch.domain.review.models import (
    DecisionType,
    ReviewItem,
    ReviewItemStatus,
    ReviewSession,
    ReviewSessionStatus,
)


def _dt(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.isoformat()


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    return datetime.fromisoformat(value)


class SqliteReviewStore:
    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS review_sessions (
                    review_session_id TEXT PRIMARY KEY,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    session_status TEXT NOT NULL,
                    assigned_reviewer_id TEXT NULL,
                    assigned_at TEXT NULL,
                    completed_at TEXT NULL,
                    session_notes TEXT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS review_items (
                    review_item_id TEXT PRIMARY KEY,
                    review_session_id TEXT NOT NULL,
                    feedback_id TEXT NOT NULL,
                    item_status TEXT NOT NULL,
                    current_decision TEXT NULL,
                    decision_reason TEXT NULL,
                    reviewed_payload_json TEXT NULL,
                    reviewed_by TEXT NULL,
                    reviewed_at TEXT NULL,
                    requires_followup INTEGER NOT NULL,
                    learning_eligible INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    # -------------------------------------------------------------------------
    # Review sessions
    # -------------------------------------------------------------------------

    def save_review_session(self, session: ReviewSession) -> ReviewSession:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO review_sessions (
                    review_session_id,
                    created_by,
                    created_at,
                    session_status,
                    assigned_reviewer_id,
                    assigned_at,
                    completed_at,
                    session_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.review_session_id,
                    session.created_by,
                    _dt(session.created_at),
                    session.session_status.value,
                    session.assigned_reviewer_id,
                    _dt(session.assigned_at),
                    _dt(session.completed_at),
                    session.session_notes,
                ),
            )
            conn.commit()

        return session

    def get_review_session(self, review_session_id: str) -> Optional[ReviewSession]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    review_session_id,
                    created_by,
                    created_at,
                    session_status,
                    assigned_reviewer_id,
                    assigned_at,
                    completed_at,
                    session_notes
                FROM review_sessions
                WHERE review_session_id = ?
                """,
                (review_session_id,),
            ).fetchone()

        if row is None:
            return None

        return ReviewSession(
            review_session_id=row["review_session_id"],
            created_by=row["created_by"],
            created_at=datetime.fromisoformat(row["created_at"]),
            session_status=ReviewSessionStatus(row["session_status"]),
            assigned_reviewer_id=row["assigned_reviewer_id"],
            assigned_at=_parse_dt(row["assigned_at"]),
            completed_at=_parse_dt(row["completed_at"]),
            session_notes=row["session_notes"],
        )

    # -------------------------------------------------------------------------
    # Review items
    # -------------------------------------------------------------------------

    def save_review_item(self, item: ReviewItem) -> ReviewItem:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO review_items (
                    review_item_id,
                    review_session_id,
                    feedback_id,
                    item_status,
                    current_decision,
                    decision_reason,
                    reviewed_payload_json,
                    reviewed_by,
                    reviewed_at,
                    requires_followup,
                    learning_eligible
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.review_item_id,
                    item.review_session_id,
                    item.feedback_id,
                    item.item_status.value,
                    item.current_decision.value if item.current_decision else None,
                    item.decision_reason,
                    json.dumps(item.reviewed_payload, sort_keys=True) if item.reviewed_payload is not None else None,
                    item.reviewed_by,
                    _dt(item.reviewed_at),
                    1 if item.requires_followup else 0,
                    1 if item.learning_eligible else 0,
                ),
            )
            conn.commit()

        return item

    def get_review_item(self, review_item_id: str) -> Optional[ReviewItem]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    review_item_id,
                    review_session_id,
                    feedback_id,
                    item_status,
                    current_decision,
                    decision_reason,
                    reviewed_payload_json,
                    reviewed_by,
                    reviewed_at,
                    requires_followup,
                    learning_eligible
                FROM review_items
                WHERE review_item_id = ?
                """,
                (review_item_id,),
            ).fetchone()

        if row is None:
            return None

        return ReviewItem(
            review_item_id=row["review_item_id"],
            review_session_id=row["review_session_id"],
            feedback_id=row["feedback_id"],
            item_status=ReviewItemStatus(row["item_status"]),
            current_decision=DecisionType(row["current_decision"]) if row["current_decision"] else None,
            decision_reason=row["decision_reason"],
            reviewed_payload=json.loads(row["reviewed_payload_json"]) if row["reviewed_payload_json"] else None,
            reviewed_by=row["reviewed_by"],
            reviewed_at=_parse_dt(row["reviewed_at"]),
            requires_followup=bool(row["requires_followup"]),
            learning_eligible=bool(row["learning_eligible"]),
        )