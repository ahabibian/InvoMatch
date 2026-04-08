from datetime import datetime, timedelta, timezone

import pytest

from invomatch.domain.operational.models import (
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
)
from invomatch.services.operational.stuck_run_policy import (
    StuckRunInput,
    StuckRunPolicy,
)


def test_expired_lease_marks_processing_run_as_stuck() -> None:
    policy = StuckRunPolicy()
    now = datetime.now(timezone.utc)

    result = policy.evaluate(
        StuckRunInput(
            business_status="processing",
            now=now,
            progress_timeout_seconds=300,
            lease_expires_at=now - timedelta(seconds=1),
        )
    )

    assert result.is_eligible is True
    assert result.decision == OperationalDecision.STUCK_DETECTED
    assert result.reason_code == OperationalReasonCode.LEASE_EXPIRED
    assert result.target_condition == OperationalCondition.STUCK_DETECTED


def test_no_progress_timeout_marks_processing_run_as_stuck() -> None:
    policy = StuckRunPolicy()
    now = datetime.now(timezone.utc)

    result = policy.evaluate(
        StuckRunInput(
            business_status="processing",
            now=now,
            progress_timeout_seconds=60,
            last_progress_at=now - timedelta(seconds=120),
        )
    )

    assert result.is_eligible is True
    assert result.reason_code == OperationalReasonCode.NO_PROGRESS_TIMEOUT


def test_active_claim_prevents_stuck_classification() -> None:
    policy = StuckRunPolicy()
    now = datetime.now(timezone.utc)

    result = policy.evaluate(
        StuckRunInput(
            business_status="processing",
            now=now,
            progress_timeout_seconds=60,
            lease_expires_at=now - timedelta(seconds=120),
            has_active_claim=True,
        )
    )

    assert result.is_eligible is False
    assert result.decision == OperationalDecision.NOT_STUCK
    assert result.reason_code == OperationalReasonCode.ACTIVE_CLAIM_PRESENT


def test_non_processing_run_is_not_stuck() -> None:
    policy = StuckRunPolicy()
    now = datetime.now(timezone.utc)

    result = policy.evaluate(
        StuckRunInput(
            business_status="failed",
            now=now,
            progress_timeout_seconds=60,
            lease_expires_at=now - timedelta(seconds=120),
        )
    )

    assert result.is_eligible is False
    assert result.target_condition == OperationalCondition.HEALTHY


def test_same_incident_is_not_marked_twice() -> None:
    policy = StuckRunPolicy()
    now = datetime.now(timezone.utc)

    result = policy.evaluate(
        StuckRunInput(
            business_status="processing",
            now=now,
            progress_timeout_seconds=60,
            lease_expires_at=now - timedelta(seconds=120),
            already_marked_same_incident=True,
        )
    )

    assert result.is_eligible is False
    assert result.decision == OperationalDecision.ALREADY_RECOVERED_NOOP
    assert result.reason_code == OperationalReasonCode.ALREADY_MARKED_SAME_INCIDENT


def test_negative_timeout_is_rejected_when_progress_timestamp_exists() -> None:
    policy = StuckRunPolicy()
    now = datetime.now(timezone.utc)

    with pytest.raises(ValueError):
        policy.evaluate(
            StuckRunInput(
                business_status="processing",
                now=now,
                progress_timeout_seconds=-1,
                last_progress_at=now - timedelta(seconds=5),
            )
        )