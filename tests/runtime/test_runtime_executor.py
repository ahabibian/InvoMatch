import pytest

from invomatch.runtime.runtime_executor import (
    RuntimeExecutionTerminalError,
    RuntimeExecutor,
)
from invomatch.runtime.runtime_failure import (
    FailureCategory,
    RuntimeDependencyError,
    RuntimeExecutionError,
)
from invomatch.runtime.runtime_policy import RuntimeRetryPolicy


def test_runtime_executor_returns_value_on_first_success():
    executor = RuntimeExecutor()

    result = executor.execute(lambda: "ok", operation_name="demo_operation")

    assert result.value == "ok"
    assert result.attempts_used == 1


def test_runtime_executor_retries_retryable_failure_then_succeeds():
    executor = RuntimeExecutor(retry_policy=RuntimeRetryPolicy(max_attempts=3))
    attempts = {"count": 0}

    def flaky_operation():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeDependencyError(
                "temporary dependency issue",
                dependency_name="projection",
            )
        return "recovered"

    result = executor.execute(flaky_operation, operation_name="build_projection")

    assert result.value == "recovered"
    assert result.attempts_used == 3
    assert attempts["count"] == 3


def test_runtime_executor_terminalizes_non_retryable_failure_without_retry():
    executor = RuntimeExecutor(retry_policy=RuntimeRetryPolicy(max_attempts=3))
    attempts = {"count": 0}

    def invalid_operation():
        attempts["count"] += 1
        raise RuntimeExecutionError("illegal execution precondition")

    with pytest.raises(RuntimeExecutionTerminalError) as exc_info:
        executor.execute(invalid_operation, operation_name="execute_run")

    error = exc_info.value
    assert error.failure.category == FailureCategory.EXECUTION_FAILURE
    assert error.failure.code == "execution_failure"
    assert error.attempts_used == 1
    assert attempts["count"] == 1


def test_runtime_executor_terminalizes_after_retry_exhaustion():
    executor = RuntimeExecutor(retry_policy=RuntimeRetryPolicy(max_attempts=3))
    attempts = {"count": 0}

    def always_fails():
        attempts["count"] += 1
        raise RuntimeDependencyError(
            "dependency unavailable",
            dependency_name="export",
        )

    with pytest.raises(RuntimeExecutionTerminalError) as exc_info:
        executor.execute(always_fails, operation_name="generate_export")

    error = exc_info.value
    assert error.failure.category == FailureCategory.RETRY_EXHAUSTED
    assert error.failure.code == "retry_exhausted"
    assert error.attempts_used == 3
    assert attempts["count"] == 3


def test_runtime_executor_preserves_operation_name_in_terminal_failure():
    executor = RuntimeExecutor(retry_policy=RuntimeRetryPolicy(max_attempts=2))

    def explode():
        raise RuntimeExecutionError("hard failure")

    with pytest.raises(RuntimeExecutionTerminalError) as exc_info:
        executor.execute(explode, operation_name="run_finalize")

    error = exc_info.value
    assert error.failure.operation_name == "run_finalize"