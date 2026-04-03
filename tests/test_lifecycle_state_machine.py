from invomatch.services.lifecycle.state_machine import RunStateMachine


def test_valid_states_are_recognized():
    assert RunStateMachine.is_valid_state("queued")
    assert RunStateMachine.is_valid_state("processing")
    assert not RunStateMachine.is_valid_state("unknown")


def test_terminal_states_are_recognized():
    assert RunStateMachine.is_terminal("completed")
    assert RunStateMachine.is_terminal("failed")
    assert not RunStateMachine.is_terminal("processing")


def test_allowed_transition_is_true():
    assert RunStateMachine.can_transition("queued", "processing")


def test_disallowed_transition_is_false():
    assert not RunStateMachine.can_transition("queued", "completed")