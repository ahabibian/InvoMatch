from datetime import datetime, timezone

from invomatch.domain.models import MatchResult, ReconciliationReport, ReconciliationResult, ReconciliationRun
from invomatch.domain.review.models import DecisionType
from invomatch.services.orchestration.export_readiness_evaluator import (
    ExportReadinessEvaluator,
)
from invomatch.services.orchestration.review_resolution_coordinator import (
    ReviewResolutionCoordinator,
)
from invomatch.services.orchestration.run_orchestration_service import (
    RunOrchestrationService,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import InMemoryRunStore


class FakeProjectionStore:
    def __init__(self):
        self._existing: set[tuple[str, str]] = set()

    def save_results(self, *, tenant_id: str, run_id: str, results: list) -> None:
        self._existing.add((tenant_id, run_id))

    def get_results(self, *, tenant_id: str, run_id: str):
        return [] if (tenant_id, run_id) in self._existing else None

    def exists(self, *, tenant_id: str, run_id: str) -> bool:
        return (tenant_id, run_id) in self._existing


def _exportable_report() -> ReconciliationReport:
    return ReconciliationReport(
        total_invoices=1,
        matched=1,
        duplicate_detected=0,
        partial_match=0,
        unmatched=0,
        results=[
            ReconciliationResult(
                invoice_id="INV-1001",
                match_result=MatchResult(
                    status="matched",
                    payment_id="PAY-E001",
                    payment_ids=["PAY-E001"],
                    duplicate_payment_ids=None,
                    confidence_score=0.99,
                    confidence_explanation="exact match",
                    mismatch_reasons=["amount_match", "reference_match"],
                ),
            )
        ],
    )

def _processing_run(run_id: str) -> ReconciliationRun:
    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        run_id=run_id,
        tenant_id="tenant-test",
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
        invoice_csv_path="sample-data/invoices.csv",
        payment_csv_path="sample-data/payments.csv",
        error_message=None,
        report=_exportable_report(),
    )


def test_end_to_end_run_flow_review_to_completion_to_export_ready():
    run = _processing_run("run_e2e_001")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    review_service = ReviewService()
    projection_store = FakeProjectionStore()

    orchestration_service = RunOrchestrationService(
        review_store=review_store,
        review_service=review_service,
        projection_store=projection_store,
    )

    coordinator = ReviewResolutionCoordinator(
        review_store=review_store,
        review_service=review_service,
        run_orchestration_service=orchestration_service,
    )

    export_evaluator = ExportReadinessEvaluator(
        run_store=run_store,
        review_store=review_store,
        review_service=review_service,
        projection_store=projection_store,
    )

    post_match_result, persisted_after_match = (
        orchestration_service.orchestrate_and_persist_post_matching(
            run_id=run.run_id,
            reconciliation_outcomes=[
                {"invoice_id": "INV-E2E-1", "status": "unmatched", "reason": "no_match"},
            ],
            run_store=run_store,
        )
    )

    assert post_match_result.run_status == "review_required"
    assert persisted_after_match.status == "review_required"
    assert len(post_match_result.review_cases) == 1

    export_before_resolution = export_evaluator.evaluate(run.run_id)
    assert export_before_resolution.is_export_ready is False
    assert export_before_resolution.reason == "run_status_not_completed:review_required"

    review_item = review_store.list_review_items()[0]
    feedback = review_store.get_feedback(review_item.feedback_id)

    resolution_result, persisted_after_resolution = coordinator.resolve_and_reconcile(
        run_id=run.run_id,
        review_item_id=review_item.review_item_id,
        feedback_id=feedback.feedback_id,
        reviewer_id="reviewer-e2e",
        decision=DecisionType.APPROVE,
        reason="resolved in end-to-end test",
        run_store=run_store,
    )

    assert resolution_result.review_item.item_status.value == "APPROVED"
    assert persisted_after_resolution.status == "completed"

    export_after_resolution = export_evaluator.evaluate(run.run_id)
    assert export_after_resolution.is_export_ready is True
    assert export_after_resolution.reason == "export_allowed"