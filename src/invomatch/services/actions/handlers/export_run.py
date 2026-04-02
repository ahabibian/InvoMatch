from __future__ import annotations

from uuid import uuid4

from invomatch.domain.export import ExportFormat
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.handlers.base import BaseActionHandler
from invomatch.services.actions.result import ActionExecutionResult, ActionExecutionStatus
from invomatch.services.export_delivery_service import ExportDeliveryService


class ExportRunActionHandler(BaseActionHandler):
    def __init__(self, delivery_service: ExportDeliveryService) -> None:
        self._delivery_service = delivery_service

    def handle(self, command: ActionCommand) -> ActionExecutionResult:
        payload = command.payload or {}
        export_format = payload.get("format")

        if not export_format:
            raise ValueError("payload.format is required for export_run")

        try:
            fmt = ExportFormat(str(export_format))
        except ValueError as exc:
            raise ValueError(f"unsupported export format: {export_format}") from exc

        artifact = self._delivery_service.create_export_artifact(
            run_id=command.run_id,
            format=fmt.value,
            force_regenerate=bool(payload.get("force_regenerate", False)),
        )

        audit_event_id = f"audit_export_{uuid4().hex}"

        return ActionExecutionResult(
            action_type=command.action_type,
            target_type="run",
            target_id=command.run_id,
            status=ActionExecutionStatus.SUCCESS,
            state_changes=[],
            side_effects=[
                {
                    "type": "export_artifact_created",
                    "artifact_id": artifact.id,
                    "format": artifact.format,
                    "file_name": artifact.file_name,
                },
                {
                    "type": "audit_event",
                    "audit_event_id": audit_event_id,
                    "action": "EXPORT_RUN",
                },
            ],
            audit_event_ids=[audit_event_id],
            response_payload={
                "run_id": command.run_id,
                "artifact_id": artifact.id,
                "export_status": artifact.status.value,
                "export_format": artifact.format,
                "content_type": artifact.content_type,
                "file_name": artifact.file_name,
                "byte_size": artifact.byte_size,
            },
        )