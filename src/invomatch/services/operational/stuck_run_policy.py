from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from invomatch.domain.operational.models import (
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
    RecoveryEvaluationResult,
)


@dataclass(frozen=True, slots=True)
class StuckRunInput:
    business_status: str
    now: datetime
    progress_timeout_seconds: int
    lease_expires_at: Optional[datetime] = None
    last_progress_at: Optional[datetime] = None
    has_active_claim: bool = False
    already_marked_same_incident: bool = False


class StuckRunPolicy:
    def evaluate(self, data: StuckRunInput) -> RecoveryEvaluationResult:
        if data.business_status != "processing":
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.NOT_STUCK,
                reason_code=OperationalReasonCode.NO_FAILURE_OR_STUCK_SIGNAL,
                target_condition=OperationalCondition.HEALTHY,
                detail="business_status_not_processing",
            )

        if data.has_active_claim:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.NOT_STUCK,
                reason_code=OperationalReasonCode.ACTIVE_CLAIM_PRESENT,
                target_condition=OperationalCondition.HEALTHY,
            )

        if data.already_marked_same_incident:
            return RecoveryEvaluationResult(
                is_eligible=False,
                decision=OperationalDecision.ALREADY_RECOVERED_NOOP,
                reason_code=OperationalReasonCode.ALREADY_MARKED_SAME_INCIDENT,
                target_condition=OperationalCondition.RECOVERY_SKIPPED,
            )

        lease_expired = (
            data.lease_expires_at is not None and data.lease_expires_at <= data.now
        )
        no_progress_timeout = self._is_no_progress_timeout(data=data)

        if lease_expired or no_progress_timeout:
            return RecoveryEvaluationResult(
                is_eligible=True,
                decision=OperationalDecision.STUCK_DETECTED,
                reason_code=(
                    OperationalReasonCode.LEASE_EXPIRED
                    if lease_expired
                    else OperationalReasonCode.NO_PROGRESS_TIMEOUT
                ),
                target_condition=OperationalCondition.STUCK_DETECTED,
            )

        return RecoveryEvaluationResult(
            is_eligible=False,
            decision=OperationalDecision.NOT_STUCK,
            reason_code=OperationalReasonCode.NONE,
            target_condition=OperationalCondition.HEALTHY,
        )

    def _is_no_progress_timeout(self, data: StuckRunInput) -> bool:
        if data.last_progress_at is None:
            return False

        if data.progress_timeout_seconds < 0:
            raise ValueError("progress_timeout_seconds must be >= 0")

        deadline = data.last_progress_at + timedelta(seconds=data.progress_timeout_seconds)
        return deadline <= data.now