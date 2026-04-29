from __future__ import annotations

from pathlib import Path

from invomatch.domain.models import MatchResult, ReconciliationReport, ReconciliationResult, ReconciliationRun
from invomatch.domain.review.models import DecisionType
from invomatch.services.export.finalized_projection_store import SqliteFinalizedProjectionStore
from invomatch.services.export.finalized_projection_writer import FinalizedProjectionWriter
from invomatch.services.orchestration.export_readiness_evaluator import ExportReadinessEvaluator
from invomatch.services.orchestration.review_resolution_coordinator import ReviewResolutionCoordinator
from invomatch.services.orchestration.run_orchestration_service import RunOrchestrationService
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.restart_consistency_repair_service import RestartConsistencyRepairService
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import JsonRunStore


def _write_matched_files(tmp_path: Path) -> tuple[Path, Path]:
    invoice = tmp_path / "invoices.csv"
    payment = tmp_path / "payments.csv"

    invoice.write_text(
        "id,date,amount,currency,reference\n"
        "inv-1,2024-01-10,100.00,USD,INV-1\n",
        encoding="utf-8",
    )

    payment.write_text(
        "id,date,amount,currency,reference,invoice_id\n"
        "pay-1,2024-01-12,100.00,USD,INV-1,inv-1\n",
        encoding="utf-8",
    )

    return invoice, payment


def _review_required_run(run_id: str, tmp_path: Path) -> ReconciliationRun:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    invoice = tmp_path / "review_invoices.csv"
    payment = tmp_path / "review_payments.csv"

    invoice.write_text(
        "id,date,amount,currency,reference\n"
        "inv-review,2024-01-10,100.00,USD,INV-REVIEW\n",
        encoding="utf-8",
    )
    payment.write_text(
        "id,date,amount,currency,reference,invoice_id\n"
        "pay-review,2024-01-12,100.00,USD,INV-REVIEW,inv-review\n",
        encoding="utf-8",
    )

    report = ReconciliationReport(
        total_invoices=1,
        matched=0,
        duplicate_detected=0,
        partial_match=0,
        unmatched=1,
        results=[
            ReconciliationResult(
                invoice_id="inv-review",
                match_result=MatchResult(
                    status="unmatched",
                    payment_id=None,
                    payment_ids=[],
                    duplicate_payment_ids=None,
                    confidence_score=0.0,
                    confidence_explanation="requires review",
                    mismatch_reasons=["no_viable_candidate"],
                ),
            )
        ],
    )

    return ReconciliationRun(
        run_id=run_id,
        tenant_id="tenant-test",
        status="processing",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=None,
        claimed_by="worker-test",
        claimed_at=now,
        lease_expires_at=now,
        attempt_count=1,
        invoice_csv_path=str(invoice),
        payment_csv_path=str(payment),
        error_message=None,
        report=report,
    )


def test_happy_path_completion_persists_projection_automatically(tmp_path: Path) -> None:
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = InMemoryReviewStore()
    projection_store = SqliteFinalizedProjectionStore(tmp_path / "finalized_projections.sqlite3")

    invoice, payment = _write_matched_files(tmp_path)

    run = reconcile_and_save(
        invoice_csv_path=invoice,
        payment_csv_path=payment,
        tenant_id="tenant-test",
        run_store=run_store,
        review_store=review_store,
        projection_store=projection_store,
    )

    assert run.status == "completed"
    assert projection_store.exists(tenant_id="tenant-test", run_id=run.run_id)

    readiness = ExportReadinessEvaluator(
        run_store=run_store,
        review_store=review_store,
        projection_store=projection_store,
    ).evaluate(run.run_id)

    assert readiness.is_export_ready is True
    assert readiness.reason == "export_allowed"


def test_review_resolution_completion_persists_projection_automatically(tmp_path: Path) -> None:
    run_id = "run-review-lifecycle"
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = InMemoryReviewStore()
    review_service = ReviewService()
    projection_store = SqliteFinalizedProjectionStore(tmp_path / "finalized_projections.sqlite3")

    run_store.create_run(_review_required_run(run_id, tmp_path))

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

    post_match_result, persisted_after_match = orchestration_service.orchestrate_and_persist_post_matching(
        run_id=run_id,
        reconciliation_outcomes=[
            {"invoice_id": "inv-review", "status": "unmatched", "reason": "no_match"},
        ],
        tenant_id="tenant-test",
        run_store=run_store,
    )

    assert post_match_result.run_status == "review_required"
    assert persisted_after_match.status == "review_required"
    assert projection_store.exists(tenant_id="tenant-test", run_id=run_id) is False

    review_item = review_store.list_review_items()[0]
    feedback = review_store.get_feedback(review_item.feedback_id)
    assert feedback is not None

    _, persisted_after_resolution = coordinator.resolve_and_reconcile(
        run_id=run_id,
        review_item_id=review_item.review_item_id,
        feedback_id=feedback.feedback_id,
        reviewer_id="reviewer-test",
        decision=DecisionType.APPROVE,
        reason="approved lifecycle test",
        tenant_id="tenant-test",
        run_store=run_store,
    )

    assert persisted_after_resolution.status == "completed"
    assert projection_store.exists(tenant_id="tenant-test", run_id=run_id)


def test_projection_writer_is_idempotent_for_completed_run(tmp_path: Path) -> None:
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = InMemoryReviewStore()
    projection_store = SqliteFinalizedProjectionStore(tmp_path / "finalized_projections.sqlite3")

    invoice, payment = _write_matched_files(tmp_path)

    run = reconcile_and_save(
        invoice_csv_path=invoice,
        payment_csv_path=payment,
        tenant_id="tenant-test",
        run_store=run_store,
        review_store=review_store,
        projection_store=projection_store,
    )

    writer = FinalizedProjectionWriter(
        projection_store=projection_store,
        review_store=review_store,
    )

    writer.persist_for_completed_run(run)
    writer.persist_for_completed_run(run)

    results = projection_store.get_results(tenant_id="tenant-test", run_id=run.run_id)

    assert results is not None
    assert len(results) == 1

def test_restart_repair_completion_persists_projection_automatically(tmp_path: Path) -> None:
    run_id = "run-repair-lifecycle"
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = InMemoryReviewStore()
    projection_store = SqliteFinalizedProjectionStore(tmp_path / "finalized_projections.sqlite3")

    review_required_run = _review_required_run(run_id, tmp_path).model_copy(
        update={
            "status": "review_required",
            "version": 1,
        }
    )
    run_store.create_run(review_required_run)

    repair_service = RestartConsistencyRepairService(
        run_store=run_store,
        review_store=review_store,
        projection_store=projection_store,
    )

    repair_result = repair_service.repair_run(run_id)

    assert repair_result is not None
    assert repair_result.original_status == "review_required"
    assert repair_result.repaired_status == "completed"
    assert repair_result.reason == "no_active_review_cases_remaining"

    persisted = run_store.get_run(run_id, tenant_id="tenant-test")
    assert persisted is not None
    assert persisted.status == "completed"
    assert projection_store.exists(tenant_id="tenant-test", run_id=run_id)
