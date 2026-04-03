import pytest

from invomatch.services.lifecycle.errors import (
    InvalidRunTransitionError,
    TerminalRunStateError,
)
from invomatch.services.lifecycle.service import RunLifecycleService


class DummyRun:
    def __init__(self, status: str):
        self.status = status


def test_transition_updates_run_status():
    run = DummyRun("queued")
    updated = RunLifecycleService.transition(run, "processing")
    assert updated.status == "processing"


def test_illegal_transition_raises():
    run = DummyRun("queued")
    with pytest.raises(InvalidRunTransitionError):
        RunLifecycleService.transition(run, "completed")


def test_terminal_state_transition_raises():
    run = DummyRun("completed")
    with pytest.raises(TerminalRunStateError):
        RunLifecycleService.transition(run, "failed")