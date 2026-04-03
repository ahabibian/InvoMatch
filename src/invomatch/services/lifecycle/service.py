from __future__ import annotations

from invomatch.services.lifecycle.errors import (
    InvalidRunStateError,
    InvalidRunTransitionError,
    TerminalRunStateError,
)
from invomatch.services.lifecycle.state_machine import RunStateMachine


class RunLifecycleService:
    @staticmethod
    def validate_transition(current_state: str, target_state: str) -> None:
        if not RunStateMachine.is_valid_state(current_state):
            raise InvalidRunStateError(f"Unknown current run state '{current_state}'.")

        if not RunStateMachine.is_valid_state(target_state):
            raise InvalidRunStateError(f"Unknown target run state '{target_state}'.")

        if RunStateMachine.is_terminal(current_state):
            raise TerminalRunStateError(
                f"Run state '{current_state}' is terminal and cannot transition."
            )

        if not RunStateMachine.can_transition(current_state, target_state):
            raise InvalidRunTransitionError(
                f"Illegal run state transition: '{current_state}' -> '{target_state}'."
            )

    @classmethod
    def transition(cls, run, target_state: str):
        current_state = run.status
        cls.validate_transition(current_state, target_state)
        run.status = target_state
        return run