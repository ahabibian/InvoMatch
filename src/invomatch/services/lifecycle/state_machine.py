from __future__ import annotations

from typing import Final


class RunStateMachine:
    VALID_STATES: Final[set[str]] = {
        "queued",
        "processing",
        "review_required",
        "completed",
        "failed",
        "cancelled",
    }

    TERMINAL_STATES: Final[set[str]] = {
        "completed",
        "failed",
        "cancelled",
    }

    TRANSITIONS: Final[dict[str, set[str]]] = {
        "queued": {"processing", "failed", "cancelled"},
        "processing": {"review_required", "completed", "failed", "cancelled"},
        "review_required": {"completed", "failed", "cancelled"},
        "completed": set(),
        "failed": set(),
        "cancelled": set(),
    }

    @classmethod
    def is_valid_state(cls, state: str) -> bool:
        return state in cls.VALID_STATES

    @classmethod
    def is_terminal(cls, state: str) -> bool:
        return state in cls.TERMINAL_STATES

    @classmethod
    def can_transition(cls, current_state: str, target_state: str) -> bool:
        if current_state not in cls.VALID_STATES:
            return False
        if target_state not in cls.VALID_STATES:
            return False
        return target_state in cls.TRANSITIONS[current_state]