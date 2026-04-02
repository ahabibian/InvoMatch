from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from invomatch.domain.export_delivery.models import (
    ExportArtifact,
    ExportArtifactStatus,
    GenerationMode,
)
from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)


def _build_artifact(
    artifact_id: str,
    *,
    run_id: str = "run_123",
    format: str = "json",
    status: ExportArtifactStatus = ExportArtifactStatus.READY,
    created_at: datetime | None = None,
) -> ExportArtifact:
    effective_created_at = created_at or datetime(2026, 4, 2, 12, 0, tzinfo=UTC)

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
        byte_size=123,
        checksum=f"checksum-{artifact_id}",
        status=status,
        created_at=effective_created_at,
        expires_at=effective_created_at + timedelta(hours=1),
        generation_mode=GenerationMode.SYNC,
    )


def test_sqlite_export_artifact_repository_create_and_get_by_id(tmp_path: Path) -> None:
    db_path = tmp_path / "export_artifacts.sqlite3"
    repository = SqliteExportArtifactRepository(str(db_path))

    artifact = _build_artifact("art_001")
    repository.create(artifact)

    loaded = repository.get_by_id("art_001")

    assert loaded is not None
    assert loaded.id == artifact.id
    assert loaded.run_id == artifact.run_id
    assert loaded.format == artifact.format
    assert loaded.status == ExportArtifactStatus.READY
    assert loaded.created_at == artifact.created_at
    assert loaded.expires_at == artifact.expires_at


def test_sqlite_export_artifact_repository_get_latest_ready_returns_newest_ready(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "export_artifacts.sqlite3"
    repository = SqliteExportArtifactRepository(str(db_path))

    older = _build_artifact(
        "art_older",
        created_at=datetime(2026, 4, 2, 10, 0, tzinfo=UTC),
    )
    newer = _build_artifact(
        "art_newer",
        created_at=datetime(2026, 4, 2, 11, 0, tzinfo=UTC),
    )
    failed = _build_artifact(
        "art_failed",
        status=ExportArtifactStatus.FAILED,
        created_at=datetime(2026, 4, 2, 12, 0, tzinfo=UTC),
    )

    repository.create(older)
    repository.create(newer)
    repository.create(failed)

    latest = repository.get_latest_ready("run_123", "json")

    assert latest is not None
    assert latest.id == "art_newer"
    assert latest.status == ExportArtifactStatus.READY


def test_sqlite_export_artifact_repository_list_by_run_is_ordered_newest_first(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "export_artifacts.sqlite3"
    repository = SqliteExportArtifactRepository(str(db_path))

    first = _build_artifact(
        "art_first",
        created_at=datetime(2026, 4, 2, 9, 0, tzinfo=UTC),
    )
    second = _build_artifact(
        "art_second",
        created_at=datetime(2026, 4, 2, 10, 0, tzinfo=UTC),
    )
    third = _build_artifact(
        "art_third",
        run_id="run_999",
        created_at=datetime(2026, 4, 2, 11, 0, tzinfo=UTC),
    )

    repository.create(first)
    repository.create(second)
    repository.create(third)

    artifacts = repository.list_by_run("run_123")

    assert [artifact.id for artifact in artifacts] == ["art_second", "art_first"]


def test_sqlite_export_artifact_repository_update_status_returns_updated_artifact(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "export_artifacts.sqlite3"
    repository = SqliteExportArtifactRepository(str(db_path))

    artifact = _build_artifact("art_010")
    repository.create(artifact)

    updated = repository.update_status("art_010", ExportArtifactStatus.EXPIRED)

    assert updated.id == "art_010"
    assert updated.status == ExportArtifactStatus.EXPIRED

    reloaded = repository.get_by_id("art_010")
    assert reloaded is not None
    assert reloaded.status == ExportArtifactStatus.EXPIRED


def test_sqlite_export_artifact_repository_update_status_missing_artifact_raises(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "export_artifacts.sqlite3"
    repository = SqliteExportArtifactRepository(str(db_path))

    with pytest.raises(KeyError):
        repository.update_status("missing", ExportArtifactStatus.DELETED)