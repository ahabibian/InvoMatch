from invomatch.runtime.runtime_failure import (
    FailureCategory,
    RuntimeDependencyError,
    RuntimeExecutionError,
    RuntimeOrchestrationError,
    RuntimePersistenceError,
    RuntimeRetryExhaustedError,
    normalize_exception_to_failure,
)


def test_normalize_dependency_error_is_retryable_and_non_terminal():
    failure = normalize_exception_to_failure(
        RuntimeDependencyError("export service unavailable", dependency_name="export"),
        operation_name="generate_export",
    )

    assert failure.category == FailureCategory.DEPENDENCY_FAILURE
    assert failure.code == "dependency_unavailable"
    assert failure.is_retryable is True
    assert failure.is_terminal is False
    assert failure.operation_name == "generate_export"
    assert failure.dependency_name == "export"


def test_normalize_persistence_error_is_retryable_and_non_terminal():
    failure = normalize_exception_to_failure(
        RuntimePersistenceError("failed to persist run update"),
        operation_name="persist_run_state",
    )

    assert failure.category == FailureCategory.PERSISTENCE_FAILURE
    assert failure.code == "persistence_failure"
    assert failure.is_retryable is True
    assert failure.is_terminal is False


def test_normalize_execution_error_is_terminal():
    failure = normalize_exception_to_failure(
        RuntimeExecutionError("illegal execution precondition"),
        operation_name="execute_run",
    )

    assert failure.category == FailureCategory.EXECUTION_FAILURE
    assert failure.code == "execution_failure"
    assert failure.is_retryable is False
    assert failure.is_terminal is True


def test_normalize_orchestration_error_is_terminal():
    failure = normalize_exception_to_failure(
        RuntimeOrchestrationError("post-step transition failed"),
        operation_name="advance_lifecycle",
    )

    assert failure.category == FailureCategory.ORCHESTRATION_FAILURE
    assert failure.code == "orchestration_failure"
    assert failure.is_retryable is False
    assert failure.is_terminal is True


def test_normalize_retry_exhausted_error_is_terminal():
    failure = normalize_exception_to_failure(
        RuntimeRetryExhaustedError("retry limit reached"),
        operation_name="runtime_execute",
    )

    assert failure.category == FailureCategory.RETRY_EXHAUSTED
    assert failure.code == "retry_exhausted"
    assert failure.is_retryable is False
    assert failure.is_terminal is True


def test_normalize_unknown_exception_defaults_to_unexpected_internal_error():
    failure = normalize_exception_to_failure(
        ValueError("unexpected boom"),
        operation_name="runtime_execute",
    )

    assert failure.category == FailureCategory.UNEXPECTED_INTERNAL_ERROR
    assert failure.code == "unexpected_internal_error"
    assert failure.is_retryable is False
    assert failure.is_terminal is True


def test_runtime_failure_to_error_dict_contains_required_fields():
    failure = normalize_exception_to_failure(
        RuntimeDependencyError("projection unavailable", dependency_name="projection"),
        operation_name="build_projection",
    )

    assert failure.to_error_dict() == {
        "category": "dependency_failure",
        "code": "dependency_unavailable",
        "message": "projection unavailable",
        "operation_name": "build_projection",
        "dependency_name": "projection",
    }