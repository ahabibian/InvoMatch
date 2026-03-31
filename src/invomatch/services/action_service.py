from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from invomatch.api.product_models.action import ProductActionRequest


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

    Current scope:
    - validate supported product action types
    - provide deterministic execution results
    - avoid leaking internal command or domain mutation details

    This version intentionally keeps side effects minimal until
    dedicated write-path integrations are introduced.
    """

    SUPPORTED_ACTIONS = {
        "resolve_review",
        "export_run",
    }

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
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=True,
                status="accepted",
                message="Review action accepted for processing.",
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