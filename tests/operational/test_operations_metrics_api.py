from fastapi.testclient import TestClient

from invomatch.main import create_app
from invomatch.services.operational.operational_metrics import (
    InMemoryOperationalMetricsStore,
    OperationalMetricsService,
)
from invomatch.domain.operational.models import (
    OperationalDecision,
    OperationalReasonCode,
)


def _client(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    return TestClient(app)


def test_operations_metrics_requires_authentication(tmp_path):
    client = _client(tmp_path)

    response = client.get("/api/operations/metrics")

    assert response.status_code == 401


def test_operations_metrics_rejects_viewer_role(tmp_path):
    client = _client(tmp_path)

    response = client.get(
        "/api/operations/metrics",
        headers={"Authorization": "Bearer viewer-token"},
    )

    assert response.status_code == 403


def test_operations_metrics_returns_admin_visible_operational_signals(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )

    metrics_service = app.state.operational_metrics_service
    metrics_service.record_recovery_result(
        decision=OperationalDecision.RETRY_TRIGGERED,
        reason_code=OperationalReasonCode.RECOVERABLE_FAILURE,
        action_taken=True,
    )

    client = TestClient(app)

    response = client.get(
        "/api/operations/metrics",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"
    assert "generated_at" in body

    assert body["signals"]["recovery_attempts_total"] == 1
    assert body["signals"]["recovery_action_taken_total"] == 1
    assert body["signals"]["retries_triggered_total"] == 1

    assert body["counters"]["recovery_attempts_total"] == 1
    assert body["decision_counts"]["retry_triggered"] == 1
    assert body["reason_counts"]["recoverable_failure"] == 1


def test_operations_metrics_reports_degraded_when_startup_repair_failed(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )

    metrics_store = InMemoryOperationalMetricsStore()
    metrics_store.increment_counter("startup_repair_failed_total")
    app.state.operational_metrics_service = OperationalMetricsService(metrics_store)

    client = TestClient(app)

    response = client.get(
        "/api/operations/metrics",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "degraded"
    assert body["signals"]["startup_repair_failed_total"] == 1


def test_operations_metrics_reports_500_when_metrics_service_missing(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )

    delattr(app.state, "operational_metrics_service")

    client = TestClient(app)

    response = client.get(
        "/api/operations/metrics",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "operational metrics service is not configured"

def test_operations_health_summary_returns_healthy_for_admin_when_no_counters(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    client = TestClient(app)

    response = client.get(
        "/api/operations/health-summary",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "healthy"
    assert body["recommended_action"] == "none"
    assert body["summary"]["startup_repair"] == "no startup repair issues detected"
    assert body["summary"]["recovery"] == "no recovery activity detected"
    assert body["summary"]["terminal_failures"] == "no terminal failure confirmations detected"
    assert "signals" in body
    assert "generated_at" in body


def test_operations_health_summary_forbids_viewer(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    client = TestClient(app)

    response = client.get(
        "/api/operations/health-summary",
        headers={"Authorization": "Bearer viewer-token"},
    )

    assert response.status_code == 403


def test_operations_health_summary_requires_authentication(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    client = TestClient(app)

    response = client.get("/api/operations/health-summary")

    assert response.status_code == 401


def test_operations_health_summary_reports_degraded_for_startup_repair_failure(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    app.state.operational_metrics_store.increment_counter("startup_repair_failed_total")

    client = TestClient(app)

    response = client.get(
        "/api/operations/health-summary",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "degraded"
    assert body["recommended_action"] == "inspect_startup_repair"
    assert body["signals"]["startup_repair_failed_total"] == 1
    assert body["summary"]["startup_repair"] == (
        "startup repair has unresolved or failed repair outcomes"
    )


def test_operations_health_summary_reports_attention_required_for_terminal_failures(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    app.state.operational_metrics_store.increment_counter(
        "terminal_failures_confirmed_total"
    )

    client = TestClient(app)

    response = client.get(
        "/api/operations/health-summary",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "attention_required"
    assert body["recommended_action"] == "inspect_terminal_failures"
    assert body["signals"]["terminal_failures_confirmed_total"] == 1
    assert body["summary"]["terminal_failures"] == (
        "terminal failures were confirmed and require operator attention"
    )


def test_operations_health_summary_reports_recovery_action_summary(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    app.state.operational_metrics_store.increment_counter("recovery_attempts_total")
    app.state.operational_metrics_store.increment_counter("recovery_action_taken_total")

    client = TestClient(app)

    response = client.get(
        "/api/operations/health-summary",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "healthy"
    assert body["summary"]["recovery"] == "recovery automation has taken action"
    assert body["signals"]["recovery_attempts_total"] == 1
    assert body["signals"]["recovery_action_taken_total"] == 1
def test_operations_metrics_response_shape_is_stable(tmp_path):
    client = _client(tmp_path)

    response = client.get(
        "/api/operations/metrics",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert set(body.keys()) == {
        "status",
        "generated_at",
        "signals",
        "counters",
        "decision_counts",
        "reason_counts",
    }

    assert set(body["signals"].keys()) == {
        "recovery_attempts_total",
        "recovery_action_taken_total",
        "retries_triggered_total",
        "reentries_triggered_total",
        "terminal_failures_confirmed_total",
        "startup_repair_items_total",
        "startup_repairs_applied_total",
        "startup_repair_failed_total",
        "startup_repair_unresolved_total",
        "startup_repair_skipped_total",
    }


def test_operations_health_summary_response_shape_is_stable(tmp_path):
    client = _client(tmp_path)

    response = client.get(
        "/api/operations/health-summary",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert set(body.keys()) == {
        "status",
        "generated_at",
        "summary",
        "signals",
        "recommended_action",
    }

    assert set(body["summary"].keys()) == {
        "startup_repair",
        "recovery",
        "terminal_failures",
    }

    assert set(body["signals"].keys()) == {
        "recovery_attempts_total",
        "recovery_action_taken_total",
        "retries_triggered_total",
        "reentries_triggered_total",
        "terminal_failures_confirmed_total",
        "startup_repair_items_total",
        "startup_repairs_applied_total",
        "startup_repair_failed_total",
        "startup_repair_unresolved_total",
        "startup_repair_skipped_total",
    }

def test_operations_alerts_requires_authentication(tmp_path):
    client = _client(tmp_path)

    response = client.get("/api/operations/alerts")

    assert response.status_code == 401


def test_operations_alerts_forbids_viewer(tmp_path):
    client = _client(tmp_path)

    response = client.get(
        "/api/operations/alerts",
        headers={"Authorization": "Bearer viewer-token"},
    )

    assert response.status_code == 403


def test_operations_alerts_reports_clear_when_no_alerts(tmp_path):
    client = _client(tmp_path)

    response = client.get(
        "/api/operations/alerts",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "clear"
    assert body["alerts"] == []
    assert "generated_at" in body


def test_operations_alerts_reports_startup_repair_critical_alert(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    app.state.operational_metrics_store.increment_counter("startup_repair_failed_total")

    client = TestClient(app)

    response = client.get(
        "/api/operations/alerts",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "active"
    assert body["alerts"][0]["code"] == "startup_repair_failed"
    assert body["alerts"][0]["severity"] == "critical"
    assert body["alerts"][0]["recommended_action"] == "inspect_startup_repair"
    assert body["alerts"][0]["signal"] == "startup_repair_failed_total"
    assert body["alerts"][0]["value"] == 1


def test_operations_alerts_reports_terminal_failure_warning_alert(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    app.state.operational_metrics_store.increment_counter(
        "terminal_failures_confirmed_total"
    )

    client = TestClient(app)

    response = client.get(
        "/api/operations/alerts",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "active"
    assert body["alerts"][0]["code"] == "terminal_failures_confirmed"
    assert body["alerts"][0]["severity"] == "warning"
    assert body["alerts"][0]["recommended_action"] == "inspect_terminal_failures"


def test_operations_alerts_response_shape_is_stable(tmp_path):
    client = _client(tmp_path)

    response = client.get(
        "/api/operations/alerts",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert set(body.keys()) == {
        "status",
        "generated_at",
        "alerts",
    }


def test_operations_metrics_openapi_response_contract_is_typed(tmp_path):
    client = _client(tmp_path)

    schema = client.get("/openapi.json").json()
    response_schema = schema["paths"]["/api/operations/metrics"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]

    assert response_schema["$ref"] == "#/components/schemas/OperationalMetricsResponse"

    model_schema = schema["components"]["schemas"]["OperationalMetricsResponse"]
    assert set(model_schema["properties"].keys()) == {
        "status",
        "generated_at",
        "signals",
        "counters",
        "decision_counts",
        "reason_counts",
    }
    assert set(model_schema["required"]) == {
        "status",
        "generated_at",
        "signals",
        "counters",
        "decision_counts",
        "reason_counts",
    }


def test_operations_health_summary_openapi_response_contract_is_typed(tmp_path):
    client = _client(tmp_path)

    schema = client.get("/openapi.json").json()
    response_schema = schema["paths"]["/api/operations/health-summary"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]

    assert response_schema["$ref"] == "#/components/schemas/OperationalHealthSummaryResponse"

    model_schema = schema["components"]["schemas"]["OperationalHealthSummaryResponse"]
    assert set(model_schema["properties"].keys()) == {
        "status",
        "generated_at",
        "summary",
        "signals",
        "recommended_action",
    }
    assert set(model_schema["required"]) == {
        "status",
        "generated_at",
        "summary",
        "signals",
        "recommended_action",
    }


def test_operations_alerts_openapi_response_contract_is_typed(tmp_path):
    client = _client(tmp_path)

    schema = client.get("/openapi.json").json()
    response_schema = schema["paths"]["/api/operations/alerts"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]

    assert response_schema["$ref"] == "#/components/schemas/OperationalAlertsResponse"

    model_schema = schema["components"]["schemas"]["OperationalAlertsResponse"]
    assert set(model_schema["properties"].keys()) == {
        "status",
        "generated_at",
        "alerts",
    }
    assert set(model_schema["required"]) == {
        "status",
        "generated_at",
        "alerts",
    }

    alert_model_schema = schema["components"]["schemas"]["OperationalAlertResponse"]
    assert set(alert_model_schema["properties"].keys()) == {
        "code",
        "severity",
        "message",
        "recommended_action",
        "signal",
        "value",
    }
    assert set(alert_model_schema["required"]) == {
        "code",
        "severity",
        "message",
        "recommended_action",
        "signal",
        "value",
    }

def test_operations_release_identity_requires_authentication(tmp_path):
    client = _client(tmp_path)

    response = client.get("/api/operations/release-identity")

    assert response.status_code == 401


def test_operations_release_identity_forbids_viewer(tmp_path):
    client = _client(tmp_path)

    response = client.get(
        "/api/operations/release-identity",
        headers={"Authorization": "Bearer viewer-token"},
    )

    assert response.status_code == 403


def test_operations_release_identity_returns_safe_fallback_metadata(tmp_path, monkeypatch):
    for key in (
        "INVOMATCH_APPLICATION_NAME",
        "INVOMATCH_APPLICATION_VERSION",
        "INVOMATCH_RELEASE_COMMIT_SHA",
        "INVOMATCH_RELEASE_BRANCH",
        "INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC",
        "INVOMATCH_RELEASE_VALIDATION_STATUS",
    ):
        monkeypatch.delenv(key, raising=False)

    client = _client(tmp_path)

    response = client.get(
        "/api/operations/release-identity",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body == {
        "application_name": "invomatch",
        "application_version": "0.1.0",
        "git_commit_sha": "unknown",
        "git_branch": "unknown",
        "build_timestamp_utc": None,
        "environment": "local",
        "validation_status": "not_declared",
        "metadata_available": False,
    }


def test_operations_release_identity_returns_explicit_release_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("INVOMATCH_RELEASE_COMMIT_SHA", "df5b2550719f03eedf460a1bc949f88d622a4159")
    monkeypatch.setenv("INVOMATCH_RELEASE_BRANCH", "main")
    monkeypatch.setenv("INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC", "2026-05-06T08:00:00Z")
    monkeypatch.setenv("INVOMATCH_RELEASE_VALIDATION_STATUS", "not_declared")
    monkeypatch.setenv("INVOMATCH_SECRET_SHOULD_NOT_LEAK", "must-not-leak")

    client = _client(tmp_path)

    response = client.get(
        "/api/operations/release-identity",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["application_name"] == "invomatch"
    assert body["application_version"] == "0.1.0"
    assert body["git_commit_sha"] == "df5b2550719f03eedf460a1bc949f88d622a4159"
    assert body["git_branch"] == "main"
    assert body["build_timestamp_utc"] == "2026-05-06T08:00:00Z"
    assert body["environment"] == "local"
    assert body["validation_status"] == "not_declared"
    assert body["metadata_available"] is True
    assert "must-not-leak" not in response.text


def test_operations_release_identity_reports_500_when_service_missing(tmp_path):
    app = create_app(
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )

    delattr(app.state, "release_identity_service")

    client = TestClient(app)

    response = client.get(
        "/api/operations/release-identity",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "release identity service is not configured"


def test_operations_release_identity_response_shape_is_stable(tmp_path):
    client = _client(tmp_path)

    response = client.get(
        "/api/operations/release-identity",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    body = response.json()

    assert set(body.keys()) == {
        "application_name",
        "application_version",
        "git_commit_sha",
        "git_branch",
        "build_timestamp_utc",
        "environment",
        "validation_status",
        "metadata_available",
    }


def test_operations_release_identity_openapi_response_contract_is_typed(tmp_path):
    client = _client(tmp_path)

    schema = client.get("/openapi.json").json()
    response_schema = schema["paths"]["/api/operations/release-identity"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]

    assert response_schema["$ref"] == "#/components/schemas/OperationalReleaseIdentityResponse"

    model_schema = schema["components"]["schemas"]["OperationalReleaseIdentityResponse"]
    assert set(model_schema["properties"].keys()) == {
        "application_name",
        "application_version",
        "git_commit_sha",
        "git_branch",
        "build_timestamp_utc",
        "environment",
        "validation_status",
        "metadata_available",
    }
    assert set(model_schema["required"]) == {
        "application_name",
        "application_version",
        "git_commit_sha",
        "git_branch",
        "build_timestamp_utc",
        "environment",
        "validation_status",
        "metadata_available",
    }
