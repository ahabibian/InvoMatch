from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from invomatch.domain.models import ReconciliationRun
from invomatch.runtime.runtime_failure import RuntimeFailure
from invomatch.runtime.runtime_policy import should_reenter_after_failure


RecoveryDecision = Literal["none", "reenter", "fail"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class StuckRunAssessment:
    is_stuck: bool
    reason: str
    recovery_decision: RecoveryDecision


def lease_is_expired(run: ReconciliationRun, *, now: datetime | None = None) -> bool:
    effective_now = now or _utcnow()

    if run.lease_expires_at is None:
        return False

    return run.lease_expires_at <= effective_now


def has_valid_owner(run: ReconciliationRun, *, now: datetime | None = None) -> bool:
    if run.claimed_by is None:
        return False

    return not lease_is_expired(run, now=now)


def assess_stuck_run(
    run: ReconciliationRun,
    *,
    last_failure: RuntimeFailure | None = None,
    now: datetime | None = None,
) -> StuckRunAssessment:
    if run.status != "processing":
        return StuckRunAssessment(
            is_stuck=False,
            reason="not_processing",
            recovery_decision="none",
        )

    if run.claimed_by is None:
        return StuckRunAssessment(
            is_stuck=True,
            reason="processing_without_owner",
            recovery_decision="fail",
        )

    if not lease_is_expired(run, now=now):
        return StuckRunAssessment(
            is_stuck=False,
            reason="active_lease",
            recovery_decision="none",
        )

    if last_failure is None:
        return StuckRunAssessment(
            is_stuck=True,
            reason="expired_lease_without_failure_context",
            recovery_decision="fail",
        )

    if should_reenter_after_failure(
        run_status=run.status,
        lease_is_valid=False,
        last_failure=last_failure,
    ):
        return StuckRunAssessment(
            is_stuck=True,
            reason="expired_lease_reentry_allowed",
            recovery_decision="reenter",
        )

    return StuckRunAssessment(
        is_stuck=True,
        reason="expired_lease_reentry_not_allowed",
        recovery_decision="fail",
    )