from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from invomatch.domain.export_delivery.models import (
    ExportArtifact,
    ExportArtifactStatus,
    GenerationMode,
)


def test_export_artifact_model_accepts_valid_values() -> None:
    created_at = datetime(2026, 4, 2, 12, 0, tzinfo=UTC)
    expires_at = created_at + timedelta(hours=1)

    artifact = ExportArtifact(
        id="art_001",
        run_id="run_123",
        format="json",
        content_type="application/json",
        file_name="run_run_123_export_json.json",
        storage_backend="local",
        storage_key="exports/run_123/art_001.json",
        byte_size=128,
        checksum="abc123",
        status=ExportArtifactStatus.READY,
        created_at=created_at,
        expires_at=expires_at,
        generation_mode=GenerationMode.SYNC,
    )

    assert artifact.id == "art_001"
    assert artifact.run_id == "run_123"
    assert artifact.format == "json"
    assert artifact.status == ExportArtifactStatus.READY
    assert artifact.generation_mode == GenerationMode.SYNC
    assert artifact.byte_size == 128
    assert artifact.storage_key == "exports/run_123/art_001.json"


def test_export_artifact_model_normalizes_naive_datetimes_to_utc() -> None:
    created_at = datetime(2026, 4, 2, 12, 0)
    expires_at = datetime(2026, 4, 2, 13, 0)

    artifact = ExportArtifact(
        id="art_002",
        run_id="run_456",
        format="csv",
        content_type="text/csv",
        file_name="run_run_456_export_csv.csv",
        storage_backend="local",
        storage_key="exports/run_456/art_002.csv",
        status=ExportArtifactStatus.READY,
        created_at=created_at,
        expires_at=expires_at,
        generation_mode=GenerationMode.CACHED,
    )

    assert artifact.created_at.tzinfo == UTC
    assert artifact.expires_at is not None
    assert artifact.expires_at.tzinfo == UTC


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("id", "   "),
        ("run_id", "   "),
        ("format", "   "),
        ("content_type", "   "),
        ("file_name", "   "),
        ("storage_backend", "   "),
        ("storage_key", "   "),
    ],
)
def test_export_artifact_model_rejects_blank_required_strings(
    field_name: str,
    field_value: str,
) -> None:
    payload = {
        "id": "art_003",
        "run_id": "run_789",
        "format": "json",
        "content_type": "application/json",
        "file_name": "run_run_789_export_json.json",
        "storage_backend": "local",
        "storage_key": "exports/run_789/art_003.json",
        "status": ExportArtifactStatus.READY,
        "created_at": datetime(2026, 4, 2, 12, 0, tzinfo=UTC),
        "generation_mode": GenerationMode.SYNC,
    }
    payload[field_name] = field_value

    with pytest.raises(ValidationError):
        ExportArtifact(**payload)


def test_export_artifact_model_rejects_negative_byte_size() -> None:
    with pytest.raises(ValidationError):
        ExportArtifact(
            id="art_004",
            run_id="run_111",
            format="json",
            content_type="application/json",
            file_name="run_run_111_export_json.json",
            storage_backend="local",
            storage_key="exports/run_111/art_004.json",
            byte_size=-1,
            status=ExportArtifactStatus.READY,
            created_at=datetime(2026, 4, 2, 12, 0, tzinfo=UTC),
            generation_mode=GenerationMode.SYNC,
        )


def test_export_artifact_model_rejects_expiry_before_creation() -> None:
    created_at = datetime(2026, 4, 2, 12, 0, tzinfo=UTC)
    expires_at = created_at - timedelta(minutes=1)

    with pytest.raises(ValidationError):
        ExportArtifact(
            id="art_005",
            run_id="run_222",
            format="csv",
            content_type="text/csv",
            file_name="run_run_222_export_csv.csv",
            storage_backend="local",
            storage_key="exports/run_222/art_005.csv",
            status=ExportArtifactStatus.READY,
            created_at=created_at,
            expires_at=expires_at,
            generation_mode=GenerationMode.SYNC,
        )