from __future__ import annotations

from dataclasses import dataclass

from invomatch.runtime.runtime_failure import FailureCategory, RuntimeFailure


@dataclass(frozen=True, slots=True)
class RuntimeRetryDecision:
    should_retry: bool
    should_terminalize: bool
    reason: str


@dataclass(frozen=True, slots=True)
class RuntimeRetryPolicy:
    max_attempts: int = 3

    def evaluate(self, failure: RuntimeFailure, *, attempt: int) -> RuntimeRetryDecision:
        if failure.is_terminal:
            return RuntimeRetryDecision(
                should_retry=False,
                should_terminalize=True,
                reason="terminal_failure",
            )

        if not failure.is_retryable:
            return RuntimeRetryDecision(
                should_retry=False,
                should_terminalize=True,
                reason="non_retryable_failure",
            )

        if attempt >= self.max_attempts:
            return RuntimeRetryDecision(
                should_retry=False,
                should_terminalize=True,
                reason="retry_exhausted",
            )

        return RuntimeRetryDecision(
            should_retry=True,
            should_terminalize=False,
            reason="retry_allowed",
        )


def default_runtime_retry_policy() -> RuntimeRetryPolicy:
    return RuntimeRetryPolicy(max_attempts=3)


def should_reenter_after_failure(
    *,
    run_status: str,
    lease_is_valid: bool,
    last_failure: RuntimeFailure,
) -> bool:
    if run_status != "processing":
        return False

    if lease_is_valid:
        return False

    if last_failure.category in {
        FailureCategory.PERSISTENCE_FAILURE,
        FailureCategory.ORCHESTRATION_FAILURE,
        FailureCategory.UNEXPECTED_INTERNAL_ERROR,
    }:
        return False

    return last_failure.is_retryable and not last_failure.is_terminal