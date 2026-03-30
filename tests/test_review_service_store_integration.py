from __future__ import annotations

from invomatch.domain.review.models import (
    DecisionType,
    EligibilityStatus,
    FeedbackRecord,
    FeedbackStatus,
    ReviewItemStatus,
    ReviewSessionStatus,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore


def make_feedback() -> FeedbackRecord:
    return FeedbackRecord(
        feedback_id="fb_integration_001",
        run_id="run_integration_001",
        source_type="user_action",
        source_reference="match:integration:001",
        feedback_type="correction",
        raw_payload={
            "invoice_id": "inv_500",
            "payment_id": "pay_900",
            "match_confidence": 0.38,
        },
        submitted_by="user_integration",
    )


def test_review_flow_approve_persists_entities_end_to_end() -> None:
    service = ReviewService()
    store = InMemoryReviewStore()

    feedback = make_feedback()
    store.save_feedback(feedback)

    session = service.create_review_session(
        created_by="system",
        assigned_reviewer_id="reviewer_1",
        session_notes="integration review session",
    )
    store.save_review_session(session)

    assert session.session_status == ReviewSessionStatus.IN_PROGRESS
    assert store.get_review_session(session.review_session_id) is session

    review_item, created_audit_event = service.create_review_item(
        feedback=feedback,
        review_session=session,
    )
    store.save_feedback(feedback)
    store.save_review_item(review_item)
    store.save_audit_event(created_audit_event)

    assert feedback.feedback_status == FeedbackStatus.QUEUED_FOR_REVIEW
    assert store.get_feedback(feedback.feedback_id) is feedback
    assert store.get_review_item(review_item.review_item_id) is review_item
    assert store.get_audit_event(created_audit_event.audit_event_id) is created_audit_event

    start_audit_event = service.start_review(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_1",
    )
    store.save_feedback(feedback)
    store.save_review_item(review_item)
    store.save_audit_event(start_audit_event)

    assert feedback.feedback_status == FeedbackStatus.UNDER_REVIEW
    assert review_item.item_status == ReviewItemStatus.IN_REVIEW
    assert start_audit_event.action_type == "REVIEW_STARTED"

    result = service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_1",
        decision=DecisionType.APPROVE,
        reason="Approved during integration flow",
    )

    store.save_feedback(feedback)
    store.save_review_item(result.review_item)
    store.save_decision_event(result.decision_event)
    store.save_audit_event(result.audit_event)

    assert result.eligibility_record is not None
    store.save_eligibility_record(result.eligibility_record)

    persisted_feedback = store.get_feedback(feedback.feedback_id)
    persisted_item = store.get_review_item(review_item.review_item_id)
    persisted_decision = store.get_decision_event(result.decision_event.decision_event_id)
    persisted_audit = store.get_audit_event(result.audit_event.audit_event_id)
    persisted_eligibility = store.get_eligibility_record(result.eligibility_record.eligibility_id)

    assert persisted_feedback is not None
    assert persisted_item is not None
    assert persisted_decision is not None
    assert persisted_audit is not None
    assert persisted_eligibility is not None

    assert persisted_feedback.feedback_status == FeedbackStatus.REVIEWED
    assert persisted_item.item_status == ReviewItemStatus.APPROVED
    assert persisted_item.learning_eligible is True
    assert persisted_decision.decision_type == DecisionType.APPROVE
    assert persisted_audit.action_type == "REVIEW_DECISION_APPROVE"
    assert persisted_eligibility.eligibility_status == EligibilityStatus.ELIGIBLE
    assert persisted_eligibility.derived_payload == feedback.raw_payload

    counts = store.snapshot_counts()
    assert counts["feedback_records"] == 1
    assert counts["review_sessions"] == 1
    assert counts["review_items"] == 1
    assert counts["decision_events"] == 1
    assert counts["audit_events"] == 3
    assert counts["eligibility_records"] == 1


def test_review_flow_modify_persists_reviewed_payload_not_raw_payload() -> None:
    service = ReviewService()
    store = InMemoryReviewStore()

    feedback = make_feedback()
    store.save_feedback(feedback)

    session = service.create_review_session(created_by="system")
    store.save_review_session(session)

    review_item, created_audit_event = service.create_review_item(
        feedback=feedback,
        review_session=session,
    )
    store.save_feedback(feedback)
    store.save_review_item(review_item)
    store.save_audit_event(created_audit_event)

    start_audit_event = service.start_review(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_2",
    )
    store.save_feedback(feedback)
    store.save_review_item(review_item)
    store.save_audit_event(start_audit_event)

    reviewed_payload = {
        "invoice_id": "inv_500",
        "payment_id": "pay_corrected_001",
        "match_confidence": 0.96,
    }

    result = service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer_2",
        decision=DecisionType.MODIFY,
        reason="Corrected during integration flow",
        reviewed_payload=reviewed_payload,
    )

    store.save_feedback(feedback)
    store.save_review_item(result.review_item)
    store.save_decision_event(result.decision_event)
    store.save_audit_event(result.audit_event)

    assert result.eligibility_record is not None
    store.save_eligibility_record(result.eligibility_record)

    persisted_item = store.get_review_item(review_item.review_item_id)
    persisted_eligibility = store.get_eligibility_record(result.eligibility_record.eligibility_id)

    assert persisted_item is not None
    assert persisted_eligibility is not None

    assert persisted_item.item_status == ReviewItemStatus.MODIFIED
    assert persisted_item.reviewed_payload == reviewed_payload
    assert persisted_eligibility.eligibility_status == EligibilityStatus.ELIGIBLE
    assert persisted_eligibility.derived_payload == reviewed_payload
    assert persisted_eligibility.derived_payload != feedback.raw_payload