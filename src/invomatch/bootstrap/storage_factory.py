from dataclasses import dataclass
from pathlib import Path

from invomatch.config.models import ApplicationSettings


@dataclass(frozen=True)
class StorageDependencies:
    artifact_root_path: Path
    export_directory: Path
    upload_root_path: Path
    temp_directory: Path
    log_directory: Path


def build_storage_dependencies(settings: ApplicationSettings) -> StorageDependencies:
    return StorageDependencies(
        artifact_root_path=settings.storage.artifact_root_path,
        export_directory=settings.storage.export_directory,
        upload_root_path=settings.storage.upload_root_path,
        temp_directory=settings.storage.temp_directory,
        log_directory=settings.storage.log_directory,
    )