from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from invomatch.domain.models import ReconciliationRun
from invomatch.domain.review.models import FeedbackRecord
from invomatch.services.review_service import ReviewService
from invomatch.services.run_store import JsonRunStore
from invomatch.services.run_view_query_service import RunViewQueryService
from invomatch.services.sqlite_review_store import SqliteReviewStore


def _now() -> datetime:
    return datetime(2026, 4, 19, 20, 0, 0, tzinfo=timezone.utc)


def _processing_run(run_id: str) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        run_id=run_id,
        status="processing",
        version=1,
        created_at=now - timedelta(minutes=10),
        updated_at=now - timedelta(minutes=1),
        started_at=now - timedelta(minutes=9),
        finished_at=None,
        claimed_by="worker-1",
        claimed_at=now - timedelta(minutes=9),
        lease_expires_at=now - timedelta(minutes=8),
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


def test_restart_exposes_processing_run_with_persisted_active_review_case(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = SqliteReviewStore(tmp_path / "review.sqlite3")
    review_service = ReviewService()

    run = _processing_run("run-orchestration-gap")
    run_store.create_run(run)

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="fb-gap-1",
        run_id=run.run_id,
        source_type="run_orchestration",
        source_reference="INV-001",
        feedback_type="REVIEW_CASE",
        raw_payload={
            "invoice_id": "INV-001",
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

    reloaded_run_store = JsonRunStore(tmp_path / "runs.json")
    reloaded_review_store = SqliteReviewStore(tmp_path / "review.sqlite3")

    query_service = RunViewQueryService(
        run_store=reloaded_run_store,
        review_store=reloaded_review_store,
        artifact_query_service=EmptyArtifactQueryService(),
        export_readiness_evaluator=ExportNotReadyEvaluator(),
    )

    run_view = query_service.get_run_view(run.run_id)

    assert run_view is not None
    assert run_view.run_id == run.run_id

    # Current persisted lifecycle truth still says processing
    assert run_view.status == "processing"

    # But persisted review truth already shows an active review case
    assert run_view.review_summary.status == "in_review"
    assert run_view.review_summary.total_items == 1
    assert run_view.review_summary.open_items == 1
    assert run_view.review_summary.resolved_items == 0

    # This test intentionally documents the current mismatch seam
    assert run_view.export_summary.status == "not_ready"