from datetime import datetime, timedelta, timezone

from invomatch.domain.models import ReconciliationRun
from invomatch.runtime.runtime_failure import FailureCategory, RuntimeFailure
from invomatch.runtime.stuck_run import (
    assess_stuck_run,
    has_valid_owner,
    lease_is_expired,
)


def _now() -> datetime:
    return datetime(2026, 4, 8, 12, 0, 0, tzinfo=timezone.utc)


def _run(
    *,
    status: str = "processing",
    claimed_by: str | None = "worker-1",
    lease_expires_at: datetime | None = None,
) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        tenant_id="tenant-test",

        run_id="run-1",
        status=status,
        version=1,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=None,
        claimed_by=claimed_by,
        claimed_at=now,
        lease_expires_at=lease_expires_at,
        attempt_count=1,
        invoice_csv_path="sample-data/invoices.csv",
        payment_csv_path="sample-data/payments.csv",
        error_message=None,
        report=None,
    )


def _failure(
    *,
    category: FailureCategory,
    is_retryable: bool,
    is_terminal: bool,
) -> RuntimeFailure:
    return RuntimeFailure(
        category=category,
        code="test_code",
        message="test message",
        is_retryable=is_retryable,
        is_terminal=is_terminal,
    )


def test_lease_is_expired_returns_false_when_no_lease_present():
    run = _run(lease_expires_at=None)

    assert lease_is_expired(run, now=_now()) is False


def test_lease_is_expired_returns_true_when_lease_deadline_passed():
    run = _run(lease_expires_at=_now() - timedelta(seconds=1))

    assert lease_is_expired(run, now=_now()) is True


def test_has_valid_owner_requires_owner_and_unexpired_lease():
    run = _run(lease_expires_at=_now() + timedelta(seconds=30))

    assert has_valid_owner(run, now=_now()) is True


def test_has_valid_owner_returns_false_when_owner_missing():
    run = _run(
        claimed_by=None,
        lease_expires_at=_now() + timedelta(seconds=30),
    )

    assert has_valid_owner(run, now=_now()) is False


def test_assess_stuck_run_returns_none_for_non_processing_run():
    run = _run(status="completed")

    assessment = assess_stuck_run(run, now=_now())

    assert assessment.is_stuck is False
    assert assessment.reason == "not_processing"
    assert assessment.recovery_decision == "none"


def test_assess_stuck_run_fails_processing_run_without_owner():
    run = _run(
        status="processing",
        claimed_by=None,
        lease_expires_at=_now() + timedelta(seconds=30),
    )

    assessment = assess_stuck_run(run, now=_now())

    assert assessment.is_stuck is True
    assert assessment.reason == "processing_without_owner"
    assert assessment.recovery_decision == "fail"


def test_assess_stuck_run_returns_none_when_processing_lease_is_active():
    run = _run(lease_expires_at=_now() + timedelta(seconds=30))

    assessment = assess_stuck_run(run, now=_now())

    assert assessment.is_stuck is False
    assert assessment.reason == "active_lease"
    assert assessment.recovery_decision == "none"


def test_assess_stuck_run_fails_expired_lease_without_failure_context():
    run = _run(lease_expires_at=_now() - timedelta(seconds=1))

    assessment = assess_stuck_run(run, now=_now())

    assert assessment.is_stuck is True
    assert assessment.reason == "expired_lease_without_failure_context"
    assert assessment.recovery_decision == "fail"


def test_assess_stuck_run_allows_reentry_for_retryable_dependency_failure():
    run = _run(lease_expires_at=_now() - timedelta(seconds=1))
    failure = _failure(
        category=FailureCategory.DEPENDENCY_FAILURE,
        is_retryable=True,
        is_terminal=False,
    )

    assessment = assess_stuck_run(
        run,
        last_failure=failure,
        now=_now(),
    )

    assert assessment.is_stuck is True
    assert assessment.reason == "expired_lease_reentry_allowed"
    assert assessment.recovery_decision == "reenter"


def test_assess_stuck_run_fails_when_reentry_not_allowed():
    run = _run(lease_expires_at=_now() - timedelta(seconds=1))
    failure = _failure(
        category=FailureCategory.PERSISTENCE_FAILURE,
        is_retryable=True,
        is_terminal=False,
    )

    assessment = assess_stuck_run(
        run,
        last_failure=failure,
        now=_now(),
    )

    assert assessment.is_stuck is True
    assert assessment.reason == "expired_lease_reentry_not_allowed"
    assert assessment.recovery_decision == "fail"