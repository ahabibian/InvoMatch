from __future__ import annotations

from invomatch.services.lifecycle.errors import LifecycleOperationNotAllowedError
from invomatch.services.lifecycle.state_machine import RunStateMachine


class RunLifecycleGuards:
    @staticmethod
    def require_export_allowed(state: str) -> None:
        if state != "completed":
            raise LifecycleOperationNotAllowedError(
                f"Export is not allowed for run state '{state}'."
            )

    @staticmethod
    def require_review_resolution_allowed(state: str) -> None:
        if state != "review_required":
            raise LifecycleOperationNotAllowedError(
                f"Review resolution is not allowed for run state '{state}'."
            )

    @staticmethod
    def require_processing_start_allowed(state: str) -> None:
        if state != "queued":
            raise LifecycleOperationNotAllowedError(
                f"Processing start is not allowed for run state '{state}'."
            )

    @staticmethod
    def require_cancellation_allowed(state: str) -> None:
        if RunStateMachine.is_terminal(state):
            raise LifecycleOperationNotAllowedError(
                f"Cancellation is not allowed for terminal run state '{state}'."
            )