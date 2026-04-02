from __future__ import annotations

from invomatch.domain.export_delivery.models import ExportArtifact, ExportArtifactStatus
from invomatch.domain.export_delivery.repository import ExportArtifactRepository
from invomatch.services.storage.base import ArtifactStorage


class ArtifactQueryError(Exception):
    pass


class ArtifactNotFoundError(ArtifactQueryError):
    pass


class ArtifactExpiredError(ArtifactQueryError):
    pass


class ArtifactDeletedError(ArtifactQueryError):
    pass


class ArtifactFailedError(ArtifactQueryError):
    pass


class ArtifactUnavailableError(ArtifactQueryError):
    pass


class ArtifactQueryService:
    def __init__(
        self,
        repository: ExportArtifactRepository,
        storage: ArtifactStorage | None = None,
    ) -> None:
        self._repository = repository
        self._storage = storage

    def list_artifacts_for_run(self, run_id: str) -> list[ExportArtifact]:
        return self._repository.list_by_run(run_id)

    def get_artifact_by_id(self, artifact_id: str) -> ExportArtifact:
        artifact = self._repository.get_by_id(artifact_id)
        if artifact is None:
            raise ArtifactNotFoundError(f"artifact not found: {artifact_id}")
        return artifact

    def get_downloadable_artifact_by_id(self, artifact_id: str) -> ExportArtifact:
        artifact = self.get_artifact_by_id(artifact_id)

        if artifact.status == ExportArtifactStatus.FAILED:
            raise ArtifactFailedError(f"artifact is failed: {artifact_id}")

        if artifact.status == ExportArtifactStatus.DELETED:
            raise ArtifactDeletedError(f"artifact is deleted: {artifact_id}")

        if artifact.status == ExportArtifactStatus.EXPIRED:
            raise ArtifactExpiredError(f"artifact is expired: {artifact_id}")

        if artifact.status != ExportArtifactStatus.READY:
            raise ArtifactFailedError(
                f"artifact is in unsupported status for download: {artifact.status}"
            )

        if self._storage is not None and not self._storage.exists(artifact.storage_key):
            raise ArtifactUnavailableError(
                f"artifact content is unavailable: {artifact_id}"
            )

        return artifact