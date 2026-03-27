from datetime import datetime, UTC
created_at=datetime.now(UTC)

from pathlib import Path

from invomatch.domain.feedback import FeedbackRecord
from invomatch.services.sqlite_feedback_store import SqliteFeedbackStore


def test_create_and_query_feedback(tmp_path: Path):
    db = tmp_path / "feedback.sqlite"
    store = SqliteFeedbackStore(db)

    record = FeedbackRecord(
        feedback_id="fb-1",
        run_id="run-1",
        match_id="match-1",
        original_status="matched",
        corrected_status="unmatched",
        selected_payment_id=None,
        action="reject_match",
        created_at=datetime.now(UTC),
    )

    store.create_feedback(record)

    by_run = store.list_by_run("run-1")
    assert len(by_run) == 1

    by_match = store.list_by_match("match-1")
    assert len(by_match) == 1