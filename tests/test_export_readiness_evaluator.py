from datetime import datetime, timezone

from invomatch.domain.models import ReconciliationRun
from invomatch.services.orchestration.export_readiness_evaluator import (
    ExportReadinessEvaluator,
)
from invomatch.services.orchestration.review_integration_service import (
    ReviewIntegrationService,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import InMemoryRunStore


def _run(run_id: str, status: str) -> ReconciliationRun:
    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        run_id=run_id,
        status=status,
        version=0,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=now if status == "completed" else None,
        claimed_by="worker-1",
        claimed_at=now,
        lease_expires_at=now,
        attempt_count=1,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error_message=None,
        report=None,
    )


def test_export_is_allowed_for_completed_run_with_no_active_review_cases():
    run = _run("run-123", "completed")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()

    evaluator = ExportReadinessEvaluator(
        run_store=run_store,
        review_store=review_store,
    )

    result = evaluator.evaluate(run.run_id)

    assert result.is_export_ready is True
    assert result.reason == "export_allowed"


def test_export_is_blocked_when_run_status_is_not_completed():
    run = _run("run-124", "processing")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()

    evaluator = ExportReadinessEvaluator(
        run_store=run_store,
        review_store=review_store,
    )

    result = evaluator.evaluate(run.run_id)

    assert result.is_export_ready is False
    assert result.reason == "run_status_not_completed:processing"


def test_export_is_blocked_when_active_blocking_review_case_exists():
    run = _run("run-125", "completed")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    review_service = ReviewService()
    review_integration = ReviewIntegrationService(
        review_service=review_service,
        review_store=review_store,
    )

    review_integration.create_cases(
        run_id=run.run_id,
        review_cases=[
            {
                "invoice_id": "INV-001",
                "reason": "no_match",
                "blocking": True,
                "status": "pending",
            }
        ],
        created_by="test",
    )

    evaluator = ExportReadinessEvaluator(
        run_store=run_store,
        review_store=review_store,
        review_service=review_service,
    )

    result = evaluator.evaluate(run.run_id)

    assert result.is_export_ready is False
    assert result.reason == "active_blocking_review_cases_present"


def test_export_is_blocked_when_deferred_review_case_exists():
    run = _run("run-126", "completed")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    review_service = ReviewService()
    review_integration = ReviewIntegrationService(
        review_service=review_service,
        review_store=review_store,
    )

    review_integration.create_cases(
        run_id=run.run_id,
        review_cases=[
            {
                "invoice_id": "INV-002",
                "reason": "need_more_context",
                "blocking": True,
                "status": "pending",
            }
        ],
        created_by="test",
    )

    review_item = review_store.list_review_items()[0]
    review_item.item_status = review_item.item_status.DEFERRED
    review_store.save_review_item(review_item)

    evaluator = ExportReadinessEvaluator(
        run_store=run_store,
        review_store=review_store,
        review_service=review_service,
    )

    result = evaluator.evaluate(run.run_id)

    assert result.is_export_ready is False
    assert result.reason == "active_blocking_review_cases_present"