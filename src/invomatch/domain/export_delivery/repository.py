from __future__ import annotations

from abc import ABC, abstractmethod

from invomatch.domain.export_delivery.models import ExportArtifact, ExportArtifactStatus


class ExportArtifactRepository(ABC):
    @abstractmethod
    def create(self, artifact: ExportArtifact) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, artifact_id: str) -> ExportArtifact | None:
        raise NotImplementedError

    @abstractmethod
    def get_latest_ready(
        self,
        run_id: str,
        format: str,
    ) -> ExportArtifact | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_run(self, run_id: str) -> list[ExportArtifact]:
        raise NotImplementedError

    @abstractmethod
    def update_status(
        self,
        artifact_id: str,
        status: ExportArtifactStatus,
    ) -> ExportArtifact:
        raise NotImplementedError