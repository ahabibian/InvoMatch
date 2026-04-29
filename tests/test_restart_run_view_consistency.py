from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from invomatch.domain.models import (
    MatchResult,
    ReconciliationReport,
    ReconciliationResult,
    ReconciliationRun,
)
from invomatch.domain.review.models import DecisionType, FeedbackRecord
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import JsonRunStore
from invomatch.services.run_view_query_service import RunViewQueryService


def _now() -> datetime:
    return datetime(2026, 4, 19, 16, 0, 0, tzinfo=timezone.utc)


def _completed_run(run_id: str) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        run_id=run_id,
            tenant_id="tenant-test",
        status="completed",
        version=2,
        created_at=now - timedelta(minutes=20),
        updated_at=now - timedelta(minutes=1),
        started_at=now - timedelta(minutes=19),
        finished_at=now - timedelta(minutes=2),
        claimed_by="worker-1",
        claimed_at=now - timedelta(minutes=19),
        lease_expires_at=now - timedelta(minutes=18),
        attempt_count=1,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error=None,
        error_message=None,
        report=ReconciliationReport(
            total_invoices=1,
            matched=0,
            duplicate_detected=0,
            partial_match=0,
            unmatched=1,
            results=[
                ReconciliationResult(
                    invoice_id="INV-001",
                    match_result=MatchResult(
                        status="unmatched",
                        payment_id=None,
                        duplicate_payment_ids=None,
                        payment_ids=None,
                        confidence_score=0.10,
                        confidence_explanation="no viable candidate",
                        mismatch_reasons=["no_viable_candidate"],
                    ),
                )
            ],
        ),
    )


class EmptyArtifactQueryService:
    def list_artifacts_for_run(self, run_id: str):
        return []


class ExportReadyEvaluator:
    def evaluate(self, run_id: str):
        class Result:
            is_export_ready = True
        return Result()


def test_run_view_after_reload_preserves_completed_review_and_ready_export_state(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    run = _completed_run("run-view-restart")
    run_store.create_run(run)

    review_store = InMemoryReviewStore()
    review_service = ReviewService()

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="fb-1",
        run_id=run.run_id,
        source_type="reconciliation_result",
        source_reference="INV-001",
        feedback_type="manual_review",
        raw_payload={"invoice_id": "INV-001"},
        submitted_by="system",
    )
    review_store.save_feedback(feedback)

    review_item, audit_event = review_service.create_review_item(
        feedback=feedback,
        review_session=session,
    )
    review_store.save_review_item(review_item)
    review_store.save_audit_event(audit_event)

    start_audit = review_service.start_review(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer-1",
    )
    review_store.save_review_item(review_item)
    review_store.save_audit_event(start_audit)

    decision_result = review_service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer-1",
        decision=DecisionType.APPROVE,
        reason="resolved before restart",
    )
    review_store.save_review_item(decision_result.review_item)
    review_store.save_decision_event(decision_result.decision_event)
    review_store.save_audit_event(decision_result.audit_event)
    if decision_result.eligibility_record is not None:
        review_store.save_eligibility_record(decision_result.eligibility_record)

    reloaded_run_store = JsonRunStore(tmp_path / "runs.json")

    query_service = RunViewQueryService(
        run_store=reloaded_run_store,
        review_store=review_store,
        artifact_query_service=EmptyArtifactQueryService(),
        export_readiness_evaluator=ExportReadyEvaluator(),
    )

    run_view = query_service.get_run_view(run.run_id)

    assert run_view is not None
    assert run_view.run_id == run.run_id
    assert run_view.status == "completed"

    assert run_view.review_summary.status == "completed"
    assert run_view.review_summary.total_items == 1
    assert run_view.review_summary.open_items == 0
    assert run_view.review_summary.resolved_items == 1

    assert run_view.export_summary.status == "ready"
    assert run_view.export_summary.artifact_count == 0

    assert run_view.match_summary.total_items == 1
    assert run_view.match_summary.unmatched_items == 1