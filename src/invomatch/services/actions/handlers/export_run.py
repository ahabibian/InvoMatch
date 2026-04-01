from __future__ import annotations

from uuid import uuid4

from invomatch.domain.export import ExportFormat
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.handlers.base import BaseActionHandler
from invomatch.services.actions.result import ActionExecutionResult, ActionExecutionStatus
from invomatch.services.export.export_service import ExportService


class ExportRunActionHandler(BaseActionHandler):
    def __init__(self, export_service: ExportService | None = None) -> None:
        self._export_service = export_service or ExportService()

    def handle(self, command: ActionCommand) -> ActionExecutionResult:
        payload = command.payload or {}
        export_format = payload.get("format")

        if not export_format:
            raise ValueError("payload.format is required for export_run")

        try:
            fmt = ExportFormat(str(export_format))
        except ValueError:
            raise ValueError(f"unsupported export format: {export_format}")

        result = self._export_service.export(
            run_id=command.run_id,
            export_format=fmt,
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
                    "type": "export_generated",
                    "format": fmt.value,
                    "filename": result.filename,
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
                "export_status": "completed",
                "export_format": fmt.value,
                "content_type": result.content_type,
                "filename": result.filename,
            },
        )
