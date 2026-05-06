from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from invomatch.domain.models import MatchResult, ReconciliationReport, ReconciliationResult, ReconciliationRun
from invomatch.domain.review.models import DecisionType, FeedbackRecord
from invomatch.services.export.finalized_projection_store import SqliteFinalizedProjectionStore
from invomatch.services.review_service import ReviewService
from invomatch.services.run_store import JsonRunStore
from invomatch.services.sqlite_review_store import SqliteReviewStore


def _now() -> datetime:
    return datetime(2026, 4, 19, 21, 0, 0, tzinfo=timezone.utc)




def _write_projection_source_files(base_dir: Path) -> tuple[Path, Path]:
    input_dir = base_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    invoice_csv = input_dir / "invoices.csv"
    payment_csv = input_dir / "payments.csv"
    invoice_csv.write_text(
        "id,date,amount,reference,currency\n"
        "INV-002,2026-04-01,100.00,REF-002,SEK\n",
        encoding="utf-8",
    )
    payment_csv.write_text(
        "invoice_id,id,date,amount,reference,currency\n"
        "INV-002,PAY-002,2026-04-01,100.00,REF-002,SEK\n",
        encoding="utf-8",
    )
    return invoice_csv, payment_csv

def _projection_safe_report() -> ReconciliationReport:
    return ReconciliationReport(
        total_invoices=1,
        matched=1,
        duplicate_detected=0,
        partial_match=0,
        unmatched=0,
        results=[
            ReconciliationResult(
                invoice_id="INV-002",
                match_result=MatchResult(
                    status="matched",
                    payment_id="PAY-002",
                    payment_ids=["PAY-002"],
                    duplicate_payment_ids=None,
                    confidence_score=0.99,
                    confidence_explanation="resolved before restart",
                    mismatch_reasons=["reference_match"],
                ),
            )
        ],
    )

def _processing_run(run_id: str) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        run_id=run_id,
            tenant_id="tenant-test",
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


def test_restart_consistency_repair_moves_processing_run_to_review_required(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = SqliteReviewStore(tmp_path / "review.sqlite3")
    review_service = ReviewService()

    run = _processing_run("run-repair-review-required")
    run_store.create_run(run)

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="fb-repair-1",
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

    # EPIC 22 target behavior:
    # a restart consistency repair service should detect that persisted
    # active review truth exists and lifecycle state must be repaired.
    from invomatch.services.restart_consistency_repair_service import (
        RestartConsistencyRepairService,
    )

    projection_store = SqliteFinalizedProjectionStore(tmp_path / "finalized_projections.sqlite3")
    service = RestartConsistencyRepairService(
        run_store=run_store,
        review_store=review_store,
        projection_store=projection_store,
    )

    repaired = service.repair_run(run.run_id)

    assert repaired is not None
    assert repaired.run_id == run.run_id
    assert repaired.original_status == "processing"
    assert repaired.repaired_status == "review_required"
    assert repaired.reason == "active_review_cases_present"

    persisted = run_store.get_run(run.run_id)
    assert persisted is not None
    assert persisted.status == "review_required"
def _review_required_run(run_id: str, base_dir: Path | None = None) -> ReconciliationRun:
    now = _now()
    if base_dir is not None:
        invoice_csv_path, payment_csv_path = _write_projection_source_files(base_dir)
    else:
        invoice_csv_path = Path("input/invoices.csv")
        payment_csv_path = Path("input/payments.csv")
    return ReconciliationRun(
        run_id=run_id,
            tenant_id="tenant-test",
        status="review_required",
        version=1,
        created_at=now - timedelta(minutes=10),
        updated_at=now - timedelta(minutes=1),
        started_at=now - timedelta(minutes=9),
        finished_at=None,
        claimed_by="worker-1",
        claimed_at=now - timedelta(minutes=9),
        lease_expires_at=now - timedelta(minutes=8),
        attempt_count=1,
        invoice_csv_path=str(invoice_csv_path),
        payment_csv_path=str(payment_csv_path),
        error=None,
        error_message=None,
        report=_projection_safe_report(),
    )


def test_restart_consistency_repair_moves_review_required_run_to_completed_when_no_active_review_remains(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = SqliteReviewStore(tmp_path / "review.sqlite3")
    review_service = ReviewService()

    run = _review_required_run("run-repair-completed", tmp_path)
    run_store.create_run(run)

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="fb-repair-2",
        run_id=run.run_id,
        source_type="run_orchestration",
        source_reference="INV-002",
        feedback_type="REVIEW_CASE",
        raw_payload={
            "invoice_id": "INV-002",
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

    from invomatch.services.restart_consistency_repair_service import (
        RestartConsistencyRepairService,
    )

    projection_store = SqliteFinalizedProjectionStore(tmp_path / "finalized_projections.sqlite3")
    service = RestartConsistencyRepairService(
        run_store=run_store,
        review_store=review_store,
        projection_store=projection_store,
    )

    repaired = service.repair_run(run.run_id)

    assert repaired is not None
    assert repaired.run_id == run.run_id
    assert repaired.original_status == "review_required"
    assert repaired.repaired_status == "completed"
    assert repaired.reason == "no_active_review_cases_remaining"

    persisted = run_store.get_run(run.run_id)
    assert persisted is not None
    assert persisted.status == "completed"
def _completed_run(run_id: str) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        run_id=run_id,
            tenant_id="tenant-test",
        status="completed",
        version=2,
        created_at=now - timedelta(minutes=15),
        updated_at=now - timedelta(minutes=2),
        started_at=now - timedelta(minutes=14),
        finished_at=now - timedelta(minutes=3),
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


def test_restart_consistency_repair_moves_completed_run_back_to_review_required_when_active_review_exists(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = SqliteReviewStore(tmp_path / "review.sqlite3")
    review_service = ReviewService()

    run = _completed_run("run-repair-completed-to-review")
    run_store.create_run(run)

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="fb-repair-3",
        run_id=run.run_id,
        source_type="run_orchestration",
        source_reference="INV-003",
        feedback_type="REVIEW_CASE",
        raw_payload={
            "invoice_id": "INV-003",
            "reason": "manual_review_required",
            "blocking": True,
            "source_status": "ambiguous_match",
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

    from invomatch.services.restart_consistency_repair_service import (
        RestartConsistencyRepairService,
    )

    projection_store = SqliteFinalizedProjectionStore(tmp_path / "finalized_projections.sqlite3")
    service = RestartConsistencyRepairService(
        run_store=run_store,
        review_store=review_store,
        projection_store=projection_store,
    )

    repaired = service.repair_run(run.run_id)

    assert repaired is not None
    assert repaired.run_id == run.run_id
    assert repaired.original_status == "completed"
    assert repaired.repaired_status == "review_required"
    assert repaired.reason == "active_review_cases_present_for_completed_run"

    persisted = run_store.get_run(run.run_id)
    assert persisted is not None
    assert persisted.status == "review_required"