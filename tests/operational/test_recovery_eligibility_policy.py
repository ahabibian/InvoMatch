from invomatch.domain.operational.models import (
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
)
from invomatch.services.operational.recovery_eligibility_policy import (
    RecoveryEligibilityInput,
    RecoveryEligibilityPolicy,
)


def test_recoverable_failure_is_retry_eligible() -> None:
    policy = RecoveryEligibilityPolicy()

    result = policy.evaluate(
        RecoveryEligibilityInput(
            business_status="failed",
            retry_count=1,
            retry_limit=3,
            failure_code="runtime_error",
            failure_is_recoverable=True,
        )
    )

    assert result.is_eligible is True
    assert result.decision == OperationalDecision.ELIGIBLE
    assert result.reason_code == OperationalReasonCode.RECOVERABLE_FAILURE
    assert result.target_condition == OperationalCondition.RETRY_PENDING


def test_stuck_run_is_reentry_eligible() -> None:
    policy = RecoveryEligibilityPolicy()

    result = policy.evaluate(
        RecoveryEligibilityInput(
            business_status="processing",
            retry_count=0,
            retry_limit=2,
            stuck_detected=True,
        )
    )

    assert result.is_eligible is True
    assert result.reason_code == OperationalReasonCode.STUCK_PROCESSING
    assert result.target_condition == OperationalCondition.REENTRY_PENDING


def test_retry_budget_exhaustion_becomes_terminal_operational_outcome() -> None:
    policy = RecoveryEligibilityPolicy()

    result = policy.evaluate(
        RecoveryEligibilityInput(
            business_status="failed",
            retry_count=3,
            retry_limit=3,
            failure_code="runtime_error",
            failure_is_recoverable=True,
        )
    )

    assert result.is_eligible is False
    assert result.decision == OperationalDecision.TERMINAL_CONFIRMED
    assert result.reason_code == OperationalReasonCode.RETRY_BUDGET_EXHAUSTED
    assert result.target_condition == OperationalCondition.RECOVERY_EXHAUSTED


def test_completed_run_is_not_recoverable() -> None:
    policy = RecoveryEligibilityPolicy()

    result = policy.evaluate(
        RecoveryEligibilityInput(
            business_status="completed",
            retry_count=0,
            retry_limit=3,
            failure_is_recoverable=True,
        )
    )

    assert result.is_eligible is False
    assert result.reason_code == OperationalReasonCode.TERMINAL_BUSINESS_STATE


def test_active_recovery_blocks_duplicate_recovery() -> None:
    policy = RecoveryEligibilityPolicy()

    result = policy.evaluate(
        RecoveryEligibilityInput(
            business_status="failed",
            retry_count=0,
            retry_limit=3,
            failure_is_recoverable=True,
            active_recovery_in_progress=True,
        )
    )

    assert result.is_eligible is False
    assert result.decision == OperationalDecision.RECOVERY_SKIPPED
    assert result.reason_code == OperationalReasonCode.ACTIVE_RECOVERY_IN_PROGRESS


def test_non_recoverable_failure_without_stuck_signal_is_rejected() -> None:
    policy = RecoveryEligibilityPolicy()

    result = policy.evaluate(
        RecoveryEligibilityInput(
            business_status="failed",
            retry_count=0,
            retry_limit=3,
            failure_code="validation_error",
            failure_is_recoverable=False,
            stuck_detected=False,
        )
    )

    assert result.is_eligible is False
    assert result.decision == OperationalDecision.CANDIDATE_REJECTED
    assert result.reason_code == OperationalReasonCode.NO_FAILURE_OR_STUCK_SIGNAL