from __future__ import annotations

from pathlib import Path

from invomatch.domain.review.models import DecisionType, FeedbackRecord
from invomatch.services.review_service import ReviewService
from invomatch.services.sqlite_review_store import SqliteReviewStore


def test_sqlite_review_store_preserves_review_truth_after_reload(tmp_path: Path) -> None:
    db_path = tmp_path / "review_restart.db"

    first_store = SqliteReviewStore(db_path)
    review_service = ReviewService()

    session = review_service.create_review_session(
        created_by="system",
        assigned_reviewer_id="reviewer-1",
        session_notes="restart persistence test",
    )
    first_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="fb_restart_001",
        run_id="run_restart_001",
        source_type="reconciliation_result",
        source_reference="INV-001",
        feedback_type="manual_review",
        raw_payload={"invoice_id": "INV-001"},
        submitted_by="system",
    )
    first_store.save_feedback(feedback)

    review_item, audit_event = review_service.create_review_item(
        feedback=feedback,
        review_session=session,
    )
    first_store.save_review_item(review_item)
    first_store.save_audit_event(audit_event)

    start_audit = review_service.start_review(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer-1",
    )
    first_store.save_review_item(review_item)
    first_store.save_audit_event(start_audit)

    decision_result = review_service.apply_decision(
        feedback=feedback,
        review_item=review_item,
        reviewer_id="reviewer-1",
        decision=DecisionType.APPROVE,
        reason="approved before restart",
    )
    first_store.save_review_item(decision_result.review_item)
    first_store.save_decision_event(decision_result.decision_event)
    first_store.save_audit_event(decision_result.audit_event)
    if decision_result.eligibility_record is not None:
        first_store.save_eligibility_record(decision_result.eligibility_record)

    reloaded_store = SqliteReviewStore(db_path)

    loaded_session = reloaded_store.get_review_session(session.review_session_id)
    loaded_feedback = reloaded_store.get_feedback(feedback.feedback_id)
    loaded_item = reloaded_store.get_review_item(review_item.review_item_id)
    loaded_decision = reloaded_store.get_decision_event(
        decision_result.decision_event.decision_event_id
    )
    loaded_audit_events = reloaded_store.list_audit_events_for_entity(
        "review_item",
        review_item.review_item_id,
    )
    eligibility_records = reloaded_store.list_eligibility_records_for_item(
        review_item.review_item_id
    )

    assert loaded_session is not None
    assert loaded_session.review_session_id == session.review_session_id
    assert loaded_session.created_by == "system"

    assert loaded_feedback is not None
    assert loaded_feedback.feedback_id == "fb_restart_001"
    assert loaded_feedback.run_id == "run_restart_001"

    assert loaded_item is not None
    assert loaded_item.review_item_id == review_item.review_item_id
    assert loaded_item.feedback_id == feedback.feedback_id
    assert loaded_item.item_status.value == "APPROVED"
    assert loaded_item.current_decision == DecisionType.APPROVE
    assert loaded_item.reviewed_by == "reviewer-1"

    assert loaded_decision is not None
    assert loaded_decision.review_item_id == review_item.review_item_id
    assert loaded_decision.decision_type == DecisionType.APPROVE
    assert loaded_decision.actor_id == "reviewer-1"
    assert loaded_decision.decision_reason == "approved before restart"

    assert len(loaded_audit_events) >= 2

    assert len(eligibility_records) == 1
    assert eligibility_records[0].review_item_id == review_item.review_item_id