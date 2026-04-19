from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from invomatch.domain.models import ReconciliationRun
from invomatch.domain.review.models import DecisionType, FeedbackRecord
from invomatch.services.restart_consistency_repair_service import (
    RestartConsistencyRepairService,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.run_store import JsonRunStore
from invomatch.services.run_view_query_service import RunViewQueryService
from invomatch.services.sqlite_review_store import SqliteReviewStore


def _now() -> datetime:
    return datetime(2026, 4, 19, 22, 0, 0, tzinfo=timezone.utc)


def _processing_run(run_id: str) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        run_id=run_id,
        status="processing",
        version=1,
        created_at=now - timedelta(minutes=15),
        updated_at=now - timedelta(minutes=1),
        started_at=now - timedelta(minutes=14),
        finished_at=None,
        claimed_by="worker-1",
        claimed_at=now - timedelta(minutes=14),
        lease_expires_at=now - timedelta(minutes=13),
        attempt_count=1,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error=None,
        error_message=None,
        report=None,
    )


class EmptyArtifactQueryService:
    def list_artifacts_for_run(self, run_id: str):
        return []


class ExportNotReadyEvaluator:
    def evaluate(self, run_id: str):
        class Result:
            is_export_ready = False
        return Result()


class ExportReadyEvaluator:
    def evaluate(self, run_id: str):
        class Result:
            is_export_ready = True
        return Result()


def test_restart_recovery_consistency_end_to_end(tmp_path: Path):
    run_store_path = tmp_path / "runs.json"
    review_store_path = tmp_path / "review.sqlite3"

    run_store = JsonRunStore(run_store_path)
    review_store = SqliteReviewStore(review_store_path)
    review_service = ReviewService()

    run = _processing_run("run-scenario-6")
    run_store.create_run(run)

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="fb-scenario-6",
        run_id=run.run_id,
        source_type="run_orchestration",
        source_reference="INV-100",
        feedback_type="REVIEW_CASE",
        raw_payload={
            "invoice_id": "INV-100",
            "reason": "manual_review_required",
            "blocking": True,
            "source_status": "unmatched",
        },
        submitted_by="system",
    )
    review_store.save_feedback(feedback)

    review_item, audit_event = review_service.create_review_item(
        feedback=feedback,
        review_session=session,
    )
    review_store.save_review_item(review_item)
    review_store.save_audit_event(audit_event)

    restarted_run_store_1 = JsonRunStore(run_store_path)
    restarted_review_store_1 = SqliteReviewStore(review_store_path)

    repair_service_1 = RestartConsistencyRepairService(
        run_store=restarted_run_store_1,
        review_store=restarted_review_store_1,
    )
    repaired_1 = repair_service_1.repair_run(run.run_id)

    assert repaired_1.original_status == "processing"
    assert repaired_1.repaired_status == "review_required"
    assert repaired_1.reason == "active_review_cases_present"

    persisted_after_first_repair = restarted_run_store_1.get_run(run.run_id)
    assert persisted_after_first_repair is not None
    assert persisted_after_first_repair.status == "review_required"

    start_audit = review_service.start_review(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer-1",
    )
    restarted_review_store_1.save_review_item(review_item)
    restarted_review_store_1.save_audit_event(start_audit)

    decision_result = review_service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer-1",
        decision=DecisionType.APPROVE,
        reason="resolved after restart",
    )
    restarted_review_store_1.save_feedback(feedback)
    restarted_review_store_1.save_review_item(decision_result.review_item)
    restarted_review_store_1.save_decision_event(decision_result.decision_event)
    restarted_review_store_1.save_audit_event(decision_result.audit_event)
    if decision_result.eligibility_record is not None:
        restarted_review_store_1.save_eligibility_record(
            decision_result.eligibility_record
        )

    restarted_run_store_2 = JsonRunStore(run_store_path)
    restarted_review_store_2 = SqliteReviewStore(review_store_path)

    repair_service_2 = RestartConsistencyRepairService(
        run_store=restarted_run_store_2,
        review_store=restarted_review_store_2,
    )
    repaired_2 = repair_service_2.repair_run(run.run_id)

    assert repaired_2.original_status == "review_required"
    assert repaired_2.repaired_status == "completed"
    assert repaired_2.reason == "no_active_review_cases_remaining"

    persisted_after_second_repair = restarted_run_store_2.get_run(run.run_id)
    assert persisted_after_second_repair is not None
    assert persisted_after_second_repair.status == "completed"

    run_view = RunViewQueryService(
        run_store=restarted_run_store_2,
        review_store=restarted_review_store_2,
        artifact_query_service=EmptyArtifactQueryService(),
        export_readiness_evaluator=ExportReadyEvaluator(),
    ).get_run_view(run.run_id)

    assert run_view is not None
    assert run_view.run_id == run.run_id
    assert run_view.status == "completed"
    assert run_view.review_summary.status == "completed"
    assert run_view.review_summary.total_items == 1
    assert run_view.review_summary.open_items == 0
    assert run_view.review_summary.resolved_items == 1
    assert run_view.export_summary.status == "ready"