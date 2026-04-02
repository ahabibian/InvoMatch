from __future__ import annotations

import uuid
from datetime import UTC, datetime

from invomatch.domain.export_delivery.models import (
    ExportArtifact,
    ExportArtifactStatus,
    GenerationMode,
)
from invomatch.domain.export_delivery.repository import ExportArtifactRepository
from invomatch.services.storage.base import ArtifactStorage


class ExportDeliveryService:
    def __init__(
        self,
        repository: ExportArtifactRepository,
        storage: ArtifactStorage,
        export_generator,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._export_generator = export_generator

    def create_export_artifact(
        self,
        run_id: str,
        format: str,
        *,
        force_regenerate: bool = False,
    ) -> ExportArtifact:

        if not force_regenerate:
            existing = self._repository.get_latest_ready(run_id, format)
            if existing is not None:
                return existing

        content: bytes = self._export_generator(run_id, format)

        artifact_id = self._generate_artifact_id()
        storage_key = self._build_storage_key(run_id, artifact_id, format)

        stored_ref = self._storage.save_bytes(
            key=storage_key,
            content=content,
            content_type=self._content_type(format),
        )

        now = datetime.now(UTC)

        artifact = ExportArtifact(
            id=artifact_id,
            run_id=run_id,
            format=format,
            content_type=self._content_type(format),
            file_name=self._file_name(run_id, format),
            storage_backend=stored_ref.backend,
            storage_key=stored_ref.key,
            byte_size=stored_ref.size,
            checksum=None,
            status=ExportArtifactStatus.READY,
            created_at=now,
            expires_at=None,
            generation_mode=GenerationMode.SYNC,
        )

        self._repository.create(artifact)

        return artifact

    @staticmethod
    def _generate_artifact_id() -> str:
        return uuid.uuid4().hex

    @staticmethod
    def _build_storage_key(run_id: str, artifact_id: str, format: str) -> str:
        extension = "json" if format == "json" else "csv"
        return f"exports/{run_id}/{artifact_id}.{extension}"

    @staticmethod
    def _file_name(run_id: str, format: str) -> str:
        extension = "json" if format == "json" else "csv"
        return f"run_{run_id}_export_{format}.{extension}"

    @staticmethod
    def _content_type(format: str) -> str:
        if format == "json":
            return "application/json"
        if format == "csv":
            return "text/csv"
        raise ValueError(f"unsupported format: {format}")