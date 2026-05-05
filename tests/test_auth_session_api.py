from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

from invomatch.main import create_app


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _seed_tokens_json() -> str:
    return """
    [
      {
        "token": "viewer-session-token",
        "user_id": "viewer-1",
        "username": "viewer",
        "role": "viewer",
        "status": "active",
        "tenant_id": "tenant-demo",
        "expires_at": "2099-01-01T00:00:00+00:00"
      },
      {
        "token": "operator-session-token",
        "user_id": "operator-1",
        "username": "operator",
        "role": "operator",
        "status": "active",
        "tenant_id": "tenant-demo",
        "expires_at": "2099-01-01T00:00:00+00:00"
      },
      {
        "token": "admin-session-token",
        "user_id": "admin-1",
        "username": "admin",
        "role": "admin",
        "status": "active",
        "tenant_id": "tenant-demo",
        "expires_at": "2099-01-01T00:00:00+00:00"
      },
      {
        "token": "expired-session-token",
        "user_id": "expired-1",
        "username": "expired",
        "role": "operator",
        "status": "active",
        "tenant_id": "tenant-demo",
        "expires_at": "2000-01-01T00:00:00+00:00"
      },
      {
        "token": "revoked-session-token",
        "user_id": "revoked-1",
        "username": "revoked",
        "role": "operator",
        "status": "active",
        "tenant_id": "tenant-demo",
        "expires_at": "2099-01-01T00:00:00+00:00",
        "revoked": true
      },
      {
        "token": "inactive-session-token",
        "user_id": "inactive-1",
        "username": "inactive",
        "role": "operator",
        "status": "inactive",
        "tenant_id": "tenant-demo",
        "expires_at": "2099-01-01T00:00:00+00:00"
      }
    ]
    """


