from dataclasses import dataclass
from pathlib import Path

from invomatch.config.models import ApplicationSettings
from invomatch.services.storage.local_storage import LocalArtifactStorage


@dataclass(frozen=True)
class StorageDependencies:
    artifact_root_path: Path
    export_directory: Path
    upload_root_path: Path
    temp_directory: Path
    log_directory: Path
    export_root: Path
    artifact_storage: LocalArtifactStorage


def build_storage_dependencies(
    settings: ApplicationSettings,
    *,
    export_base_dir: Path | None = None,
) -> StorageDependencies:
    export_root = Path(export_base_dir or settings.storage.export_directory)

    return StorageDependencies(
        artifact_root_path=settings.storage.artifact_root_path,
        export_directory=settings.storage.export_directory,
        upload_root_path=settings.storage.upload_root_path,
        temp_directory=settings.storage.temp_directory,
        log_directory=settings.storage.log_directory,
        export_root=export_root,
        artifact_storage=LocalArtifactStorage(export_root),
    )