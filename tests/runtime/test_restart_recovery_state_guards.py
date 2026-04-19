from datetime import datetime, timedelta, timezone

import pytest

from invomatch.domain.models import ReconciliationRun
from invomatch.runtime.runtime_failure import FailureCategory, RuntimeFailure
from invomatch.services.runtime_recovery_service import RuntimeRecoveryService
from invomatch.services.run_store import InMemoryRunStore


def _now() -> datetime:
    return datetime(2026, 4, 19, 12, 0, 0, tzinfo=timezone.utc)


def _run(
    *,
    run_id: str,
    status: str,
    claimed_by: str | None = None,
    lease_expires_at: datetime | None = None,
    attempt_count: int = 0,
) -> ReconciliationRun:
    now = _now()
    started_at = now if status in {"processing", "review_required", "completed", "failed"} else None
    finished_at = now if status in {"completed", "failed", "cancelled"} else None

    return ReconciliationRun(
        run_id=run_id,
        status=status,
        version=0,
        created_at=now,
        updated_at=now,
        started_at=started_at,
        finished_at=finished_at,
        claimed_by=claimed_by,
        claimed_at=now if claimed_by is not None else None,
        lease_expires_at=lease_expires_at,
        attempt_count=attempt_count,
        invoice_csv_path="sample-data/invoices.csv",
        payment_csv_path="sample-data/payments.csv",
        error_message=None,
        report=None,
    )


def _failure(
    *,
    category: FailureCategory = FailureCategory.DEPENDENCY_FAILURE,
    is_retryable: bool = True,
    is_terminal: bool = False,
) -> RuntimeFailure:
    return RuntimeFailure(
        category=category,
        code="test_code",
        message="test_message",
        is_retryable=is_retryable,
        is_terminal=is_terminal,
    )


def test_claim_reentry_candidate_rejects_review_required_run():
    run_store = InMemoryRunStore(
        [
            _run(
                run_id="run-review-required",
                status="review_required",
                claimed_by="worker-old",
                lease_expires_at=_now() - timedelta(seconds=5),
                attempt_count=1,
            )
        ]
    )

    service = RuntimeRecoveryService()

    with pytest.raises(ValueError, match="not eligible for recovery claim"):
        service.claim_reentry_candidate(
            run_id="run-review-required",
            worker_id="worker-new",
            run_store=run_store,
            failure_lookup={
                "run-review-required": _failure(),
            },
            now=_now(),
        )

    persisted = run_store.get_run("run-review-required")
    assert persisted is not None
    assert persisted.status == "review_required"
    assert persisted.claimed_by == "worker-old"
    assert persisted.attempt_count == 1


def test_claim_reentry_candidate_rejects_completed_run():
    run_store = InMemoryRunStore(
        [
            _run(
                run_id="run-completed",
                status="completed",
                claimed_by="worker-old",
                lease_expires_at=_now() - timedelta(seconds=5),
                attempt_count=1,
            )
        ]
    )

    service = RuntimeRecoveryService()

    with pytest.raises(ValueError, match="not eligible for recovery claim"):
        service.claim_reentry_candidate(
            run_id="run-completed",
            worker_id="worker-new",
            run_store=run_store,
            failure_lookup={
                "run-completed": _failure(),
            },
            now=_now(),
        )

    persisted = run_store.get_run("run-completed")
    assert persisted is not None
    assert persisted.status == "completed"
    assert persisted.claimed_by == "worker-old"
    assert persisted.attempt_count == 1


def test_claim_reentry_candidate_rejects_failed_run():
    run_store = InMemoryRunStore(
        [
            _run(
                run_id="run-failed",
                status="failed",
                claimed_by="worker-old",
                lease_expires_at=_now() - timedelta(seconds=5),
                attempt_count=2,
            )
        ]
    )

    service = RuntimeRecoveryService()

    with pytest.raises(ValueError, match="not eligible for recovery claim"):
        service.claim_reentry_candidate(
            run_id="run-failed",
            worker_id="worker-new",
            run_store=run_store,
            failure_lookup={
                "run-failed": _failure(),
            },
            now=_now(),
        )

    persisted = run_store.get_run("run-failed")
    assert persisted is not None
    assert persisted.status == "failed"
    assert persisted.claimed_by == "worker-old"
    assert persisted.attempt_count == 2


def test_claim_reentry_candidate_rejects_queued_run():
    run_store = InMemoryRunStore(
        [
            _run(
                run_id="run-queued",
                status="queued",
                claimed_by=None,
                lease_expires_at=None,
                attempt_count=0,
            )
        ]
    )

    service = RuntimeRecoveryService()

    with pytest.raises(ValueError, match="not eligible for recovery claim"):
        service.claim_reentry_candidate(
            run_id="run-queued",
            worker_id="worker-new",
            run_store=run_store,
            failure_lookup={},
            now=_now(),
        )

    persisted = run_store.get_run("run-queued")
    assert persisted is not None
    assert persisted.status == "queued"
    assert persisted.claimed_by is None
    assert persisted.attempt_count == 0