import os

from fastapi.testclient import TestClient

from invomatch.main import create_app


def _build_client(tmp_path):
    previous_audit_db_path = os.environ.get("INVOMATCH_AUDIT_EVENT_DB_PATH")
    previous_startup_repair = os.environ.get("INVOMATCH_STARTUP_REPAIR_ENABLED")
    os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = str(tmp_path / "audit_events.sqlite3")
    os.environ["INVOMATCH_STARTUP_REPAIR_ENABLED"] = "false"

    try:
        app = create_app(
            run_store_backend="sqlite",
            run_store_path=tmp_path / "runs.sqlite3",
            review_store_backend="sqlite",
            review_store_path=tmp_path / "reviews.sqlite3",
            export_base_dir=tmp_path / "exports",
        )
        client = TestClient(app)
        return client, app
    finally:
        if previous_audit_db_path is None:
            os.environ.pop("INVOMATCH_AUDIT_EVENT_DB_PATH", None)
        else:
            os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = previous_audit_db_path

        if previous_startup_repair is None:
            os.environ.pop("INVOMATCH_STARTUP_REPAIR_ENABLED", None)
        else:
            os.environ["INVOMATCH_STARTUP_REPAIR_ENABLED"] = previous_startup_repair


def test_audit_api_filters_by_user_and_event_type(tmp_path) -> None:
    client, app = _build_client(tmp_path)

    audit_service = app.state.security_audit_service

    principal = app.state.authentication_service.authenticate_authorization_header(
        "Bearer admin-token"
    ).principal
    assert principal is not None

    audit_service.record(
        event_type="authentication_success",
        principal=principal,
        request_path="/api/reconciliation/runs",
        request_method="GET",
        outcome="allowed",
        metadata={"source": "test"},
    )
    audit_service.record(
        event_type="authorization_denied",
        principal=principal,
        request_path="/api/reconciliation/runs",
        request_method="POST",
        outcome="denied",
        reason="missing_permission",
        metadata={"source": "test"},
    )

    response = client.get(
        "/api/audit/events",
        params={"user_id": "admin-1", "event_type": "authorization_denied"},
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["events"]) == 1
    assert payload["events"][0]["event_type"] == "authorization_denied"
    assert payload["events"][0]["user_id"] == "admin-1"

def test_audit_api_does_not_return_events_from_other_tenants(tmp_path) -> None:
    client, app = _build_client(tmp_path)

    audit_service = app.state.security_audit_service

    principal = app.state.authentication_service.authenticate_authorization_header(
        "Bearer admin-token"
    ).principal
    assert principal is not None
    assert principal.tenant_id == "tenant-demo"

    audit_service.record(
        event_type="authentication_success",
        principal=principal,
        request_path="/api/reconciliation/runs",
        request_method="GET",
        outcome="allowed",
        metadata={"source": "tenant-demo"},
    )

    from invomatch.domain.audit.models import AuditCategory, AuditEvent
    from datetime import UTC, datetime
    from uuid import uuid4

    app.state.audit_event_repository.create(
        AuditEvent(
            event_id=str(uuid4()),
            sequence_id=None,
            tenant_id="tenant-b",
            occurred_at=datetime.now(UTC),
            recorded_at=datetime.now(UTC),
            event_type="authentication_success",
            category=AuditCategory.SECURITY,
            user_id="admin-1",
            outcome="allowed",
            metadata={"source": "tenant-b"},
        )
    )

    response = client.get(
        "/api/audit/events",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    returned_sources = {
        event["metadata"].get("source")
        for event in payload["events"]
        if event.get("metadata")
    }

    assert "tenant-demo" in returned_sources
    assert "tenant-b" not in returned_sources