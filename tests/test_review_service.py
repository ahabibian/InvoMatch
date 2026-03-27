from __future__ import annotations

import pytest

from invomatch.domain.review.models import (
    DecisionType,
    EligibilityStatus,
    FeedbackRecord,
    FeedbackStatus,
    ReviewItemStatus,
)
from invomatch.services.review_service import ReviewService


def make_feedback() -> FeedbackRecord:
    return FeedbackRecord(
        feedback_id="fb_001",
        run_id="run_001",
        source_type="user_action",
        source_reference="match:123",
        feedback_type="correction",
        raw_payload={
            "invoice_id": "inv_100",
            "payment_id": "pay_200",
            "match_confidence": 0.42,
        },
        submitted_by="user_1",
    )


def test_create_review_item_queues_feedback_and_emits_audit_event() -> None:
    service = ReviewService()
    feedback = make_feedback()
    session = service.create_review_session(created_by="system")

    review_item, audit_event = service.create_review_item(
        feedback=feedback,
        review_session=session,
    )

    assert feedback.feedback_status == FeedbackStatus.QUEUED_FOR_REVIEW
    assert review_item.feedback_id == feedback.feedback_id
    assert review_item.review_session_id == session.review_session_id
    assert review_item.item_status == ReviewItemStatus.PENDING

    assert audit_event.entity_type == "review_item"
    assert audit_event.entity_id == review_item.review_item_id
    assert audit_event.action_type == "REVIEW_ITEM_CREATED"
    assert audit_event.event_payload is not None
    assert audit_event.event_payload["feedback_id"] == feedback.feedback_id


def test_start_review_moves_feedback_and_item_to_under_review_state() -> None:
    service = ReviewService()
    feedback = make_feedback()
    session = service.create_review_session(created_by="system", assigned_reviewer_id="reviewer_1")
    review_item, _ = service.create_review_item(feedback=feedback, review_session=session)

    audit_event = service.start_review(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_1",
    )

    assert feedback.feedback_status == FeedbackStatus.UNDER_REVIEW
    assert review_item.item_status == ReviewItemStatus.IN_REVIEW
    assert audit_event.action_type == "REVIEW_STARTED"
    assert audit_event.actor_id == "reviewer_1"


def test_apply_approve_marks_item_reviewed_and_creates_eligible_record() -> None:
    service = ReviewService()
    feedback = make_feedback()
    session = service.create_review_session(created_by="system")
    review_item, _ = service.create_review_item(feedback=feedback, review_session=session)
    service.start_review(feedback=feedback, review_item=review_item, reviewer_id="reviewer_1")

    result = service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_1",
        decision=DecisionType.APPROVE,
        reason="Valid correction",
    )

    assert result.review_item.item_status == ReviewItemStatus.APPROVED
    assert result.review_item.learning_eligible is True
    assert result.decision_event.decision_type == DecisionType.APPROVE
    assert result.audit_event.action_type == "REVIEW_DECISION_APPROVE"

    assert result.eligibility_record is not None
    assert result.eligibility_record.eligibility_status == EligibilityStatus.ELIGIBLE
    assert result.eligibility_record.derived_payload == feedback.raw_payload

    assert feedback.feedback_status == FeedbackStatus.REVIEWED


def test_apply_reject_marks_item_ineligible() -> None:
    service = ReviewService()
    feedback = make_feedback()
    session = service.create_review_session(created_by="system")
    review_item, _ = service.create_review_item(feedback=feedback, review_session=session)
    service.start_review(feedback=feedback, review_item=review_item, reviewer_id="reviewer_1")

    result = service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_1",
        decision=DecisionType.REJECT,
        reason="Incorrect correction",
    )

    assert result.review_item.item_status == ReviewItemStatus.REJECTED
    assert result.review_item.learning_eligible is False
    assert result.eligibility_record is not None
    assert result.eligibility_record.eligibility_status == EligibilityStatus.INELIGIBLE
    assert result.eligibility_record.derived_payload is None
    assert feedback.feedback_status == FeedbackStatus.REVIEWED


def test_modify_requires_reviewed_payload() -> None:
    service = ReviewService()
    feedback = make_feedback()
    session = service.create_review_session(created_by="system")
    review_item, _ = service.create_review_item(feedback=feedback, review_session=session)
    service.start_review(feedback=feedback, review_item=review_item, reviewer_id="reviewer_1")

    with pytest.raises(ValueError, match="reviewed_payload is required for MODIFY decisions"):
        service.apply_decision(
            feedback=feedback,
            review_item=review_item,
            reviewer_id="reviewer_1",
            decision=DecisionType.MODIFY,
            reason="Adjusted correction",
        )


def test_apply_modify_uses_reviewed_payload_for_eligibility() -> None:
    service = ReviewService()
    feedback = make_feedback()
    session = service.create_review_session(created_by="system")
    review_item, _ = service.create_review_item(feedback=feedback, review_session=session)
    service.start_review(feedback=feedback, review_item=review_item, reviewer_id="reviewer_1")

    reviewed_payload = {
        "invoice_id": "inv_100",
        "payment_id": "pay_777",
        "match_confidence": 0.91,
    }

    result = service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_1",
        decision=DecisionType.MODIFY,
        reason="Payload corrected during review",
        reviewed_payload=reviewed_payload,
    )

    assert result.review_item.item_status == ReviewItemStatus.MODIFIED
    assert result.review_item.learning_eligible is True
    assert result.review_item.reviewed_payload == reviewed_payload

    assert result.eligibility_record is not None
    assert result.eligibility_record.eligibility_status == EligibilityStatus.ELIGIBLE
    assert result.eligibility_record.derived_payload == reviewed_payload

    assert feedback.feedback_status == FeedbackStatus.REVIEWED


def test_apply_defer_keeps_feedback_under_review_and_marks_pending_eligibility() -> None:
    service = ReviewService()
    feedback = make_feedback()
    session = service.create_review_session(created_by="system")
    review_item, _ = service.create_review_item(feedback=feedback, review_session=session)
    service.start_review(feedback=feedback, review_item=review_item, reviewer_id="reviewer_1")

    result = service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_1",
        decision=DecisionType.DEFER,
        reason="Need more context",
    )

    assert result.review_item.item_status == ReviewItemStatus.DEFERRED
    assert result.review_item.learning_eligible is False
    assert result.review_item.requires_followup is True

    assert result.eligibility_record is not None
    assert result.eligibility_record.eligibility_status == EligibilityStatus.PENDING

    assert feedback.feedback_status == FeedbackStatus.UNDER_REVIEW


def test_apply_reopen_returns_item_to_in_review_and_marks_pending_eligibility() -> None:
    service = ReviewService()
    feedback = make_feedback()
    session = service.create_review_session(created_by="system")
    review_item, _ = service.create_review_item(feedback=feedback, review_session=session)
    service.start_review(feedback=feedback, review_item=review_item, reviewer_id="reviewer_1")

    service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_1",
        decision=DecisionType.APPROVE,
        reason="Initial approval",
    )

    result = service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_1",
        decision=DecisionType.REOPEN,
        reason="Reopened for re-review",
    )

    assert result.review_item.item_status == ReviewItemStatus.IN_REVIEW
    assert result.review_item.learning_eligible is False
    assert result.review_item.requires_followup is True

    assert result.eligibility_record is not None
    assert result.eligibility_record.eligibility_status == EligibilityStatus.PENDING

    assert feedback.feedback_status == FeedbackStatus.UNDER_REVIEW