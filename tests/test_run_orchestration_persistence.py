from datetime import datetime, timezone

import pytest

from invomatch.domain.models import ReconciliationRun
from invomatch.services.orchestration.run_orchestration_service import (
    RunOrchestrationService,
)
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import InMemoryRunStore


def _processing_run(run_id: str) -> ReconciliationRun:
    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        run_id=run_id,
        status="processing",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=None,
        claimed_by="worker-1",
        claimed_at=now,
        lease_expires_at=now,
        attempt_count=1,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error_message=None,
        report=None,
    )


def _review_required_run(run_id: str) -> ReconciliationRun:
    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        run_id=run_id,
        status="review_required",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=None,
        claimed_by="worker-1",
        claimed_at=now,
        lease_expires_at=now,
        attempt_count=1,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error_message=None,
        report=None,
    )


def test_orchestrate_and_persist_post_matching_moves_run_to_review_required():
    run = _processing_run("run_review_required")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    outcomes = [
        {"invoice_id": "INV-001", "status": "unmatched", "reason": "no_match"},
    ]

    result, persisted_run = service.orchestrate_and_persist_post_matching(
        run_id=run.run_id,
        reconciliation_outcomes=outcomes,
        run_store=run_store,
    )

    assert result.run_status == "review_required"
    assert persisted_run.status == "review_required"
    assert len(result.review_cases) == 1


def test_orchestrate_and_persist_post_matching_moves_run_to_completed():
    run = _processing_run("run_completed")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    outcomes = [
        {"invoice_id": "INV-010", "status": "finalizable"},
    ]

    result, persisted_run = service.orchestrate_and_persist_post_matching(
        run_id=run.run_id,
        reconciliation_outcomes=outcomes,
        run_store=run_store,
    )

    assert result.run_status == "completed"
    assert persisted_run.status == "completed"
    assert result.review_cases == []


def test_orchestrate_and_persist_post_matching_fails_for_invalid_run_transition():
    now = datetime.now(timezone.utc)
    run = ReconciliationRun(
        run_id="run_invalid_transition",
        status="queued",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=None,
        finished_at=None,
        claimed_by=None,
        claimed_at=None,
        lease_expires_at=None,
        attempt_count=0,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error_message=None,
        report=None,
    )

    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    outcomes = [
        {"invoice_id": "INV-020", "status": "finalizable"},
    ]

    with pytest.raises(ValueError):
        service.orchestrate_and_persist_post_matching(
            run_id=run.run_id,
            reconciliation_outcomes=outcomes,
            run_store=run_store,
        )


def test_orchestrate_and_persist_post_review_resolution_moves_run_to_completed():
    run = _review_required_run("run_resolved_completed")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    result, persisted_run = service.orchestrate_and_persist_post_review_resolution(
        run_id=run.run_id,
        matching_completed=True,
        run_store=run_store,
    )

    assert result.run_status == "completed"
    assert persisted_run.status == "completed"
    assert result.review_cases == []


def test_orchestrate_and_persist_post_review_resolution_keeps_run_in_review_required_when_blockers_exist():
    run = _review_required_run("run_still_blocked")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    service.orchestrate_post_matching(
        run_id=run.run_id,
        reconciliation_outcomes=[
            {"invoice_id": "INV-030", "status": "unmatched", "reason": "no_match"},
        ],
    )

    result, persisted_run = service.orchestrate_and_persist_post_review_resolution(
        run_id=run.run_id,
        matching_completed=True,
        run_store=run_store,
    )

    assert result.run_status == "review_required"
    assert persisted_run.status == "review_required"
    assert len(result.review_cases) == 1


def test_orchestrate_and_persist_post_review_resolution_fails_for_invalid_run_transition():
    run = _processing_run("run_invalid_review_resolution")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    with pytest.raises(ValueError):
        service.orchestrate_and_persist_post_review_resolution(
            run_id=run.run_id,
            matching_completed=True,
            run_store=run_store,
        )