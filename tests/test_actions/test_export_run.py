from pathlib import Path

from invomatch.api.product_models.action import ProductActionRequest
from invomatch.domain.models import ReconciliationReport, ReconciliationResult, MatchResult
from invomatch.domain.review.models import DecisionType, FeedbackRecord
from invomatch.services.action_service import ActionService
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.handlers.export_run import ExportRunActionHandler
from invomatch.services.actions.result import ActionExecutionStatus
from invomatch.services.export.export_service import ExportService
from invomatch.services.export.run_finalized_result_reader import RunFinalizedResultReader
from invomatch.services.reconciliation_runs import (
    create_reconciliation_run,
    update_reconciliation_run,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import JsonRunStore


def _completed_run_store(tmp_path: Path) -> tuple[JsonRunStore, str]:
    run_store = JsonRunStore(tmp_path / "runs.json")

    invoice_path = tmp_path / "invoices.csv"
    payment_path = tmp_path / "payments.csv"

    invoice_path.write_text(
        "\n".join(
            [
                "id,date,amount,currency,reference",
                "inv-1,2024-01-10,100.00,USD,INV-1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payment_path.write_text(
        "\n".join(
            [
                "id,date,amount,currency,reference",
                "pay-1,2024-01-12,100.00,USD,Payment for INV-1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    run = create_reconciliation_run(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )

    update_reconciliation_run(run.run_id, status="running", run_store=run_store)

    report = ReconciliationReport(
        total_invoices=1,
        matched=1,
        unmatched=0,
        duplicate_detected=0,
        partial_match=0,
        results=[
            ReconciliationResult(
                invoice_id="inv-1",
                match_result=MatchResult(
                    status="matched",
                    payment_id="pay-1",
                    payment_ids=["pay-1"],
                    duplicate_payment_ids=None,
                    confidence_score=0.99,
                    confidence_explanation="exact match",
                    mismatch_reasons=["amount_match", "reference_match"],
                ),
            )
        ],
    )

    completed = update_reconciliation_run(
        run.run_id,
        status="completed",
        report=report,
        run_store=run_store,
    )

    return run_store, completed.run_id


def _seed_approved_review(review_store: InMemoryReviewStore, run_id: str) -> None:
    review_service = ReviewService()

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="fb_inv_1",
        run_id=run_id,
        source_type="reconciliation_result",
        source_reference="inv-1",
        feedback_type="manual_review",
        raw_payload={
            "invoice_id": "inv-1",
            "payment_ids": ["pay-1"],
            "reason_code": "action_export_test",
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
        reason="approved for export",
    )
    review_store.save_review_item(decision_result.review_item)
    review_store.save_decision_event(decision_result.decision_event)
    review_store.save_audit_event(decision_result.audit_event)
    if decision_result.eligibility_record is not None:
        review_store.save_eligibility_record(decision_result.eligibility_record)


def test_export_run_handler_returns_metadata(tmp_path: Path):
    run_store, run_id = _completed_run_store(tmp_path)
    review_store = InMemoryReviewStore()
    _seed_approved_review(review_store, run_id)

    export_service = ExportService(
        run_store=run_store,
        reader=RunFinalizedResultReader(
            run_store=run_store,
            review_store=review_store,
        ),
    )
    handler = ExportRunActionHandler(export_service=export_service)

    command = ActionCommand(
        action_type="export_run",
        run_id=run_id,
        payload={"format": "json"},
    )

    result = handler.handle(command)

    assert result.status == ActionExecutionStatus.SUCCESS
    assert result.response_payload["run_id"] == run_id
    assert result.response_payload["export_status"] == "completed"
    assert result.response_payload["export_format"] == "json"
    assert result.response_payload["content_type"] == "application/json"
    assert result.response_payload["filename"] == f"run_{run_id}.json"


def test_action_service_rejects_export_without_format():
    service = ActionService()

    result = service.execute(
        run_id="run-123",
        request=ProductActionRequest(
            action_type="export_run",
            payload={},
        ),
    )

    assert result.accepted is False
    assert result.status == "invalid_request"
