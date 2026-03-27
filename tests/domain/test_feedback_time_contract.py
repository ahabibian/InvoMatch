from datetime import datetime, UTC

import pytest
from pydantic import ValidationError

from invomatch.domain.feedback import FeedbackRecord


def test_feedback_record_accepts_timezone_aware_datetime() -> None:
    record = FeedbackRecord(
        feedback_id="fb-1",
        run_id="run-1",
        match_id="match-1",
        original_status="matched",
        corrected_status="unmatched",
        selected_payment_id=None,
        action="reject_match",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert record.created_at.tzinfo is not None


def test_feedback_record_rejects_naive_datetime() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        FeedbackRecord(
            feedback_id="fb-1",
            run_id="run-1",
            match_id="match-1",
            original_status="matched",
            corrected_status="unmatched",
            selected_payment_id=None,
            action="reject_match",
            created_at=datetime(2026, 1, 1),
        )