from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

from invomatch.main import create_app
from invomatch.domain.audit.models import AuditCategory, AuditEventQuery


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_scenario_11_security_boundary_enforcement(tmp_path: Path) -> None:
    previous_seed_tokens = os.environ.get("INVOMATCH_SECURITY_SEED_TOKENS_JSON")
    previous_audit_db_path = os.environ.get("INVOMATCH_AUDIT_EVENT_DB_PATH")

    audit_db_path = tmp_path / "audit.sqlite3"

    os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = str(audit_db_path)
    os.environ["INVOMATCH_SECURITY_SEED_TOKENS_JSON"] = """
    [
      {
        "token": "operator-active-token",
        "user_id": "operator-a",
        "username": "operator-a",
        "role": "operator",
        "status": "active",
        "tenant_id": "tenant-a",
        "expires_at": "2099-01-01T00:00:00+00:00"
      },
      {
        "token": "viewer-active-token",
        "user_id": "viewer-a",
        "username": "viewer-a",
        "role": "viewer",
        "status": "active",
        "tenant_id": "tenant-a",
        "expires_at": "2099-01-01T00:00:00+00:00"
      },
      {
        "token": "admin-active-token",
        "user_id": "admin-a",
        "username": "admin-a",
        "role": "admin",
        "status": "active",
        "tenant_id": "tenant-a",
        "expires_at": "2099-01-01T00:00:00+00:00"
      },
      {
        "token": "expired-token",
        "user_id": "expired-user",
        "username": "expired-user",
        "role": "operator",
        "status": "active",
        "tenant_id": "tenant-a",
        "expires_at": "2000-01-01T00:00:00+00:00"
      },
      {
        "token": "revoked-token",
        "user_id": "revoked-user",
        "username": "revoked-user",
        "role": "operator",
        "status": "active",
        "tenant_id": "tenant-a",
        "expires_at": "2099-01-01T00:00:00+00:00",
        "revoked": true
      },
      {
        "token": "operator-tenant-b-token",
        "user_id": "operator-b",
        "username": "operator-b",
        "role": "operator",
        "status": "active",
        "tenant_id": "tenant-b",
        "expires_at": "2099-01-01T00:00:00+00:00"
      }
    ]
    """

    try:
        app = create_app(
            run_store_path=tmp_path / "runs.sqlite3",
            review_store_path=tmp_path / "reviews.sqlite3",
            export_base_dir=tmp_path / "exports",
        )
        client = TestClient(app)

        payload = {
            "invoices": [
                {
                    "id": "inv-sec-001",
                    "date": "2026-04-30",
                    "amount": "100.00",
                    "currency": "USD",
                    "reference": "SEC-001",
                }
            ],
            "payments": [
                {
                    "id": "pay-sec-001",
                    "date": "2026-04-30",
                    "amount": "100.00",
                    "currency": "USD",
                    "reference": "SEC-001",
                }
            ],
        }

        missing_token = client.post("/api/reconciliation/input/json", json=payload)
        assert missing_token.status_code == 401

        expired_token = client.post(
            "/api/reconciliation/input/json",
            json=payload,
            headers=_auth_headers("expired-token"),
        )
        assert expired_token.status_code == 401
        assert expired_token.json()["detail"] == "Token expired"

        revoked_token = client.post(
            "/api/reconciliation/input/json",
            json=payload,
            headers=_auth_headers("revoked-token"),
        )
        assert revoked_token.status_code == 401
        assert revoked_token.json()["detail"] == "Token revoked"

        viewer_action_attempt = client.post(
            "/api/reconciliation/runs/run-sec-001/actions",
            json={
                "action_type": "export_run",
                "target_id": "run-sec-001",
                "payload": {"format": "json"},
                "note": "viewer must not export",
            },
            headers=_auth_headers("viewer-active-token"),
        )
        assert viewer_action_attempt.status_code == 403

        operator_submit = client.post(
            "/api/reconciliation/input/json",
            json=payload,
            headers=_auth_headers("operator-active-token"),
        )
        assert operator_submit.status_code in {200, 201, 202}

        tenant_b_runs = client.get(
            "/api/reconciliation/runs",
            headers=_auth_headers("operator-tenant-b-token"),
        )
        assert tenant_b_runs.status_code == 200
        assert tenant_b_runs.json()["items"] == []

        admin_audit_query = client.get(
            "/api/audit/events",
            headers=_auth_headers("admin-active-token"),
        )
        assert admin_audit_query.status_code == 200

        viewer_audit_query = client.get(
            "/api/audit/events",
            headers=_auth_headers("viewer-active-token"),
        )
        assert viewer_audit_query.status_code == 403

        security_events = app.state.audit_event_repository.list_events(
            AuditEventQuery(
                tenant_id="security-boundary",
                category=AuditCategory.SECURITY,
                limit=100,
                offset=0,
            )
        )

        security_event_types = {event.event_type for event in security_events}
        security_reasons = {event.reason_code for event in security_events}

        assert "authentication_failure" in security_event_types
        assert "missing_authorization_header" in security_reasons
        assert "token_expired" in security_reasons
        assert "token_revoked" in security_reasons

        tenant_a_security_events = app.state.audit_event_repository.list_events(
            AuditEventQuery(
                tenant_id="tenant-a",
                category=AuditCategory.SECURITY,
                limit=100,
                offset=0,
            )
        )
        tenant_a_event_types = {event.event_type for event in tenant_a_security_events}

        assert "authorization_denied" in tenant_a_event_types
        assert "privileged_action_executed" in tenant_a_event_types

    finally:
        if previous_seed_tokens is None:
            os.environ.pop("INVOMATCH_SECURITY_SEED_TOKENS_JSON", None)
        else:
            os.environ["INVOMATCH_SECURITY_SEED_TOKENS_JSON"] = previous_seed_tokens

        if previous_audit_db_path is None:
            os.environ.pop("INVOMATCH_AUDIT_EVENT_DB_PATH", None)
        else:
            os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = previous_audit_db_path