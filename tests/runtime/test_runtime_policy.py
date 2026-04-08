from invomatch.runtime.runtime_failure import (
    FailureCategory,
    RuntimeFailure,
)
from invomatch.runtime.runtime_policy import (
    RuntimeRetryPolicy,
    should_reenter_after_failure,
)


def _failure(
    *,
    category: FailureCategory,
    is_retryable: bool,
    is_terminal: bool,
) -> RuntimeFailure:
    return RuntimeFailure(
        category=category,
        code="test_code",
        message="test message",
        is_retryable=is_retryable,
        is_terminal=is_terminal,
    )


def test_retry_policy_allows_retry_for_retryable_non_terminal_failure_before_limit():
    policy = RuntimeRetryPolicy(max_attempts=3)
    failure = _failure(
        category=FailureCategory.DEPENDENCY_FAILURE,
        is_retryable=True,
        is_terminal=False,
    )

    decision = policy.evaluate(failure, attempt=1)

    assert decision.should_retry is True
    assert decision.should_terminalize is False
    assert decision.reason == "retry_allowed"


def test_retry_policy_terminalizes_non_retryable_failure():
    policy = RuntimeRetryPolicy(max_attempts=3)
    failure = _failure(
        category=FailureCategory.EXECUTION_FAILURE,
        is_retryable=False,
        is_terminal=True,
    )

    decision = policy.evaluate(failure, attempt=1)

    assert decision.should_retry is False
    assert decision.should_terminalize is True
    assert decision.reason == "terminal_failure"


def test_retry_policy_terminalizes_when_attempt_limit_is_reached():
    policy = RuntimeRetryPolicy(max_attempts=3)
    failure = _failure(
        category=FailureCategory.DEPENDENCY_FAILURE,
        is_retryable=True,
        is_terminal=False,
    )

    decision = policy.evaluate(failure, attempt=3)

    assert decision.should_retry is False
    assert decision.should_terminalize is True
    assert decision.reason == "retry_exhausted"


def test_reentry_requires_processing_status():
    failure = _failure(
        category=FailureCategory.DEPENDENCY_FAILURE,
        is_retryable=True,
        is_terminal=False,
    )

    assert should_reenter_after_failure(
        run_status="review_required",
        lease_is_valid=False,
        last_failure=failure,
    ) is False


def test_reentry_requires_expired_or_invalid_lease():
    failure = _failure(
        category=FailureCategory.DEPENDENCY_FAILURE,
        is_retryable=True,
        is_terminal=False,
    )

    assert should_reenter_after_failure(
        run_status="processing",
        lease_is_valid=True,
        last_failure=failure,
    ) is False


def test_reentry_rejects_persistence_failure():
    failure = _failure(
        category=FailureCategory.PERSISTENCE_FAILURE,
        is_retryable=True,
        is_terminal=False,
    )

    assert should_reenter_after_failure(
        run_status="processing",
        lease_is_valid=False,
        last_failure=failure,
    ) is False


def test_reentry_allows_retryable_dependency_failure_after_lease_expiry():
    failure = _failure(
        category=FailureCategory.DEPENDENCY_FAILURE,
        is_retryable=True,
        is_terminal=False,
    )

    assert should_reenter_after_failure(
        run_status="processing",
        lease_is_valid=False,
        last_failure=failure,
    ) is True