def _client(tmp_path: Path) -> TestClient:
    os.environ["INVOMATCH_SECURITY_SEED_TOKENS_JSON"] = _seed_tokens_json()
    os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = str(tmp_path / "audit.sqlite3")

    app = create_app(
        run_store_path=tmp_path / "runs.sqlite3",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    return TestClient(app)


def test_auth_session_requires_authentication(tmp_path: Path) -> None:
    previous_seed_tokens = os.environ.get("INVOMATCH_SECURITY_SEED_TOKENS_JSON")
    previous_audit_db_path = os.environ.get("INVOMATCH_AUDIT_EVENT_DB_PATH")

    try:
        client = _client(tmp_path)

        response = client.get("/api/auth/session")

        assert response.status_code == 401
    finally:
        if previous_seed_tokens is None:
            os.environ.pop("INVOMATCH_SECURITY_SEED_TOKENS_JSON", None)
        else:
            os.environ["INVOMATCH_SECURITY_SEED_TOKENS_JSON"] = previous_seed_tokens

        if previous_audit_db_path is None:
            os.environ.pop("INVOMATCH_AUDIT_EVENT_DB_PATH", None)
        else:
            os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = previous_audit_db_path


def test_auth_session_returns_viewer_principal_and_permissions(tmp_path: Path) -> None:
    previous_seed_tokens = os.environ.get("INVOMATCH_SECURITY_SEED_TOKENS_JSON")
    previous_audit_db_path = os.environ.get("INVOMATCH_AUDIT_EVENT_DB_PATH")

    try:
        client = _client(tmp_path)

        response = client.get(
            "/api/auth/session",
            headers=_auth_headers("viewer-session-token"),
        )

        assert response.status_code == 200
        body = response.json()

        assert body["user"] == {
            "user_id": "viewer-1",
            "username": "viewer",
            "role": "viewer",
            "status": "active",
            "tenant_id": "tenant-demo",
            "auth_source": "internal_token",
        }
        assert body["permissions"] == [
            "input.view",
            "runs.list",
            "runs.read",
            "runs.read_view",
            "runs.read_review",
            "artifacts.list",
            "artifacts.read_metadata",
        ]
        assert "operations.view_metrics" not in body["permissions"]
    finally:
        if previous_seed_tokens is None:
            os.environ.pop("INVOMATCH_SECURITY_SEED_TOKENS_JSON", None)
        else:
            os.environ["INVOMATCH_SECURITY_SEED_TOKENS_JSON"] = previous_seed_tokens

        if previous_audit_db_path is None:
            os.environ.pop("INVOMATCH_AUDIT_EVENT_DB_PATH", None)
        else:
            os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = previous_audit_db_path


def test_auth_session_returns_operator_principal_and_permissions(tmp_path: Path) -> None:
    previous_seed_tokens = os.environ.get("INVOMATCH_SECURITY_SEED_TOKENS_JSON")
    previous_audit_db_path = os.environ.get("INVOMATCH_AUDIT_EVENT_DB_PATH")

    try:
        client = _client(tmp_path)

        response = client.get(
            "/api/auth/session",
            headers=_auth_headers("operator-session-token"),
        )

        assert response.status_code == 200
        body = response.json()

        assert body["user"]["user_id"] == "operator-1"
        assert body["user"]["username"] == "operator"
        assert body["user"]["role"] == "operator"
        assert body["user"]["status"] == "active"
        assert body["user"]["tenant_id"] == "tenant-demo"
        assert body["user"]["auth_source"] == "internal_token"

        assert body["permissions"] == [
            "input.submit",
            "input.view",
            "runs.create",
            "runs.create_from_ingestion",
            "runs.list",
            "runs.read",
            "runs.read_view",
            "runs.read_review",
            "actions.resolve_review",
            "actions.export_run",
            "exports.download_direct",
            "artifacts.list",
            "artifacts.read_metadata",
            "artifacts.download",
        ]
        assert "operations.view_metrics" not in body["permissions"]
    finally:
        if previous_seed_tokens is None:
            os.environ.pop("INVOMATCH_SECURITY_SEED_TOKENS_JSON", None)
        else:
            os.environ["INVOMATCH_SECURITY_SEED_TOKENS_JSON"] = previous_seed_tokens

        if previous_audit_db_path is None:
            os.environ.pop("INVOMATCH_AUDIT_EVENT_DB_PATH", None)
        else:
            os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = previous_audit_db_path


def test_auth_session_returns_admin_principal_and_operations_permission(tmp_path: Path) -> None:
    previous_seed_tokens = os.environ.get("INVOMATCH_SECURITY_SEED_TOKENS_JSON")
    previous_audit_db_path = os.environ.get("INVOMATCH_AUDIT_EVENT_DB_PATH")

    try:
        client = _client(tmp_path)

        response = client.get(
            "/api/auth/session",
            headers=_auth_headers("admin-session-token"),
        )

        assert response.status_code == 200
        body = response.json()

        assert body["user"] == {
            "user_id": "admin-1",
            "username": "admin",
            "role": "admin",
            "status": "active",
            "tenant_id": "tenant-demo",
            "auth_source": "internal_token",
        }
        assert body["permissions"] == [
            "input.submit",
            "input.view",
            "runs.create",
            "runs.create_from_ingestion",
            "runs.list",
            "runs.read",
            "runs.read_view",
            "runs.read_review",
            "actions.resolve_review",
            "actions.export_run",
            "exports.download_direct",
            "artifacts.list",
            "artifacts.read_metadata",
            "artifacts.download",
            "operations.view_metrics",
            "operations.execute_recovery",
            "operations.execute_startup_repair",
            "operations.manage_admin_surface",
        ]
    finally:
        if previous_seed_tokens is None:
            os.environ.pop("INVOMATCH_SECURITY_SEED_TOKENS_JSON", None)
        else:
            os.environ["INVOMATCH_SECURITY_SEED_TOKENS_JSON"] = previous_seed_tokens

        if previous_audit_db_path is None:
            os.environ.pop("INVOMATCH_AUDIT_EVENT_DB_PATH", None)
        else:
            os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = previous_audit_db_path


def test_auth_session_rejects_expired_and_revoked_tokens(tmp_path: Path) -> None:
    previous_seed_tokens = os.environ.get("INVOMATCH_SECURITY_SEED_TOKENS_JSON")
    previous_audit_db_path = os.environ.get("INVOMATCH_AUDIT_EVENT_DB_PATH")

    try:
        client = _client(tmp_path)

        expired = client.get(
            "/api/auth/session",
            headers=_auth_headers("expired-session-token"),
        )
        revoked = client.get(
            "/api/auth/session",
            headers=_auth_headers("revoked-session-token"),
        )

        assert expired.status_code == 401
        assert expired.json()["detail"] == "Token expired"

        assert revoked.status_code == 401
        assert revoked.json()["detail"] == "Token revoked"
    finally:
        if previous_seed_tokens is None:
            os.environ.pop("INVOMATCH_SECURITY_SEED_TOKENS_JSON", None)
        else:
            os.environ["INVOMATCH_SECURITY_SEED_TOKENS_JSON"] = previous_seed_tokens

        if previous_audit_db_path is None:
            os.environ.pop("INVOMATCH_AUDIT_EVENT_DB_PATH", None)
        else:
            os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = previous_audit_db_path


def test_auth_session_rejects_inactive_user(tmp_path: Path) -> None:
    previous_seed_tokens = os.environ.get("INVOMATCH_SECURITY_SEED_TOKENS_JSON")
    previous_audit_db_path = os.environ.get("INVOMATCH_AUDIT_EVENT_DB_PATH")

    try:
        client = _client(tmp_path)

        response = client.get(
            "/api/auth/session",
            headers=_auth_headers("inactive-session-token"),
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "User is inactive"
    finally:
        if previous_seed_tokens is None:
            os.environ.pop("INVOMATCH_SECURITY_SEED_TOKENS_JSON", None)
        else:
            os.environ["INVOMATCH_SECURITY_SEED_TOKENS_JSON"] = previous_seed_tokens

        if previous_audit_db_path is None:
            os.environ.pop("INVOMATCH_AUDIT_EVENT_DB_PATH", None)
        else:
            os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = previous_audit_db_path