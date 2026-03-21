from invomatch.domain.models import RunStatus


class InvalidRunStateTransition(ValueError):
    pass


ALLOWED_TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    "pending": {"pending", "running", "failed"},
    "running": {"running", "completed", "failed"},
    "completed": {"completed"},
    "failed": {"failed"},
}


def assert_transition_allowed(current: RunStatus, target: RunStatus) -> None:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise InvalidRunStateTransition(
            f"Invalid transition {current} -> {target}"
        )
