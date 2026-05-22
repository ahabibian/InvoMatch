from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from invomatch.api.review_cases import (
 get_reconciliation_run_review,
 list_review_queue,
)
from invomatch.domain.review.models import FeedbackRecord
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.security import (
    AuthenticationService,
    AuthorizationService,
    InMemorySecurityAuditService,
    StaticTokenProvider,
)


def _request_with_review_store(
    review_store: InMemoryReviewStore,
    authorization: str | None = "Bearer viewer-token",
) -> SimpleNamespace:
    token_provider = StaticTokenProvider(
        '[{"token":"viewer-token","user_id":"viewer-1","username":"viewer","role":"viewer","status":"active"}]'
    )
    authentication_service = AuthenticationService(token_provider=token_provider)
    authorization_service = AuthorizationService()
    security_audit_service = InMemorySecurityAuditService()

    app = SimpleNamespace(
        state=SimpleNamespace(
            review_store=review_store,
            security_settings=SimpleNamespace(
                auth_enabled=True,
                security_audit_enabled=True,
            ),
            authentication_service=authentication_service,
            authorization_service=authorization_service,
            security_audit_service=security_audit_service,
        )
    )
    headers = {}
    if authorization is not None:
        headers["Authorization"] = authorization

    return SimpleNamespace(
        app=app,
        headers=headers,
        method="GET",
        url=SimpleNamespace(path="/api/reconciliation/runs/run-123/review"),
    )


def test_get_reconciliation_run_review_returns_401_without_auth():
    review_store = InMemoryReviewStore()
    request = _request_with_review_store(review_store, authorization=None)

    with pytest.raises(HTTPException) as exc_info:
        get_reconciliation_run_review("missing-run", request=request)

    assert exc_info.value.status_code == 401


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


def test_list_review_queue_returns_401_without_auth():
    review_store = InMemoryReviewStore()
    request = _request_with_review_store(review_store, authorization=None)

    with pytest.raises(HTTPException) as exc_info:
        list_review_queue(request=request)

    assert exc_info.value.status_code == 401


def test_list_review_queue_returns_empty_rows_when_no_active_cases_exist():
    review_store = InMemoryReviewStore()
    request = _request_with_review_store(review_store)

    response = list_review_queue(request=request)

    assert response == []


def test_list_review_queue_returns_backend_owned_display_only_rows():
    review_store = InMemoryReviewStore()
    review_service = ReviewService()

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="feedback-queue-1",
        run_id="run-queue-1",
        source_type="system",
        source_reference="test-source",
        feedback_type="match_feedback",
        raw_payload={
            "reason_code": "ambiguous_match",
            "match_id": "match-queue-1",
            "invoice_id": "INV-SHOULD-NOT-LEAK_AS_REQUIRED_FIELD",
            "payment_id": "PAY-SHOULD-NOT-LEAK_AS_REQUIRED_FIELD",
            "confidence": 0.42,
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
    response = list_review_queue(request=request)

    assert len(response) == 1

    row = response[0]
    assert row.case_id == review_item.review_item_id
    assert row.run_id == "run-queue-1"
    assert row.status == "open"
    assert row.reason_code == "ambiguous_match"
    assert row.match_id == "match-queue-1"
    assert row.priority is None

    row_payload = row.model_dump()
    assert "reviewed_payload" not in row_payload
    assert "reviewed_by" not in row_payload
    assert "evidence" not in row_payload
    assert "confidence" not in row_payload
    assert "export_readiness" not in row_payload


def test_list_review_queue_excludes_terminal_review_items():
    review_store = InMemoryReviewStore()
    review_service = ReviewService()

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="feedback-queue-closed",
        run_id="run-queue-closed",
        source_type="system",
        source_reference="test-source",
        feedback_type="match_feedback",
        raw_payload={
            "reason_code": "ambiguous_match",
            "match_id": "match-closed",
        },
        submitted_by="system",
    )
    review_store.save_feedback(feedback)

    review_item, audit_event = review_service.create_review_item(
        feedback=feedback,
        review_session=session,
    )
    review_item.close()
    review_store.save_review_item(review_item)
    review_store.save_audit_event(audit_event)

    request = _request_with_review_store(review_store)
    response = list_review_queue(request=request)

    assert response == []
