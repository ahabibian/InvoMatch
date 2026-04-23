import os
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from invomatch.domain.audit.models import AuditEventQuery
from invomatch.domain.models import ReconciliationRun
from invomatch.main import create_app


class StubRepairResult:
    def __init__(self, repaired_status: str, reason: str) -> None:
        self.repaired_status = repaired_status
        self.reason = reason


class StubRepairService:
    def repair_run(self, run_id: str) -> StubRepairResult:
        return StubRepairResult(
            repaired_status="review_required",
            reason="status_repaired_from_processing",
        )


class StubRunStore:
    def __init__(self, run) -> None:
        self._run = run

    def list_runs(self, limit=100000, offset=0):
        return [self._run], 1


class StubReviewStore:
    pass


def _build_isolated_app(tmp_path):
    previous_audit_db_path = os.environ.get("INVOMATCH_AUDIT_EVENT_DB_PATH")
    previous_startup_repair = os.environ.get("INVOMATCH_STARTUP_REPAIR_ENABLED")

    audit_db_path = tmp_path / "audit_events.sqlite3"
    os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = str(audit_db_path)
    os.environ["INVOMATCH_STARTUP_REPAIR_ENABLED"] = "false"

    try:
        app = create_app(
            run_store_backend="sqlite",
            run_store_path=tmp_path / "runs.sqlite3",
            review_store_backend="sqlite",
            review_store_path=tmp_path / "reviews.sqlite3",
            export_base_dir=tmp_path / "exports",
        )
        return app, audit_db_path
    finally:
        if previous_audit_db_path is None:
            os.environ.pop("INVOMATCH_AUDIT_EVENT_DB_PATH", None)
        else:
            os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = previous_audit_db_path

        if previous_startup_repair is None:
            os.environ.pop("INVOMATCH_STARTUP_REPAIR_ENABLED", None)
        else:
            os.environ["INVOMATCH_STARTUP_REPAIR_ENABLED"] = previous_startup_repair


def test_scenario_9_audit_persistence_integrity(tmp_path) -> None:
    app, audit_db_path = _build_isolated_app(tmp_path)
    client = TestClient(app)

    principal = app.state.authentication_service.authenticate_authorization_header(
        "Bearer admin-token"
    ).principal
    assert principal is not None

    app.state.security_audit_service.record(
        event_type="authorization_denied",
        principal=principal,
        request_path="/api/reconciliation/runs",
        request_method="POST",
        capability="runs.create",
        outcome="denied",
        reason="missing_permission",
        metadata={"source": "scenario_9"},
    )

    created_at = datetime.now(UTC) - timedelta(minutes=5)
    run = ReconciliationRun(
        run_id="run-s9",
        status="processing",
        created_at=created_at,
        updated_at=created_at,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        invoices=[],
        payments=[],
        matched_pairs=[],
        unmatched_invoices=[],
        unmatched_payments=[],
        suggested_pairs=[],
        version=0,
        attempt_count=0,
    )

    coordinator = app.state.startup_repair_coordinator.__class__(
        run_store=StubRunStore(run),
        review_store=StubReviewStore(),
        repair_service=StubRepairService(),
        metrics_service=app.state.operational_metrics_service,
        audit_service=app.state.operational_audit_service,
        now_provider=lambda: datetime.now(UTC),
    )

    result = coordinator.run_startup_scan()
    assert result.total_runs_scanned == 1

    persisted_events = app.state.audit_event_repository.list_events(
        AuditEventQuery(limit=20, offset=0)
    )

    assert len(persisted_events) == 2
    assert persisted_events[0].sequence_id is not None
    assert persisted_events[1].sequence_id is not None
    assert persisted_events[0].sequence_id < persisted_events[1].sequence_id

    security_events = app.state.audit_event_repository.list_events(
        AuditEventQuery(user_id="admin-1", event_type="authorization_denied", limit=20, offset=0)
    )
    assert len(security_events) == 1
    assert security_events[0].category.value == "security"

    run_events = app.state.audit_event_repository.list_events(
        AuditEventQuery(run_id="run-s9", limit=20, offset=0)
    )
    assert len(run_events) == 1
    assert run_events[0].event_type == "startup_repair_applied"
    assert run_events[0].category.value == "operational"

    response = client.get(
        "/api/audit/events",
        params={"run_id": "run-s9"},
        headers={"Authorization": "Bearer admin-token"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["events"]) == 1
    assert payload["events"][0]["event_type"] == "startup_repair_applied"

    app_reloaded, _ = _build_isolated_app(tmp_path)
    reloaded_events = app_reloaded.state.audit_event_repository.list_events(
        AuditEventQuery(limit=20, offset=0)
    )

    assert len(reloaded_events) >= 2
    assert any(
        event.event_type == "authorization_denied" and event.user_id == "admin-1"
        for event in reloaded_events
    )
    assert any(
        event.event_type == "startup_repair_applied" and event.run_id == "run-s9"
        for event in reloaded_events
    )
    assert audit_db_path.exists()