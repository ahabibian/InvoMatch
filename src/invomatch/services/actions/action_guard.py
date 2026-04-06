from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Mapping


ALLOWED_ACTIONS_BY_STATE: Mapping[str, FrozenSet[str]] = {
    "queued": frozenset(),
    "processing": frozenset(),
    "review_required": frozenset({"resolve_review"}),
    "completed": frozenset({"export_run"}),
    "failed": frozenset(),
    "cancelled": frozenset(),
}


@dataclass(frozen=True)
class InvalidActionForStateError(Exception):
    run_state: str
    action_type: str

    def __str__(self) -> str:
        return (
            f"Action '{self.action_type}' is not allowed when run state is "
            f"'{self.run_state}'."
        )


@dataclass(frozen=True)
class UnknownRunStateError(Exception):
    run_state: str

    def __str__(self) -> str:
        return f"Unknown run state: '{self.run_state}'."


def get_allowed_actions_for_state(run_state: str) -> FrozenSet[str]:
    if run_state not in ALLOWED_ACTIONS_BY_STATE:
        raise UnknownRunStateError(run_state=run_state)

    return ALLOWED_ACTIONS_BY_STATE[run_state]


def is_action_allowed(run_state: str, action_type: str) -> bool:
    allowed_actions = get_allowed_actions_for_state(run_state)
    return action_type in allowed_actions


def validate_action_for_state(run_state: str, action_type: str) -> None:
    if not is_action_allowed(run_state=run_state, action_type=action_type):
        raise InvalidActionForStateError(
            run_state=run_state,
            action_type=action_type,
        )