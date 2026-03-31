from __future__ import annotations

from types import SimpleNamespace

from invomatch.api.actions import post_reconciliation_run_action
from invomatch.api.product_models.action import ProductActionRequest
from invomatch.services.action_service import ActionService


def _request_with_action_service(action_service: ActionService) -> SimpleNamespace:
    app = SimpleNamespace(state=SimpleNamespace(action_service=action_service))
    return SimpleNamespace(app=app)


def test_post_reconciliation_run_action_accepts_resolve_review():
    request = _request_with_action_service(ActionService())

    response = post_reconciliation_run_action(
        "run-123",
        ProductActionRequest(
            action_type="resolve_review",
            target_id="case-1",
            payload={
                "decision": "APPROVE",
                "reviewer_id": "reviewer-1",
                "feedback_id": "feedback-1",
                "review_session_id": "review-session-1",
                "review_item_id": "review-item-1",
                "source_type": "manual_review",
                "source_reference": "case-1",
                "feedback_type": "review_resolution",
                "raw_payload": {"matched": False},
                "submitted_by": "system",
                "feedback_status": "UNDER_REVIEW",
                "review_item_status": "IN_REVIEW",
            },
            note="resolved by reviewer",
        ),
        request=request,
    )

    assert response.run_id == "run-123"
    assert response.action_type == "resolve_review"
    assert response.accepted is True
    assert response.status == "accepted"


def test_post_reconciliation_run_action_accepts_export_run():
    request = _request_with_action_service(ActionService())

    response = post_reconciliation_run_action(
        "run-123",
        ProductActionRequest(
            action_type="export_run",
            target_id=None,
            payload={"format": "json"},
            note="export requested",
        ),
        request=request,
    )

    assert response.run_id == "run-123"
    assert response.action_type == "export_run"
    assert response.accepted is True
    assert response.status == "accepted"


def test_post_reconciliation_run_action_rejects_invalid_resolve_review_payload():
    request = _request_with_action_service(ActionService())

    response = post_reconciliation_run_action(
        "run-123",
        ProductActionRequest(
            action_type="resolve_review",
            target_id="case-1",
            payload={},
            note="invalid request",
        ),
        request=request,
    )

    assert response.run_id == "run-123"
    assert response.action_type == "resolve_review"
    assert response.accepted is False
    assert response.status == "invalid_request"