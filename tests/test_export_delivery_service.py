from __future__ import annotations

from pathlib import Path

from invomatch.domain.export_delivery.models import ExportArtifactStatus
from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)
from invomatch.services.export_delivery_service import ExportDeliveryService
from invomatch.services.storage.local_storage import LocalArtifactStorage


def fake_export_generator(run_id: str, format: str, *, tenant_id: str | None = None) -> bytes:
    return f"{run_id}-{format}".encode("utf-8")


def test_export_delivery_creates_artifact(tmp_path: Path) -> None:
    db_path = tmp_path / "db.sqlite3"

    repository = SqliteExportArtifactRepository(str(db_path))
    storage = LocalArtifactStorage(tmp_path / "exports")

    service = ExportDeliveryService(
        repository=repository,
        storage=storage,
        export_generator=fake_export_generator,
    )

    artifact = service.create_export_artifact("run_1", "json")

    assert artifact.run_id == "run_1"
    assert artifact.format == "json"
    assert artifact.status == ExportArtifactStatus.READY
    assert storage.exists(artifact.storage_key) is True


def test_export_delivery_uses_cache(tmp_path: Path) -> None:
    db_path = tmp_path / "db.sqlite3"

    repository = SqliteExportArtifactRepository(str(db_path))
    storage = LocalArtifactStorage(tmp_path / "exports")

    calls = {"count": 0}

    def generator(run_id: str, format: str, *, tenant_id: str | None = None) -> bytes:
        calls["count"] += 1
        return b"data"

    service = ExportDeliveryService(
        repository=repository,
        storage=storage,
        export_generator=generator,
    )

    first = service.create_export_artifact("run_1", "json")
    second = service.create_export_artifact("run_1", "json")

    assert first.id == second.id
    assert calls["count"] == 1


def test_export_delivery_force_regenerate(tmp_path: Path) -> None:
    db_path = tmp_path / "db.sqlite3"

    repository = SqliteExportArtifactRepository(str(db_path))
    storage = LocalArtifactStorage(tmp_path / "exports")

    calls = {"count": 0}

    def generator(run_id: str, format: str, *, tenant_id: str | None = None) -> bytes:
        calls["count"] += 1
        return b"data"

    service = ExportDeliveryService(
        repository=repository,
        storage=storage,
        export_generator=generator,
    )

    first = service.create_export_artifact("run_1", "json")
    second = service.create_export_artifact("run_1", "json", force_regenerate=True)

    assert first.id != second.id
    assert calls["count"] == 2