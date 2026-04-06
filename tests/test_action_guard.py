import pytest

from invomatch.services.actions.action_guard import (
    ALLOWED_ACTIONS_BY_STATE,
    InvalidActionForStateError,
    UnknownRunStateError,
    get_allowed_actions_for_state,
    is_action_allowed,
    validate_action_for_state,
)


def test_get_allowed_actions_for_known_state_returns_expected_actions() -> None:
    assert get_allowed_actions_for_state("completed") == frozenset({"export_run"})


def test_get_allowed_actions_for_unknown_state_raises() -> None:
    with pytest.raises(UnknownRunStateError) as exc:
        get_allowed_actions_for_state("mystery_state")

    assert "mystery_state" in str(exc.value)


@pytest.mark.parametrize(
    ("run_state", "action_type"),
    [
        ("review_required", "resolve_review"),
        ("completed", "export_run"),
    ],
)
def test_is_action_allowed_returns_true_for_valid_pairs(
    run_state: str,
    action_type: str,
) -> None:
    assert is_action_allowed(run_state, action_type) is True


@pytest.mark.parametrize(
    ("run_state", "action_type"),
    [
        ("queued", "resolve_review"),
        ("queued", "export_run"),
        ("processing", "export_run"),
        ("processing", "resolve_review"),
        ("review_required", "export_run"),
        ("completed", "resolve_review"),
        ("failed", "export_run"),
        ("cancelled", "resolve_review"),
    ],
)
def test_is_action_allowed_returns_false_for_invalid_pairs(
    run_state: str,
    action_type: str,
) -> None:
    assert is_action_allowed(run_state, action_type) is False


def test_validate_action_for_state_allows_valid_action() -> None:
    validate_action_for_state("completed", "export_run")
    validate_action_for_state("review_required", "resolve_review")


@pytest.mark.parametrize(
    ("run_state", "action_type"),
    [
        ("processing", "export_run"),
        ("processing", "resolve_review"),
        ("completed", "resolve_review"),
        ("review_required", "export_run"),
        ("cancelled", "export_run"),
    ],
)
def test_validate_action_for_state_rejects_invalid_action(
    run_state: str,
    action_type: str,
) -> None:
    with pytest.raises(InvalidActionForStateError) as exc:
        validate_action_for_state(run_state, action_type)

    assert run_state in str(exc.value)
    assert action_type in str(exc.value)


def test_allowed_action_map_has_only_contract_states() -> None:
    assert set(ALLOWED_ACTIONS_BY_STATE.keys()) == {
        "queued",
        "processing",
        "review_required",
        "completed",
        "failed",
        "cancelled",
    }