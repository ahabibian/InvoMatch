from fastapi.testclient import TestClient

from invomatch.main import create_app


def test_health_endpoint_exposes_startup_repair_state(tmp_path) -> None:
    app = create_app(
        run_store_backend="json",
        run_store_path=tmp_path / "runs.json",
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert "startup_scan_failed" in payload
    assert "readiness_ok" in payload
    assert "readiness_reason" in payload


def test_readiness_endpoint_exposes_startup_repair_summary(tmp_path) -> None:
    app = create_app(
        run_store_backend="json",
        run_store_path=tmp_path / "runs.json",
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    client = TestClient(app)

    response = client.get("/readiness")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] in {"ready", "not_ready"}
    assert "startup_scan_failed" in payload
    assert "readiness_reason" in payload
    assert "repairs_applied" in payload
    assert "unresolved_mismatches" in payload
    assert "skipped_due_to_active_lease" in payload
    assert "skipped_due_to_terminal_protection" in payload