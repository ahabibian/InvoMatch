from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

from invomatch.domain.export_delivery.models import (
    ExportArtifact,
    ExportArtifactStatus,
    GenerationMode,
)
from invomatch.main import create_app
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.run_store import JsonRunStore


def _write_source_files(tmp_path: Path) -> tuple[Path, Path]:
    invoice_path = tmp_path / "invoices.csv"
    payment_path = tmp_path / "payments.csv"

    invoice_path.write_text(
        "\n".join(
            [
                "id,date,amount,currency,reference",
                "inv-1,2024-01-10,100.00,USD,INV-1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payment_path.write_text(
        "\n".join(
            [
                "id,date,amount,currency,reference,invoice_id",
                "pay-1,2024-01-12,100.00,USD,Payment for INV-1,inv-1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return invoice_path, payment_path


def _create_completed_run(tmp_path: Path, run_store: JsonRunStore):
    invoice_path, payment_path = _write_source_files(tmp_path)
    return reconcile_and_save(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )


def _make_artifact(
    *,
    artifact_id: str,
    run_id: str,
    status: ExportArtifactStatus,
    created_at: datetime | None = None,
    expires_at: datetime | None = None,
    format: str = "json",
) -> ExportArtifact:
    now = created_at or datetime.now(UTC)

    extension = "json" if format == "json" else "csv"
    content_type = "application/json" if format == "json" else "text/csv"

    return ExportArtifact(
        id=artifact_id,
        run_id=run_id,
        format=format,
        content_type=content_type,
        file_name=f"run_{run_id}_export_{format}.{extension}",
        storage_backend="local",
        storage_key=f"exports/{run_id}/{artifact_id}.{extension}",
        byte_size=128,
        checksum=None,
        status=status,
        created_at=now,
        expires_at=expires_at,
        generation_mode=GenerationMode.SYNC,
    )


def test_list_run_export_artifacts_returns_empty_list_for_existing_run_without_artifacts(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    run = _create_completed_run(tmp_path, run_store)
    app = create_app(
        run_store=run_store,
        export_base_dir=tmp_path / "exports",
    )
    client = TestClient(app)

    response = client.get(f"/api/reconciliation/runs/{run.run_id}/exports")

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"] == run.run_id
    assert payload["artifacts"] == []


def test_list_run_export_artifacts_returns_404_for_missing_run(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    app = create_app(
        run_store=run_store,
        export_base_dir=tmp_path / "exports",
    )
    client = TestClient(app)

    response = client.get("/api/reconciliation/runs/missing-run/exports")

    assert response.status_code == 404
    payload = response.json()["detail"]
    assert payload["code"] == "run_not_found"
    assert payload["message"] == "Reconciliation run not found"


def test_get_export_artifact_metadata_returns_artifact_details(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    run = _create_completed_run(tmp_path, run_store)
    app = create_app(
        run_store=run_store,
        export_base_dir=tmp_path / "exports",
    )

    repository = app.state.export_artifact_repository
    artifact = _make_artifact(
        artifact_id="artifact-ready-1",
        run_id=run.run_id,
        status=ExportArtifactStatus.READY,
    )
    repository.create(artifact)

    client = TestClient(app)
    response = client.get(f"/api/reconciliation/exports/{artifact.id}")

    assert response.status_code == 200
    payload = response.json()["artifact"]

    assert payload["artifact_id"] == artifact.id
    assert payload["run_id"] == run.run_id
    assert payload["format"] == "json"
    assert payload["file_name"] == f"run_{run.run_id}_export_json.json"
    assert payload["content_type"] == "application/json"
    assert payload["size_bytes"] == 128
    assert payload["state"] == "available"
    assert payload["download_available"] is True


def test_get_export_artifact_metadata_returns_404_for_missing_artifact(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    app = create_app(
        run_store=run_store,
        export_base_dir=tmp_path / "exports",
    )
    client = TestClient(app)

    response = client.get("/api/reconciliation/exports/missing-artifact")

    assert response.status_code == 404
    payload = response.json()["detail"]
    assert payload["code"] == "artifact_not_found"
    assert payload["message"] == "Export artifact not found"


def test_get_export_artifact_metadata_preserves_lifecycle_visibility_for_non_downloadable_artifacts(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    run = _create_completed_run(tmp_path, run_store)
    app = create_app(
        run_store=run_store,
        export_base_dir=tmp_path / "exports",
    )

    repository = app.state.export_artifact_repository
    now = datetime.now(UTC)

    expired_artifact = _make_artifact(
        artifact_id="artifact-expired-1",
        run_id=run.run_id,
        status=ExportArtifactStatus.EXPIRED,
        created_at=now - timedelta(days=2),
        expires_at=now - timedelta(days=1),
    )
    deleted_artifact = _make_artifact(
        artifact_id="artifact-deleted-1",
        run_id=run.run_id,
        status=ExportArtifactStatus.DELETED,
        created_at=now - timedelta(hours=2),
    )
    failed_artifact = _make_artifact(
        artifact_id="artifact-failed-1",
        run_id=run.run_id,
        status=ExportArtifactStatus.FAILED,
        created_at=now - timedelta(hours=1),
    )

    repository.create(expired_artifact)
    repository.create(deleted_artifact)
    repository.create(failed_artifact)

    client = TestClient(app)

    expired_response = client.get(f"/api/reconciliation/exports/{expired_artifact.id}")
    deleted_response = client.get(f"/api/reconciliation/exports/{deleted_artifact.id}")
    failed_response = client.get(f"/api/reconciliation/exports/{failed_artifact.id}")

    assert expired_response.status_code == 200
    assert deleted_response.status_code == 200
    assert failed_response.status_code == 200

    expired_payload = expired_response.json()["artifact"]
    deleted_payload = deleted_response.json()["artifact"]
    failed_payload = failed_response.json()["artifact"]

    assert expired_payload["state"] == "expired"
    assert expired_payload["download_available"] is False

    assert deleted_payload["state"] == "deleted"
    assert deleted_payload["download_available"] is False

    assert failed_payload["state"] == "failed"
    assert failed_payload["download_available"] is False
def test_download_export_artifact_success(tmp_path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    run = _create_completed_run(tmp_path, run_store)

    export_dir = tmp_path / "exports"
    app = create_app(run_store=run_store, export_base_dir=export_dir)

    repository = app.state.export_artifact_repository
    storage = app.state.export_artifact_storage

    artifact = _make_artifact(
        artifact_id="artifact-ready-download",
        run_id=run.run_id,
        status=ExportArtifactStatus.READY,
    )

    # create actual file in storage
    storage.save_bytes(
        key=artifact.storage_key,
        content=b"test-content",
        content_type=artifact.content_type,
    )

    repository.create(artifact)

    client = TestClient(app)

    response = client.get(f"/api/reconciliation/exports/{artifact.id}/download")

    assert response.status_code == 200
    assert response.content == b"test-content"
    assert response.headers["Content-Disposition"].startswith("attachment;")


def test_download_export_artifact_not_found(tmp_path):
    app = create_app(run_store=JsonRunStore(tmp_path / "runs.json"))

    client = TestClient(app)

    response = client.get("/api/reconciliation/exports/missing/download")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "artifact_not_found"


def test_download_export_artifact_expired(tmp_path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    run = _create_completed_run(tmp_path, run_store)

    app = create_app(run_store=run_store, export_base_dir=tmp_path / "exports")

    repository = app.state.export_artifact_repository

    artifact = _make_artifact(
        artifact_id="artifact-expired",
        run_id=run.run_id,
        status=ExportArtifactStatus.EXPIRED,
    )

    repository.create(artifact)

    client = TestClient(app)

    response = client.get(f"/api/reconciliation/exports/{artifact.id}/download")

    assert response.status_code == 410
    assert response.json()["detail"]["code"] == "artifact_expired"


def test_download_export_artifact_deleted(tmp_path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    run = _create_completed_run(tmp_path, run_store)

    app = create_app(run_store=run_store, export_base_dir=tmp_path / "exports")

    repository = app.state.export_artifact_repository

    artifact = _make_artifact(
        artifact_id="artifact-deleted",
        run_id=run.run_id,
        status=ExportArtifactStatus.DELETED,
    )

    repository.create(artifact)

    client = TestClient(app)

    response = client.get(f"/api/reconciliation/exports/{artifact.id}/download")

    assert response.status_code == 410
    assert response.json()["detail"]["code"] == "artifact_deleted"


def test_download_export_artifact_failed(tmp_path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    run = _create_completed_run(tmp_path, run_store)

    app = create_app(run_store=run_store, export_base_dir=tmp_path / "exports")

    repository = app.state.export_artifact_repository

    artifact = _make_artifact(
        artifact_id="artifact-failed",
        run_id=run.run_id,
        status=ExportArtifactStatus.FAILED,
    )

    repository.create(artifact)

    client = TestClient(app)

    response = client.get(f"/api/reconciliation/exports/{artifact.id}/download")

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "artifact_failed"


def test_download_export_artifact_unavailable(tmp_path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    run = _create_completed_run(tmp_path, run_store)

    app = create_app(run_store=run_store, export_base_dir=tmp_path / "exports")

    repository = app.state.export_artifact_repository

    # READY but no file in storage
    artifact = _make_artifact(
        artifact_id="artifact-unavailable",
        run_id=run.run_id,
        status=ExportArtifactStatus.READY,
    )

    repository.create(artifact)

    client = TestClient(app)

    response = client.get(f"/api/reconciliation/exports/{artifact.id}/download")

    assert response.status_code == 500
    assert response.json()["detail"]["code"] == "artifact_unavailable"

