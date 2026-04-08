from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FailureCategory(str, Enum):
    EXECUTION_FAILURE = "execution_failure"
    ORCHESTRATION_FAILURE = "orchestration_failure"
    DEPENDENCY_FAILURE = "dependency_failure"
    PERSISTENCE_FAILURE = "persistence_failure"
    RETRY_EXHAUSTED = "retry_exhausted"
    UNEXPECTED_INTERNAL_ERROR = "unexpected_internal_error"


@dataclass(frozen=True, slots=True)
class RuntimeFailure:
    category: FailureCategory
    code: str
    message: str
    is_retryable: bool
    is_terminal: bool
    operation_name: str | None = None
    dependency_name: str | None = None

    def to_error_dict(self) -> dict[str, str]:
        payload = {
            "category": self.category.value,
            "code": self.code,
            "message": self.message,
        }
        if self.operation_name is not None:
            payload["operation_name"] = self.operation_name
        if self.dependency_name is not None:
            payload["dependency_name"] = self.dependency_name
        return payload


class RuntimeExecutionError(Exception):
    """Canonical business/runtime execution failure."""


class RuntimeOrchestrationError(Exception):
    """Runtime coordination or orchestration failure."""


class RuntimeDependencyError(Exception):
    """Required dependency unavailable or degraded beyond safe tolerance."""

    def __init__(self, message: str, *, dependency_name: str | None = None) -> None:
        super().__init__(message)
        self.dependency_name = dependency_name


class RuntimePersistenceError(Exception):
    """Canonical persistence failure for runtime-critical state."""


class RuntimeRetryExhaustedError(Exception):
    """Raised when retry policy is exhausted for a retryable failure."""


def normalize_exception_to_failure(
    exc: Exception,
    *,
    operation_name: str | None = None,
) -> RuntimeFailure:
    if isinstance(exc, RuntimeDependencyError):
        return RuntimeFailure(
            category=FailureCategory.DEPENDENCY_FAILURE,
            code="dependency_unavailable",
            message=str(exc),
            is_retryable=True,
            is_terminal=False,
            operation_name=operation_name,
            dependency_name=exc.dependency_name,
        )

    if isinstance(exc, RuntimePersistenceError):
        return RuntimeFailure(
            category=FailureCategory.PERSISTENCE_FAILURE,
            code="persistence_failure",
            message=str(exc),
            is_retryable=True,
            is_terminal=False,
            operation_name=operation_name,
        )

    if isinstance(exc, RuntimeExecutionError):
        return RuntimeFailure(
            category=FailureCategory.EXECUTION_FAILURE,
            code="execution_failure",
            message=str(exc),
            is_retryable=False,
            is_terminal=True,
            operation_name=operation_name,
        )

    if isinstance(exc, RuntimeOrchestrationError):
        return RuntimeFailure(
            category=FailureCategory.ORCHESTRATION_FAILURE,
            code="orchestration_failure",
            message=str(exc),
            is_retryable=False,
            is_terminal=True,
            operation_name=operation_name,
        )

    if isinstance(exc, RuntimeRetryExhaustedError):
        return RuntimeFailure(
            category=FailureCategory.RETRY_EXHAUSTED,
            code="retry_exhausted",
            message=str(exc),
            is_retryable=False,
            is_terminal=True,
            operation_name=operation_name,
        )

    return RuntimeFailure(
        category=FailureCategory.UNEXPECTED_INTERNAL_ERROR,
        code="unexpected_internal_error",
        message=str(exc),
        is_retryable=False,
        is_terminal=True,
        operation_name=operation_name,
    )