from __future__ import annotations

from invomatch.domain.export_delivery.models import (
    ExportArtifact,
    ExportArtifactStatus,
    GenerationMode,
)
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.handlers.export_run import ExportRunActionHandler


class FakeDeliveryService:
    def create_export_artifact(
        self,
        run_id: str,
        format: str,
        *,
        force_regenerate: bool = False,
    ) -> ExportArtifact:
        return ExportArtifact(
            id="art_001",
            run_id=run_id,
            format=format,
            content_type="application/json" if format == "json" else "text/csv",
            file_name=f"run_{run_id}_export_{format}.json" if format == "json" else f"run_{run_id}_export_{format}.csv",
            storage_backend="local",
            storage_key=f"exports/{run_id}/art_001.json" if format == "json" else f"exports/{run_id}/art_001.csv",
            byte_size=128,
            checksum=None,
            status=ExportArtifactStatus.READY,
            created_at="2026-04-02T20:00:00Z",
            expires_at=None,
            generation_mode=GenerationMode.SYNC,
        )


def test_export_run_action_handler_returns_successful_artifact_response() -> None:
    handler = ExportRunActionHandler(delivery_service=FakeDeliveryService())

    result = handler.handle(
        ActionCommand(
            action_type="export_run",
            run_id="run_123",
            payload={"format": "json"},
        )
    )

    assert result.action_type == "export_run"
    assert result.target_type == "run"
    assert result.target_id == "run_123"
    assert result.status.value == "success"
    assert result.response_payload["run_id"] == "run_123"
    assert result.response_payload["artifact_id"] == "art_001"
    assert result.response_payload["export_status"] == "READY"
    assert result.response_payload["export_format"] == "json"