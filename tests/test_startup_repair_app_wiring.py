from pathlib import Path

from invomatch.main import create_app


def test_create_app_exposes_startup_repair_state(tmp_path: Path) -> None:
    app = create_app(
        run_store_backend="json",
        run_store_path=tmp_path / "runs.json",
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )

    assert hasattr(app.state, "operational_metrics_store")
    assert hasattr(app.state, "operational_metrics_service")
    assert hasattr(app.state, "restart_consistency_repair_service")
    assert hasattr(app.state, "startup_repair_coordinator")
    assert hasattr(app.state, "startup_repair_result")

    result = app.state.startup_repair_result
    assert result is not None
    assert hasattr(result, "startup_scan_failed")
    assert hasattr(result, "readiness_ok")
    assert hasattr(result, "readiness_reason")