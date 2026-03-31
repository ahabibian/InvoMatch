from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.handlers.resolve_review import ResolveReviewActionHandler
from invomatch.services.actions.result import ActionExecutionStatus
from invomatch.services.action_service import ActionService
from invomatch.api.product_models.action import ProductActionRequest


def _payload():
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
        "feedback_status": "REVIEWED",
        "review_item_status": "APPROVED",
        "current_decision": "APPROVE",
        "eligibility_status": "ELIGIBLE",
    }


def test_resolve_review_handler_returns_no_op_for_same_terminal_decision():
    handler = ResolveReviewActionHandler()
    command = ActionCommand(
        action_type="resolve_review",
        run_id="run-123",
        target_id="case-1",
        payload=_payload(),
        note="repeat approve",
    )

    result = handler.handle(command)

    assert result.status == ActionExecutionStatus.NO_OP
    assert result.state_changes == []
    assert result.side_effects == []
    assert result.audit_event_ids == []
    assert result.response_payload["review_item_status"] == "APPROVED"


def test_resolve_review_handler_returns_conflict_for_different_terminal_decision():
    handler = ResolveReviewActionHandler()
    payload = _payload()
    payload["decision"] = "REJECT"

    command = ActionCommand(
        action_type="resolve_review",
        run_id="run-123",
        target_id="case-1",
        payload=payload,
        note="conflicting reject",
    )

    result = handler.handle(command)

    assert result.status == ActionExecutionStatus.CONFLICT
    assert result.state_changes == []
    assert result.side_effects == []
    assert result.audit_event_ids == []
    assert result.response_payload["review_item_status"] == "APPROVED"
    assert result.response_payload["decision"] == "APPROVE"


def test_action_service_maps_conflict_status():
    service = ActionService()
    payload = _payload()
    payload["decision"] = "REJECT"

    result = service.execute(
        run_id="run-123",
        request=ProductActionRequest(
            action_type="resolve_review",
            target_id="case-1",
            payload=payload,
            note="conflicting reject",
        ),
    )

    assert result.accepted is False
    assert result.status == "conflict"