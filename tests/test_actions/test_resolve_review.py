from datetime import datetime, timezone

from invomatch.domain.models import ReconciliationRun
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.handlers.resolve_review import ResolveReviewActionHandler
from invomatch.services.actions.result import ActionExecutionStatus
from invomatch.services.orchestration.run_orchestration_service import (
    RunOrchestrationService,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import InMemoryRunStore


def _base_payload():
    return {
        "decision": "APPROVE",
        "reviewer_id": "reviewer-1",
        "feedback_id": "feedback-1",
        "review_session_id": "review-session-1",
        "review_item_id": "review-item-1",
        "source_type": "manual_review",
        "source_reference": "case-1",
        "feedback_type": "review_resolution",
        "raw_payload": {"matched": False},
        "submitted_by": "system",
        "feedback_status": "UNDER_REVIEW",
        "review_item_status": "IN_REVIEW",
    }


def _review_required_run(run_id: str) -> ReconciliationRun:
    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        tenant_id="tenant-test",

        run_id=run_id,
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


def test_resolve_review_handler_applies_approve_decision():
    handler = ResolveReviewActionHandler()
    command = ActionCommand(
        action_type="resolve_review",
        tenant_id="tenant-test",

        run_id="run-123",
        target_id="case-1",
        payload=_base_payload(),
        note="approved by reviewer",
    )

    result = handler.handle(command)

    assert result.status == ActionExecutionStatus.SUCCESS
    assert result.target_type == "review_item"
    assert result.target_id == "review-item-1"
    assert result.response_payload["review_item_status"] == "APPROVED"
    assert result.response_payload["feedback_status"] == "REVIEWED"
    assert result.response_payload["decision"] == "APPROVE"
    assert result.response_payload["eligibility_status"] == "ELIGIBLE"
    assert len(result.state_changes) == 2
    assert len(result.side_effects) == 3
    assert len(result.audit_event_ids) == 1


def test_resolve_review_handler_requires_reviewed_payload_for_modify():
    handler = ResolveReviewActionHandler()
    payload = _base_payload()
    payload["decision"] = "MODIFY"

    command = ActionCommand(
        action_type="resolve_review",
        tenant_id="tenant-test",

        run_id="run-123",
        target_id="case-1",
        payload=payload,
        note="modified by reviewer",
    )

    try:
        handler.handle(command)
    except ValueError as exc:
        assert "reviewed_payload is required for MODIFY decisions" in str(exc)
    else:
        raise AssertionError("Expected ValueError for MODIFY without reviewed_payload")


def test_resolve_review_handler_uses_persisted_coordinator_path_and_completes_run():
    run = _review_required_run("run-456")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    review_service = ReviewService()
    orchestration_service = RunOrchestrationService(
        review_store=review_store,
        review_service=review_service,
    )

    orchestration_service.orchestrate_post_matching(
        tenant_id="tenant-test",

        run_id=run.run_id,
        reconciliation_outcomes=[
            {"invoice_id": "INV-500", "status": "unmatched", "reason": "no_match"},
        ],
    )

    review_item = review_store.list_review_items()[0]
    feedback = review_store.get_feedback(review_item.feedback_id)

    handler = ResolveReviewActionHandler(
        review_service=review_service,
        review_store=review_store,
        run_store=run_store,
        run_orchestration_service=orchestration_service,
    )

    payload = {
        "decision": "APPROVE",
        "reviewer_id": "reviewer-9",
        "feedback_id": feedback.feedback_id,
        "review_session_id": review_item.review_session_id,
        "review_item_id": review_item.review_item_id,
        "source_type": feedback.source_type,
        "source_reference": feedback.source_reference,
        "feedback_type": feedback.feedback_type,
        "raw_payload": feedback.raw_payload,
        "submitted_by": feedback.submitted_by,
        "feedback_status": feedback.feedback_status.value,
        "review_item_status": review_item.item_status.value,
    }

    command = ActionCommand(
        action_type="resolve_review",
        tenant_id="tenant-test",

        run_id=run.run_id,
        target_id=feedback.source_reference,
        payload=payload,
        note="approved through persisted path",
    )

    result = handler.handle(command)

    persisted_run = run_store.get_run(run.run_id)

    assert result.status == ActionExecutionStatus.SUCCESS
    assert result.response_payload["review_item_status"] == "APPROVED"
    assert result.response_payload["feedback_status"] == "REVIEWED"
    assert result.response_payload["decision"] == "APPROVE"
    assert result.response_payload["eligibility_status"] == "ELIGIBLE"
    assert result.response_payload["run_status"] == "completed"
    assert persisted_run is not None
    assert persisted_run.status == "completed"