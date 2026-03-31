from __future__ import annotations

from dataclasses import dataclass

from invomatch.api.product_models.action import ProductActionRequest
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.dispatcher import ActionDispatcher
from invomatch.services.actions.execution_service import ActionExecutionService
from invomatch.services.actions.handlers.resolve_review import ResolveReviewActionHandler
from invomatch.services.actions.result import ActionExecutionStatus


@dataclass(slots=True)
class ActionExecutionResult:
    run_id: str
    action_type: str
    accepted: bool
    status: str
    message: str | None = None


class ActionService:
    """
    Product-facing action dispatcher.

    EPIC 7 integration scope:
    - preserve product-facing contract behavior
    - route resolve_review through the real review decision handler
    - keep export_run as placeholder until export workflow is implemented
    """

    SUPPORTED_ACTIONS = {
        "resolve_review",
        "export_run",
    }

    def __init__(self) -> None:
        dispatcher = ActionDispatcher()
        dispatcher.register("resolve_review", ResolveReviewActionHandler)
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

        if action_type == "resolve_review":
            command = ActionCommand(
                action_type=action_type,
                run_id=run_id,
                target_id=request.target_id,
                payload=request.payload or {},
                note=request.note,
            )

            try:
                result = self._execution_service.execute(command)
            except ValueError as exc:
                return ActionExecutionResult(
                    run_id=run_id,
                    action_type=action_type,
                    accepted=False,
                    status="invalid_request",
                    message=str(exc),
                )

            if result.status in {ActionExecutionStatus.SUCCESS, ActionExecutionStatus.NO_OP}:
                return ActionExecutionResult(
                    run_id=run_id,
                    action_type=action_type,
                    accepted=True,
                    status="accepted",
                    message="Review decision applied.",
                )

            if result.status == ActionExecutionStatus.CONFLICT:
                return ActionExecutionResult(
                    run_id=run_id,
                    action_type=action_type,
                    accepted=False,
                    status="conflict",
                    message="Review decision conflicts with current state.",
                )

            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=False,
                status="failed",
                message="Review decision could not be applied.",
            )

        if action_type == "export_run":
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=True,
                status="accepted",
                message="Export action accepted for processing.",
            )

        return ActionExecutionResult(
            run_id=run_id,
            action_type=action_type,
            accepted=False,
            status="unsupported_action",
            message=f"Unsupported action type: {action_type}",
        )