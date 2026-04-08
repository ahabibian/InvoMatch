from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar

from invomatch.runtime.runtime_failure import (
    RuntimeFailure,
    RuntimeRetryExhaustedError,
    normalize_exception_to_failure,
)
from invomatch.runtime.runtime_policy import (
    RuntimeRetryPolicy,
    default_runtime_retry_policy,
)

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RuntimeExecutionResult(Generic[T]):
    value: T
    attempts_used: int


class RuntimeExecutionTerminalError(Exception):
    def __init__(self, failure: RuntimeFailure, *, attempts_used: int) -> None:
        super().__init__(failure.message)
        self.failure = failure
        self.attempts_used = attempts_used


class RuntimeExecutor:
    def __init__(self, retry_policy: RuntimeRetryPolicy | None = None) -> None:
        self._retry_policy = retry_policy or default_runtime_retry_policy()

    def execute(
        self,
        operation: Callable[[], T],
        *,
        operation_name: str | None = None,
    ) -> RuntimeExecutionResult[T]:
        attempt = 1
        last_failure: RuntimeFailure | None = None

        while True:
            try:
                value = operation()
                return RuntimeExecutionResult(value=value, attempts_used=attempt)

            except Exception as exc:
                failure = normalize_exception_to_failure(
                    exc,
                    operation_name=operation_name,
                )
                last_failure = failure

                decision = self._retry_policy.evaluate(failure, attempt=attempt)

                if decision.should_retry:
                    attempt += 1
                    continue

                if decision.reason == "retry_exhausted":
                    exhausted_failure = normalize_exception_to_failure(
                        RuntimeRetryExhaustedError(
                            f"retry limit reached for operation: {operation_name or 'unknown_operation'}"
                        ),
                        operation_name=operation_name,
                    )
                    raise RuntimeExecutionTerminalError(
                        exhausted_failure,
                        attempts_used=attempt,
                    ) from exc

                raise RuntimeExecutionTerminalError(
                    last_failure,
                    attempts_used=attempt,
                ) from exc