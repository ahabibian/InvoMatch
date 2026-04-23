from __future__ import annotations

from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
from types import SimpleNamespace

from fastapi import HTTPException
import pytest

from invomatch.api.actions import post_reconciliation_run_action
from invomatch.api.product_models.action import ProductActionRequest
from invomatch.services.action_service import ActionService
from invomatch.services.security import (
    AuthenticationService,
    AuthorizationService,
    InMemorySecurityAuditService,
    StaticTokenProvider,
)


def _request_with_action_service(
    action_service,
    authorization: str | None = "Bearer operator-token",
):
    token_provider = StaticTokenProvider(
        '[{"token":"viewer-token","user_id":"viewer-1","username":"viewer","role":"viewer","status":"active"},{"token":"operator-token","user_id":"operator-1","username":"operator","role":"operator","status":"active"},{"token":"admin-token","user_id":"admin-1","username":"admin","role":"admin","status":"active"}]'
    )
    authentication_service = AuthenticationService(token_provider=token_provider)
    authorization_service = AuthorizationService()
    security_audit_service = InMemorySecurityAuditService()

    app = SimpleNamespace(
        state=SimpleNamespace(
            action_service=action_service,
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
        method="POST",
        url=SimpleNamespace(path="/api/reconciliation/runs/run-123/actions"),
    )


def test_post_reconciliation_run_action_returns_401_without_auth():
    request = _request_with_action_service(ActionService(), authorization=None)

    with pytest.raises(HTTPException) as exc_info:
        post_reconciliation_run_action(
            "run-123",
            ProductActionRequest(
                action_type="resolve_review",
                target_id="case-1",
                payload={},
                note="no auth",
            ),
            request=request,
        )

    assert exc_info.value.status_code == 401


def test_post_reconciliation_run_action_returns_403_for_viewer_resolve_review():
    request = _request_with_action_service(ActionService(), authorization="Bearer viewer-token")

    with pytest.raises(HTTPException) as exc_info:
        post_reconciliation_run_action(
            "run-123",
            ProductActionRequest(
                action_type="resolve_review",
                target_id="case-1",
                payload={},
                note="viewer forbidden",
            ),
            request=request,
        )

    assert exc_info.value.status_code == 403


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
    class StubActionService:
        def execute(self, *, run_id: str, request: ProductActionRequest, principal=None):
            return SimpleNamespace(
                run_id=run_id,
                action_type=str(request.action_type),
                accepted=True,
                status="accepted",
                message="Export artifact created.",
            )

    request = _request_with_action_service(StubActionService())

    response = post_reconciliation_run_action(
        "run-export-123",
        ProductActionRequest(
            action_type="export_run",
            target_id=None,
            payload={"format": "json"},
            note="export requested",
        ),
        request=request,
    )

    assert response.run_id == "run-export-123"
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