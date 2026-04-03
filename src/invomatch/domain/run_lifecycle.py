from invomatch.domain.models import RunStatus


class InvalidRunStateTransition(ValueError):
    pass


ALLOWED_TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    "queued": {"processing", "failed", "cancelled"},
    "processing": {"review_required", "completed", "failed", "cancelled"},
    "review_required": {"completed", "failed", "cancelled"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
}


def assert_transition_allowed(current: RunStatus, target: RunStatus) -> None:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise InvalidRunStateTransition(
            f"Invalid transition {current} -> {target}"
        )