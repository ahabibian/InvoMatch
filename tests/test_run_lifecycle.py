import pytest

from invomatch.domain.run_lifecycle import (
    InvalidRunStateTransition,
    assert_transition_allowed,
)


def test_valid_transition_pending_to_running():
    assert_transition_allowed("queued", "processing")


def test_valid_transition_running_to_completed():
    assert_transition_allowed("processing", "completed")


def test_invalid_transition_completed_to_running():
    with pytest.raises(InvalidRunStateTransition):
        assert_transition_allowed("completed", "processing")


def test_invalid_transition_failed_to_completed():
    with pytest.raises(InvalidRunStateTransition):
        assert_transition_allowed("failed", "completed")
