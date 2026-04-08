from invomatch.domain.operational.models import (
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
)
from invomatch.services.operational.recovery_eligibility_policy import (
    RecoveryEligibilityInput,
)
from invomatch.services.operational.recovery_loop_service import (
    InMemoryRecoveryIncidentTracker,
    RecoveryCandidate,
    RecoveryLoopService,
)


def test_recoverable_failure_triggers_retry_once() -> None:
    calls: list[str] = []

    service = RecoveryLoopService(
        retry_executor=lambda run_id: calls.append(run_id),
    )

    candidate = RecoveryCandidate(
        run_id="run-1",
        incident_key="failure-1",
        eligibility=RecoveryEligibilityInput(
            business_status="failed",
            retry_count=0,
            retry_limit=3,
            failure_code="runtime_error",
            failure_is_recoverable=True,
        ),
    )

    result = service.process(candidate)

    assert result.decision == OperationalDecision.RETRY_TRIGGERED
    assert result.reason_code == OperationalReasonCode.RECOVERABLE_FAILURE
    assert result.target_condition == OperationalCondition.RETRY_PENDING
    assert result.action_taken is True
    assert result.action_name == "retry"
    assert calls == ["run-1"]


def test_stuck_run_triggers_reentry() -> None:
    calls: list[str] = []

    service = RecoveryLoopService(
        reentry_executor=lambda run_id: calls.append(run_id),
    )

    candidate = RecoveryCandidate(
        run_id="run-2",
        incident_key="stuck-1",
        eligibility=RecoveryEligibilityInput(
            business_status="processing",
            retry_count=0,
            retry_limit=2,
            stuck_detected=True,
        ),
    )

    result = service.process(candidate)

    assert result.decision == OperationalDecision.REENTRY_TRIGGERED
    assert result.reason_code == OperationalReasonCode.STUCK_PROCESSING
    assert result.target_condition == OperationalCondition.REENTRY_PENDING
    assert result.action_taken is True
    assert result.action_name == "reentry"
    assert calls == ["run-2"]


def test_same_incident_is_noop_on_second_processing() -> None:
    tracker = InMemoryRecoveryIncidentTracker()
    calls: list[str] = []

    service = RecoveryLoopService(
        incident_tracker=tracker,
        retry_executor=lambda run_id: calls.append(run_id),
    )

    candidate = RecoveryCandidate(
        run_id="run-3",
        incident_key="failure-2",
        eligibility=RecoveryEligibilityInput(
            business_status="failed",
            retry_count=0,
            retry_limit=2,
            failure_code="runtime_error",
            failure_is_recoverable=True,
        ),
    )

    first = service.process(candidate)
    second = service.process(candidate)

    assert first.decision == OperationalDecision.RETRY_TRIGGERED
    assert second.decision == OperationalDecision.ALREADY_RECOVERED_NOOP
    assert second.reason_code == OperationalReasonCode.ALREADY_RECOVERED_SAME_INCIDENT
    assert second.action_taken is False
    assert calls == ["run-3"]


def test_ineligible_candidate_is_marked_without_action() -> None:
    calls: list[str] = []

    service = RecoveryLoopService(
        retry_executor=lambda run_id: calls.append(run_id),
    )

    candidate = RecoveryCandidate(
        run_id="run-4",
        incident_key="failure-3",
        eligibility=RecoveryEligibilityInput(
            business_status="completed",
            retry_count=0,
            retry_limit=3,
            failure_is_recoverable=True,
        ),
    )

    result = service.process(candidate)

    assert result.decision == OperationalDecision.CANDIDATE_REJECTED
    assert result.reason_code == OperationalReasonCode.TERMINAL_BUSINESS_STATE
    assert result.action_taken is False
    assert calls == []


def test_failed_revalidation_blocks_action() -> None:
    calls: list[str] = []

    service = RecoveryLoopService(
        retry_executor=lambda run_id: calls.append(run_id),
        revalidate_candidate=lambda candidate: False,
    )

    candidate = RecoveryCandidate(
        run_id="run-5",
        incident_key="failure-4",
        eligibility=RecoveryEligibilityInput(
            business_status="failed",
            retry_count=1,
            retry_limit=3,
            failure_code="runtime_error",
            failure_is_recoverable=True,
        ),
    )

    result = service.process(candidate)

    assert result.decision == OperationalDecision.CANDIDATE_REJECTED
    assert result.reason_code == OperationalReasonCode.CANDIDATE_STATE_CHANGED
    assert result.target_condition == OperationalCondition.RECOVERY_SKIPPED
    assert result.action_taken is False
    assert calls == []


def test_exhausted_retry_budget_returns_terminal_without_action() -> None:
    calls: list[str] = []

    service = RecoveryLoopService(
        retry_executor=lambda run_id: calls.append(run_id),
    )

    candidate = RecoveryCandidate(
        run_id="run-6",
        incident_key="failure-5",
        eligibility=RecoveryEligibilityInput(
            business_status="failed",
            retry_count=3,
            retry_limit=3,
            failure_code="runtime_error",
            failure_is_recoverable=True,
        ),
    )

    result = service.process(candidate)

    assert result.decision == OperationalDecision.TERMINAL_CONFIRMED
    assert result.reason_code == OperationalReasonCode.RETRY_BUDGET_EXHAUSTED
    assert result.target_condition == OperationalCondition.RECOVERY_EXHAUSTED
    assert result.action_taken is False
    assert calls == []