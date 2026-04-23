from __future__ import annotations

from datetime import UTC, datetime
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


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


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


def _make_ready_artifact(run_id: str, artifact_id: str = "artifact-ready-1") -> ExportArtifact:
    return ExportArtifact(
        id=artifact_id,
        run_id=run_id,
        format="json",
        content_type="application/json",
        file_name=f"run_{run_id}_export_json.json",
        storage_backend="local",
        storage_key=f"exports/{run_id}/{artifact_id}.json",
        byte_size=32,
        checksum=None,
        status=ExportArtifactStatus.READY,
        created_at=datetime.now(UTC),
        expires_at=None,
        generation_mode=GenerationMode.SYNC,
    )


def test_scenario_8_permission_boundary_enforcement(tmp_path: Path) -> None:
    run_store = JsonRunStore(tmp_path / "runs.json")
    app = create_app(
        run_store=run_store,
        export_base_dir=tmp_path / "exports",
    )
    client = TestClient(app)

    payload = {
        "invoices": [
            {
                "id": "inv-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
                "reference": "ref-001",
            }
        ],
        "payments": [
            {
                "id": "pay-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
                "reference": "ref-001",
            }
        ],
    }

    unauthenticated_submit = client.post(
        "/api/reconciliation/input/json",
        json=payload,
    )
    assert unauthenticated_submit.status_code == 401

    viewer_create_run = client.post(
        "/api/reconciliation/runs",
        json={
            "invoice_csv_path": "sample-data/invoices.csv",
            "payment_csv_path": "sample-data/payments.csv",
        },
        headers=_auth_headers("viewer-token"),
    )
    assert viewer_create_run.status_code == 403

    operator_create_run = client.post(
        "/api/reconciliation/runs",
        json={
            "invoice_csv_path": "sample-data/invoices.csv",
            "payment_csv_path": "sample-data/payments.csv",
        },
        headers=_auth_headers("operator-token"),
    )
    assert operator_create_run.status_code == 201

    viewer_resolve_review = client.post(
        "/api/reconciliation/runs/run-123/actions",
        json={
            "action_type": "resolve_review",
            "target_id": "case-1",
            "payload": {},
            "note": "viewer attempt",
        },
        headers=_auth_headers("viewer-token"),
    )
    assert viewer_resolve_review.status_code == 403

    run = _create_completed_run(tmp_path, run_store)
    repository = app.state.export_artifact_repository
    storage = app.state.export_artifact_storage

    artifact = _make_ready_artifact(run.run_id)
    storage.save_bytes(
        key=artifact.storage_key,
        content=b'{"ok":true}',
        content_type=artifact.content_type,
    )
    repository.create(artifact)

    viewer_metadata = client.get(
        f"/api/reconciliation/exports/{artifact.id}",
        headers=_auth_headers("viewer-token"),
    )
    assert viewer_metadata.status_code == 200

    viewer_download = client.get(
        f"/api/reconciliation/exports/{artifact.id}/download",
        headers=_auth_headers("viewer-token"),
    )
    assert viewer_download.status_code == 403

    operator_download = client.get(
        f"/api/reconciliation/exports/{artifact.id}/download",
        headers=_auth_headers("operator-token"),
    )
    assert operator_download.status_code == 200