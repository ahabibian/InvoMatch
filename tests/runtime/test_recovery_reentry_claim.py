from datetime import datetime, timedelta, timezone

import pytest

from invomatch.domain.models import ReconciliationRun
from invomatch.runtime.runtime_failure import FailureCategory, RuntimeFailure
from invomatch.services.runtime_recovery_service import RuntimeRecoveryService
from invomatch.services.run_store import InMemoryRunStore


def _now() -> datetime:
    return datetime(2026, 4, 8, 12, 0, 0, tzinfo=timezone.utc)


def _processing_run(
    *,
    run_id: str,
    claimed_by: str | None,
    lease_expires_at: datetime | None,
) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        run_id=run_id,
        status="processing",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=None,
        claimed_by=claimed_by,
        claimed_at=now if claimed_by is not None else None,
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
        message="test_message",
        is_retryable=is_retryable,
        is_terminal=is_terminal,
    )


def test_claim_reentry_candidate_reacquires_expired_processing_run():
    run_store = InMemoryRunStore()
    run_store.create_run(
        _processing_run(
            run_id="run-reenter",
            claimed_by="worker-old",
            lease_expires_at=_now() - timedelta(seconds=5),
        )
    )

    failure_lookup = {
        "run-reenter": _failure(
            category=FailureCategory.DEPENDENCY_FAILURE,
            is_retryable=True,
            is_terminal=False,
        )
    }

    service = RuntimeRecoveryService()
    result = service.claim_reentry_candidate(
        run_id="run-reenter",
        worker_id="worker-new",
        run_store=run_store,
        failure_lookup=failure_lookup,
        lease_seconds=120,
        now=_now(),
    )

    assert result.run_id == "run-reenter"
    assert result.claimed_by == "worker-new"
    assert result.recovery_decision == "reenter"
    assert result.assessment_reason == "expired_lease_reentry_allowed"

    persisted = run_store.get_run("run-reenter")
    assert persisted is not None
    assert persisted.status == "processing"
    assert persisted.claimed_by == "worker-new"
    assert persisted.lease_expires_at is not None
    assert persisted.version >= 1


def test_claim_reentry_candidate_rejects_non_stuck_processing_run():
    run_store = InMemoryRunStore()
    run_store.create_run(
        _processing_run(
            run_id="run-active",
            claimed_by="worker-1",
            lease_expires_at=_now() + timedelta(seconds=30),
        )
    )

    service = RuntimeRecoveryService()

    with pytest.raises(ValueError, match="not eligible for recovery claim"):
        service.claim_reentry_candidate(
            run_id="run-active",
            worker_id="worker-new",
            run_store=run_store,
            failure_lookup={},
            now=_now(),
        )

    persisted = run_store.get_run("run-active")
    assert persisted is not None
    assert persisted.claimed_by == "worker-1"


def test_claim_reentry_candidate_rejects_non_reenterable_stuck_run():
    run_store = InMemoryRunStore()
    run_store.create_run(
        _processing_run(
            run_id="run-fail",
            claimed_by="worker-old",
            lease_expires_at=_now() - timedelta(seconds=5),
        )
    )

    failure_lookup = {
        "run-fail": _failure(
            category=FailureCategory.PERSISTENCE_FAILURE,
            is_retryable=True,
            is_terminal=False,
        )
    }

    service = RuntimeRecoveryService()

    with pytest.raises(ValueError, match="not reenterable"):
        service.claim_reentry_candidate(
            run_id="run-fail",
            worker_id="worker-new",
            run_store=run_store,
            failure_lookup=failure_lookup,
            now=_now(),
        )

    persisted = run_store.get_run("run-fail")
    assert persisted is not None
    assert persisted.claimed_by == "worker-old"


def test_claim_reentry_candidate_raises_for_missing_run():
    run_store = InMemoryRunStore()
    service = RuntimeRecoveryService()

    with pytest.raises(KeyError, match="Reconciliation run not found"):
        service.claim_reentry_candidate(
            run_id="missing-run",
            worker_id="worker-new",
            run_store=run_store,
            failure_lookup={},
            now=_now(),
        )