from __future__ import annotations

from datetime import UTC, datetime

from invomatch.domain.export_delivery.models import (
    ExportArtifact,
    ExportArtifactStatus,
    GenerationMode,
)
from invomatch.domain.export_delivery.repository import ExportArtifactRepository


def _build_artifact(artifact_id: str = "art_001") -> ExportArtifact:
    return ExportArtifact(
        id=artifact_id,
        run_id="run_123",
        format="json",
        content_type="application/json",
        file_name="run_run_123_export_json.json",
        storage_backend="local",
        storage_key=f"exports/run_123/{artifact_id}.json",
        byte_size=123,
        checksum="abc123",
        status=ExportArtifactStatus.READY,
        created_at=datetime(2026, 4, 2, 12, 0, tzinfo=UTC),
        generation_mode=GenerationMode.SYNC,
    )


def test_export_artifact_repository_is_abstract() -> None:
    try:
        ExportArtifactRepository()  # type: ignore[abstract]
        instantiated = True
    except TypeError:
        instantiated = False

    assert instantiated is False


def test_export_artifact_repository_contract_shape() -> None:
    artifact = _build_artifact()

    assert hasattr(ExportArtifactRepository, "create")
    assert hasattr(ExportArtifactRepository, "get_by_id")
    assert hasattr(ExportArtifactRepository, "get_latest_ready")
    assert hasattr(ExportArtifactRepository, "list_by_run")
    assert hasattr(ExportArtifactRepository, "update_status")

    assert artifact.status == ExportArtifactStatus.READY