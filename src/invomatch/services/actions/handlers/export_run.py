from __future__ import annotations

from uuid import uuid4

from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.handlers.base import BaseActionHandler
from invomatch.services.actions.result import ActionExecutionResult, ActionExecutionStatus
from invomatch.services.export.export_workflow import ExportWorkflowService


class ExportRunActionHandler(BaseActionHandler):
    def __init__(self, workflow: ExportWorkflowService | None = None) -> None:
        self._workflow = workflow or ExportWorkflowService()

    def handle(self, command: ActionCommand) -> ActionExecutionResult:
        payload = command.payload or {}
        export_format = payload.get("format")

        if not export_format:
            raise ValueError("payload.format is required for export_run")

        result = self._workflow.execute(
            run_id=command.run_id,
            export_format=str(export_format),
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
                    "format": result.export_format,
                    "artifact_path": result.artifact_path,
                },
                {
                    "type": "audit_event",
                    "audit_event_id": audit_event_id,
                    "action": "EXPORT_RUN",
                },
            ],
            audit_event_ids=[audit_event_id],
            response_payload={
                "run_id": result.run_id,
                "export_status": result.export_status,
                "export_format": result.export_format,
                "artifact_path": result.artifact_path,
            },
        )