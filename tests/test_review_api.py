from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from invomatch.api.review_cases import get_reconciliation_run_review
from invomatch.domain.review.models import FeedbackRecord
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore


def _request_with_review_store(review_store: InMemoryReviewStore) -> SimpleNamespace:
    app = SimpleNamespace(state=SimpleNamespace(review_store=review_store))
    return SimpleNamespace(app=app)


def test_get_reconciliation_run_review_returns_404_when_no_case_exists():
    review_store = InMemoryReviewStore()
    request = _request_with_review_store(review_store)

    with pytest.raises(HTTPException) as exc_info:
        get_reconciliation_run_review("missing-run", request=request)

    assert exc_info.value.status_code == 404


def test_get_reconciliation_run_review_returns_product_case():
    review_store = InMemoryReviewStore()
    review_service = ReviewService()

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="feedback-1",
        run_id="run-123",
        source_type="system",
        source_reference="test-source",
        feedback_type="match_feedback",
        raw_payload={
            "reason_code": "ambiguous_match",
            "match_id": "match-789",
        },
        submitted_by="system",
    )
    review_store.save_feedback(feedback)

    review_item, audit_event = review_service.create_review_item(
        feedback=feedback,
        review_session=session,
    )
    review_store.save_review_item(review_item)
    review_store.save_audit_event(audit_event)

    request = _request_with_review_store(review_store)
    response = get_reconciliation_run_review("run-123", request=request)

    assert response.case_id == review_item.review_item_id
    assert response.run_id == "run-123"
    assert response.status == "open"
    assert response.reason_code == "ambiguous_match"
    assert response.match_id == "match-789"
    assert response.explanation == []
    assert not hasattr(response, "reviewed_payload")
    assert not hasattr(response, "reviewed_by")