from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.handlers.resolve_review import ResolveReviewActionHandler
from invomatch.services.actions.result import ActionExecutionStatus


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


def test_resolve_review_handler_applies_approve_decision():
    handler = ResolveReviewActionHandler()
    command = ActionCommand(
        action_type="resolve_review",
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