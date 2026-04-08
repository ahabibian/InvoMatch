from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from invomatch.domain.operational.models import (
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
    RecoveryEvaluationResult,
)
from invomatch.services.operational.retry_budget_policy import RetryBudgetPolicy


_TERMINAL_BUSINESS_STATES = {"completed", "cancelled"}


@dataclass(frozen=True, slots=True)
class RecoveryEligibilityInput:
    business_status: str
    retry_count: int
    retry_limit: int
    failure_code: Optional[str] = None
    failure_is_recoverable: bool = False
    stuck_detected: bool = False
    active_recovery_in_progress: bool = False
    has_valid_lease: bool = False
    already_recovered_same_incident: bool = False
    manually_cancelled: bool = False
    terminal_failure_confirmed: bool = False
    candidate_state_changed: bool = False
    lifecycle_allows_recovery: bool = True


class RecoveryEligibilityPolicy:
    def __init__(self, retry_budget_policy: RetryBudgetPolicy | None = None) -> None:
        self._retry_budget_policy = retry_budget_policy or RetryBudgetPolicy()

    def evaluate(self, data: RecoveryEligibilityInput) -> RecoveryEvaluationResult:
        if data.business_status in _TERMINAL_BUSINESS_STATES:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.CANDIDATE_REJECTED,
                reason_code=OperationalReasonCode.TERMINAL_BUSINESS_STATE,
                target_condition=OperationalCondition.TERMINAL_CONFIRMED,
            )

        if data.manually_cancelled:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.CANDIDATE_REJECTED,
                reason_code=OperationalReasonCode.MANUALLY_CANCELLED,
                target_condition=OperationalCondition.TERMINAL_CONFIRMED,
            )

        if data.terminal_failure_confirmed:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.TERMINAL_CONFIRMED,
                reason_code=OperationalReasonCode.TERMINAL_FAILURE_CONFIRMED,
                target_condition=OperationalCondition.TERMINAL_CONFIRMED,
            )

        if data.candidate_state_changed:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.CANDIDATE_REJECTED,
                reason_code=OperationalReasonCode.CANDIDATE_STATE_CHANGED,
                target_condition=OperationalCondition.RECOVERY_SKIPPED,
            )

        if not data.lifecycle_allows_recovery:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.CANDIDATE_REJECTED,
                reason_code=OperationalReasonCode.LIFECYCLE_BLOCKED,
                target_condition=OperationalCondition.RECOVERY_SKIPPED,
            )

        if data.active_recovery_in_progress:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.RECOVERY_SKIPPED,
                reason_code=OperationalReasonCode.ACTIVE_RECOVERY_IN_PROGRESS,
                target_condition=OperationalCondition.RECOVERY_SKIPPED,
            )

        if data.has_valid_lease:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.RECOVERY_SKIPPED,
                reason_code=OperationalReasonCode.VALID_LEASE_PRESENT,
                target_condition=OperationalCondition.RECOVERY_SKIPPED,
            )

        if data.already_recovered_same_incident:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.ALREADY_RECOVERED_NOOP,
                reason_code=OperationalReasonCode.ALREADY_RECOVERED_SAME_INCIDENT,
                target_condition=OperationalCondition.RECOVERY_SKIPPED,
            )

        if self._retry_budget_policy.is_exhausted(
            retry_count=data.retry_count,
            retry_limit=data.retry_limit,
        ):
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.TERMINAL_CONFIRMED,
                reason_code=OperationalReasonCode.RETRY_BUDGET_EXHAUSTED,
                target_condition=OperationalCondition.RECOVERY_EXHAUSTED,
            )

        has_recoverable_signal = data.failure_is_recoverable or data.stuck_detected
        if not has_recoverable_signal:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.CANDIDATE_REJECTED,
                reason_code=OperationalReasonCode.NO_FAILURE_OR_STUCK_SIGNAL,
                target_condition=OperationalCondition.RECOVERY_SKIPPED,
            )

        if data.stuck_detected:
            return RecoveryEvaluationResult(
                is_eligible=True,
                decision=OperationalDecision.ELIGIBLE,
                reason_code=OperationalReasonCode.STUCK_PROCESSING,
                target_condition=OperationalCondition.REENTRY_PENDING,
            )

        if not data.failure_is_recoverable:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.CANDIDATE_REJECTED,
                reason_code=OperationalReasonCode.FAILURE_NOT_RECOVERABLE,
                target_condition=OperationalCondition.TERMINAL_CONFIRMED,
            )

        return RecoveryEvaluationResult(
            is_eligible=True,
            decision=OperationalDecision.ELIGIBLE,
            reason_code=OperationalReasonCode.RECOVERABLE_FAILURE,
            target_condition=OperationalCondition.RETRY_PENDING,
        )