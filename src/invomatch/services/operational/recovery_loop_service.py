from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Protocol

from invomatch.domain.operational.models import (
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
)
from invomatch.services.operational.operational_audit import (
    OperationalAuditService,
    OperationalAuditWrite,
)
from invomatch.services.operational.operational_metrics import (
    InMemoryOperationalMetricsStore,
    OperationalMetricsService,
)
from invomatch.services.operational.recovery_eligibility_policy import (
    RecoveryEligibilityInput,
    RecoveryEligibilityPolicy,
)


class RecoveryIncidentTracker(Protocol):
    def has_processed(self, run_id: str, incident_key: str) -> bool:
        ...

    def mark_processed(self, run_id: str, incident_key: str) -> None:
        ...


@dataclass(frozen=True, slots=True)
class RecoveryCandidate:
    run_id: str
    incident_key: str
    eligibility: RecoveryEligibilityInput


@dataclass(frozen=True, slots=True)
class RecoveryLoopResult:
    run_id: str
    incident_key: str
    decision: OperationalDecision
    reason_code: OperationalReasonCode
    target_condition: OperationalCondition
    action_taken: bool
    action_name: Optional[str] = None
    detail: Optional[str] = None


class InMemoryRecoveryIncidentTracker:
    def __init__(self) -> None:
        self._processed: set[tuple[str, str]] = set()

    def has_processed(self, run_id: str, incident_key: str) -> bool:
        return (run_id, incident_key) in self._processed

    def mark_processed(self, run_id: str, incident_key: str) -> None:
        self._processed.add((run_id, incident_key))


class RecoveryLoopService:
    def __init__(
        self,
        *,
        eligibility_policy: RecoveryEligibilityPolicy | None = None,
        incident_tracker: RecoveryIncidentTracker | None = None,
        retry_executor: Callable[[str], None] | None = None,
        reentry_executor: Callable[[str], None] | None = None,
        revalidate_candidate: Callable[[RecoveryCandidate], bool] | None = None,
        audit_service: OperationalAuditService | None = None,
        metrics_service: OperationalMetricsService | None = None,
    ) -> None:
        self._eligibility_policy = eligibility_policy or RecoveryEligibilityPolicy()
        self._incident_tracker = incident_tracker or InMemoryRecoveryIncidentTracker()
        self._retry_executor = retry_executor or (lambda run_id: None)
        self._reentry_executor = reentry_executor or (lambda run_id: None)
        self._revalidate_candidate = revalidate_candidate or (lambda candidate: True)
        self._audit_service = audit_service
        self._metrics_service = metrics_service or OperationalMetricsService(
            InMemoryOperationalMetricsStore()
        )

    def process(self, candidate: RecoveryCandidate) -> RecoveryLoopResult:
        if self._incident_tracker.has_processed(
            run_id=candidate.run_id,
            incident_key=candidate.incident_key,
        ):
            result = RecoveryLoopResult(
                run_id=candidate.run_id,
                incident_key=candidate.incident_key,
                decision=OperationalDecision.ALREADY_RECOVERED_NOOP,
                reason_code=OperationalReasonCode.ALREADY_RECOVERED_SAME_INCIDENT,
                target_condition=OperationalCondition.RECOVERY_SKIPPED,
                action_taken=False,
                detail="incident_already_processed",
            )
            self._record(candidate, result)
            return result

        evaluation = self._eligibility_policy.evaluate(candidate.eligibility)

        if not evaluation.is_eligible:
            self._incident_tracker.mark_processed(
                run_id=candidate.run_id,
                incident_key=candidate.incident_key,
            )
            result = RecoveryLoopResult(
                run_id=candidate.run_id,
                incident_key=candidate.incident_key,
                decision=evaluation.decision,
                reason_code=evaluation.reason_code,
                target_condition=evaluation.target_condition,
                action_taken=False,
                detail=evaluation.detail,
            )
            self._record(candidate, result)
            return result

        if not self._revalidate_candidate(candidate):
            self._incident_tracker.mark_processed(
                run_id=candidate.run_id,
                incident_key=candidate.incident_key,
            )
            result = RecoveryLoopResult(
                run_id=candidate.run_id,
                incident_key=candidate.incident_key,
                decision=OperationalDecision.CANDIDATE_REJECTED,
                reason_code=OperationalReasonCode.CANDIDATE_STATE_CHANGED,
                target_condition=OperationalCondition.RECOVERY_SKIPPED,
                action_taken=False,
                detail="candidate_failed_revalidation",
            )
            self._record(candidate, result)
            return result

        if evaluation.target_condition == OperationalCondition.RETRY_PENDING:
            self._retry_executor(candidate.run_id)
            self._incident_tracker.mark_processed(
                run_id=candidate.run_id,
                incident_key=candidate.incident_key,
            )
            result = RecoveryLoopResult(
                run_id=candidate.run_id,
                incident_key=candidate.incident_key,
                decision=OperationalDecision.RETRY_TRIGGERED,
                reason_code=evaluation.reason_code,
                target_condition=OperationalCondition.RETRY_PENDING,
                action_taken=True,
                action_name="retry",
            )
            self._record(candidate, result)
            return result

        if evaluation.target_condition == OperationalCondition.REENTRY_PENDING:
            self._reentry_executor(candidate.run_id)
            self._incident_tracker.mark_processed(
                run_id=candidate.run_id,
                incident_key=candidate.incident_key,
            )
            result = RecoveryLoopResult(
                run_id=candidate.run_id,
                incident_key=candidate.incident_key,
                decision=OperationalDecision.REENTRY_TRIGGERED,
                reason_code=evaluation.reason_code,
                target_condition=OperationalCondition.REENTRY_PENDING,
                action_taken=True,
                action_name="reentry",
            )
            self._record(candidate, result)
            return result

        self._incident_tracker.mark_processed(
            run_id=candidate.run_id,
            incident_key=candidate.incident_key,
        )
        result = RecoveryLoopResult(
            run_id=candidate.run_id,
            incident_key=candidate.incident_key,
            decision=OperationalDecision.CANDIDATE_REJECTED,
            reason_code=OperationalReasonCode.LIFECYCLE_BLOCKED,
            target_condition=OperationalCondition.RECOVERY_SKIPPED,
            action_taken=False,
            detail="unsupported_target_condition",
        )
        self._record(candidate, result)
        return result

    def _record(self, candidate: RecoveryCandidate, result: RecoveryLoopResult) -> None:
        self._metrics_service.record_recovery_result(
            decision=result.decision,
            reason_code=result.reason_code,
            action_taken=result.action_taken,
        )

        if self._audit_service is None:
            return

        self._audit_service.record(
            OperationalAuditWrite(
                run_id=candidate.run_id,
                event_type=result.decision.value,
                decision=result.decision,
                reason_code=result.reason_code,
                new_operational_state=result.target_condition,
                related_failure_code=candidate.eligibility.failure_code,
                correlation_id=candidate.incident_key,
                reason_detail=result.detail,
                metadata={
                    "action_taken": str(result.action_taken).lower(),
                    "action_name": result.action_name or "",
                },
            )
        )