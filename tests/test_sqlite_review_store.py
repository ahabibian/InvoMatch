from __future__ import annotations

import sqlite3
from pathlib import Path

from invomatch.domain.review.models import (
    DecisionType,
    ReviewItem,
    ReviewItemStatus,
)
from invomatch.services.sqlite_review_store import SqliteReviewStore


def test_sqlite_store_creates_db_and_table(tmp_path: Path) -> None:
    db_path = tmp_path / "review.db"

    SqliteReviewStore(db_path)

    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='review_items'"
    )
    row = cursor.fetchone()

    assert row is not None
    assert row[0] == "review_items"

    conn.close()


def test_save_and_get_review_item_round_trip(tmp_path: Path) -> None:
    db_path = tmp_path / "review.db"
    store = SqliteReviewStore(db_path)

    item = ReviewItem(
        review_item_id="ri_001",
        review_session_id="rs_001",
        feedback_id="fb_001",
        item_status=ReviewItemStatus.MODIFIED,
        current_decision=DecisionType.MODIFY,
        decision_reason="Adjusted during sqlite persistence test",
        reviewed_payload={
            "invoice_id": "inv_123",
            "payment_id": "pay_456",
            "match_confidence": 0.93,
        },
        reviewed_by="reviewer_sqlite",
        requires_followup=False,
        learning_eligible=True,
    )

    store.save_review_item(item)
    loaded = store.get_review_item("ri_001")

    assert loaded is not None
    assert loaded.review_item_id == item.review_item_id
    assert loaded.review_session_id == item.review_session_id
    assert loaded.feedback_id == item.feedback_id
    assert loaded.item_status == ReviewItemStatus.MODIFIED
    assert loaded.current_decision == DecisionType.MODIFY
    assert loaded.decision_reason == item.decision_reason
    assert loaded.reviewed_payload == item.reviewed_payload
    assert loaded.reviewed_by == item.reviewed_by
    assert loaded.requires_followup is False
    assert loaded.learning_eligible is True