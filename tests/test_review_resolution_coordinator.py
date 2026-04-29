from datetime import datetime, timezone

import pytest

from invomatch.domain.models import ReconciliationRun
from invomatch.domain.review.models import DecisionType
from invomatch.services.orchestration.review_resolution_coordinator import (
    ReviewResolutionCoordinator,
)
from invomatch.services.orchestration.run_orchestration_service import (
    RunOrchestrationService,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import InMemoryRunStore


def _review_required_run(run_id: str) -> ReconciliationRun:
    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        run_id=run_id,
            tenant_id="tenant-test",
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


def test_resolve_and_reconcile_completes_run_when_last_blocker_is_approved():
    run = _review_required_run("run_resolve_complete")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    review_service = ReviewService()
    orchestration_service = RunOrchestrationService(
        review_store=review_store,
        review_service=review_service,
    )
    coordinator = ReviewResolutionCoordinator(
        review_store=review_store,
        review_service=review_service,
        run_orchestration_service=orchestration_service,
    )

    orchestration_service.orchestrate_post_matching(
        run_id=run.run_id,
        reconciliation_outcomes=[
            {"invoice_id": "INV-100", "status": "unmatched", "reason": "no_match"},
        ],
    )

    review_item = review_store.list_review_items()[0]
    feedback = review_store.get_feedback(review_item.feedback_id)

    result, persisted_run = coordinator.resolve_and_reconcile(
        run_id=run.run_id,
        review_item_id=review_item.review_item_id,
        feedback_id=feedback.feedback_id,
        reviewer_id="reviewer-1",
        decision=DecisionType.APPROVE,
        reason="approved after manual review",
        run_store=run_store,
    )

    assert result.review_item.item_status.value == "APPROVED"
    assert persisted_run.status == "completed"


def test_resolve_and_reconcile_keeps_run_in_review_required_when_item_is_deferred():
    run = _review_required_run("run_resolve_deferred")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    review_service = ReviewService()
    orchestration_service = RunOrchestrationService(
        review_store=review_store,
        review_service=review_service,
    )
    coordinator = ReviewResolutionCoordinator(
        review_store=review_store,
        review_service=review_service,
        run_orchestration_service=orchestration_service,
    )

    orchestration_service.orchestrate_post_matching(
        run_id=run.run_id,
        reconciliation_outcomes=[
            {"invoice_id": "INV-101", "status": "unmatched", "reason": "no_match"},
        ],
    )

    review_item = review_store.list_review_items()[0]
    feedback = review_store.get_feedback(review_item.feedback_id)

    result, persisted_run = coordinator.resolve_and_reconcile(
        run_id=run.run_id,
        review_item_id=review_item.review_item_id,
        feedback_id=feedback.feedback_id,
        reviewer_id="reviewer-2",
        decision=DecisionType.DEFER,
        reason="need more context",
        run_store=run_store,
    )

    assert result.review_item.item_status.value == "DEFERRED"
    assert persisted_run.status == "review_required"


def test_resolve_and_reconcile_raises_when_review_item_is_missing():
    run = _review_required_run("run_missing_item")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    review_service = ReviewService()
    orchestration_service = RunOrchestrationService(
        review_store=review_store,
        review_service=review_service,
    )
    coordinator = ReviewResolutionCoordinator(
        review_store=review_store,
        review_service=review_service,
        run_orchestration_service=orchestration_service,
    )

    with pytest.raises(KeyError):
        coordinator.resolve_and_reconcile(
            run_id=run.run_id,
            review_item_id="missing_review_item",
            feedback_id="missing_feedback",
            reviewer_id="reviewer-3",
            decision=DecisionType.APPROVE,
            run_store=run_store,
        )