from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from invomatch.api.product_models.action import ProductActionRequest
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.dispatcher import ActionDispatcher
from invomatch.services.actions.execution_service import ActionExecutionService
from invomatch.services.actions.handlers.export_run import ExportRunActionHandler
from invomatch.services.actions.handlers.resolve_review import ResolveReviewActionHandler
from invomatch.services.actions.result import ActionExecutionStatus
from invomatch.services.export.export_workflow import ExportWorkflowService
from invomatch.services.export.export_writer import ExportWriter
from invomatch.services.run_store import RunStore


@dataclass(slots=True)
class ActionExecutionResult:
    run_id: str
    action_type: str
    accepted: bool
    status: str
    message: str | None = None


class ActionService:
    SUPPORTED_ACTIONS = {
        "resolve_review",
        "export_run",
    }

    def __init__(
        self,
        *,
        run_store: RunStore | None = None,
        export_base_dir: Path | None = None,
    ) -> None:
        dispatcher = ActionDispatcher()
        dispatcher.register("resolve_review", ResolveReviewActionHandler)

        export_workflow = ExportWorkflowService(
            run_store=run_store,
            writer=ExportWriter(export_base_dir),
        )
        dispatcher.register(
            "export_run",
            lambda: ExportRunActionHandler(workflow=export_workflow),
        )

        self._execution_service = ActionExecutionService(dispatcher)

    def execute(self, *, run_id: str, request: ProductActionRequest) -> ActionExecutionResult:
        action_type = str(request.action_type)

        if action_type not in self.SUPPORTED_ACTIONS:
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=False,
                status="unsupported_action",
                message=f"Unsupported action type: {action_type}",
            )

        command = ActionCommand(
            action_type=action_type,
            run_id=run_id,
            target_id=request.target_id,
            payload=request.payload or {},
            note=request.note,
        )

        try:
            result = self._execution_service.execute(command)
        except (ValueError, KeyError) as exc:
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=False,
                status="invalid_request",
                message=str(exc),
            )

        if result.status == ActionExecutionStatus.SUCCESS:
            message = "Action executed successfully."
            if action_type == "resolve_review":
                message = "Review decision applied."
            elif action_type == "export_run":
                message = f"Export generated (format={request.payload.get('format')})."
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=True,
                status="accepted",
                message=message,
            )

        if result.status == ActionExecutionStatus.NO_OP:
            message = "Action already applied."
            if action_type == "resolve_review":
                message = "Review decision already applied."
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=True,
                status="accepted",
                message=message,
            )

        if result.status == ActionExecutionStatus.CONFLICT:
            message = "Action conflicts with current state."
            if action_type == "resolve_review":
                message = "Review decision conflicts with current state."
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=False,
                status="conflict",
                message=message,
            )

        return ActionExecutionResult(
            run_id=run_id,
            action_type=action_type,
            accepted=False,
            status="failed",
            message="Action could not be completed.",
        )