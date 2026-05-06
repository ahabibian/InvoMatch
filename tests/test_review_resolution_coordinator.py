from datetime import datetime, timezone
from pathlib import Path

import pytest

from invomatch.domain.models import MatchResult, ReconciliationReport, ReconciliationResult, ReconciliationRun
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

class FakeProjectionStore:
    def __init__(self) -> None:
        self._results: dict[tuple[str, str], list] = {}

    def save_results(self, *, tenant_id: str, run_id: str, results: list, **kwargs) -> None:
        self._results[(tenant_id, run_id)] = list(results)

    def get_results(self, *, tenant_id: str, run_id: str):
        return self._results.get((tenant_id, run_id))

    def exists(self, *, tenant_id: str, run_id: str) -> bool:
        return (tenant_id, run_id) in self._results


def _projection_safe_report() -> ReconciliationReport:
    return ReconciliationReport(
        total_invoices=1,
        matched=1,
        duplicate_detected=0,
        partial_match=0,
        unmatched=0,
        results=[
            ReconciliationResult(
                invoice_id="INV-100",
                match_result=MatchResult(
                    status="matched",
                    payment_id="PAY-100",
                    payment_ids=["PAY-100"],
                    duplicate_payment_ids=None,
                    confidence_score=0.99,
                    confidence_explanation="approved review completion",
                    mismatch_reasons=["reference_match"],
                ),
            )
        ],
    )


def _review_required_run(run_id: str, base_dir: Path | None = None) -> ReconciliationRun:
    input_dir = (base_dir or Path(".")) / "input"
    invoice_csv_path = input_dir / "invoices.csv"
    payment_csv_path = input_dir / "payments.csv"
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
        invoice_csv_path=str(invoice_csv_path),
        payment_csv_path=str(payment_csv_path),
        error_message=None,
        report=_projection_safe_report(),
    )



def _write_projection_source_files(base_dir: Path) -> None:
    input_dir = base_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "invoices.csv").write_text(
        "id,date,amount,reference,currency\n"
        "INV-100,2026-04-01,100.00,REF-100,SEK\n",
        encoding="utf-8",
    )
    (input_dir / "payments.csv").write_text(
        "invoice_id,id,date,amount,reference,currency\n"
        "INV-100,PAY-100,2026-04-01,100.00,REF-100,SEK\n",
        encoding="utf-8",
    )

def test_resolve_and_reconcile_completes_run_when_last_blocker_is_approved(tmp_path):
    _write_projection_source_files(tmp_path)
    run = _review_required_run("run_resolve_complete", tmp_path)
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


def test_resolve_and_reconcile_keeps_run_in_review_required_when_item_is_deferred(tmp_path):
    _write_projection_source_files(tmp_path)
    run = _review_required_run("run_resolve_deferred", tmp_path)
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


def test_resolve_and_reconcile_raises_when_review_item_is_missing(tmp_path):
    _write_projection_source_files(tmp_path)
    run = _review_required_run("run_missing_item", tmp_path)
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

    with pytest.raises(KeyError):
        coordinator.resolve_and_reconcile(
            run_id=run.run_id,
            review_item_id="missing_review_item",
            feedback_id="missing_feedback",
            reviewer_id="reviewer-3",
            decision=DecisionType.APPROVE,
            run_store=run_store,
        )