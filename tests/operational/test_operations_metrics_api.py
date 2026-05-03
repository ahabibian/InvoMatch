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
