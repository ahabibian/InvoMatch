from __future__ import annotations

from dataclasses import replace
from typing import Dict, List, Optional

from invomatch.domain.review.models import (
    AuditEvent,
    FeedbackRecord,
    LearningEligibilityRecord,
    ReviewDecisionEvent,
    ReviewItem,
    ReviewSession,
)


class InMemoryReviewStore:
    """
    Minimal in-memory persistence for the review domain.

    Purpose:
    - support service integration without introducing database complexity
    - provide deterministic storage behavior for tests
    - act as a temporary boundary before sqlite-backed persistence
    """

    def __init__(self) -> None:
        self._feedback_records: Dict[str, FeedbackRecord] = {}
        self._review_sessions: Dict[str, ReviewSession] = {}
        self._review_items: Dict[str, ReviewItem] = {}
        self._decision_events: Dict[str, ReviewDecisionEvent] = {}
        self._audit_events: Dict[str, AuditEvent] = {}
        self._eligibility_records: Dict[str, LearningEligibilityRecord] = {}

    # -------------------------------------------------------------------------
    # Feedback
    # -------------------------------------------------------------------------

    def save_feedback(self, feedback: FeedbackRecord) -> FeedbackRecord:
        self._feedback_records[feedback.feedback_id] = feedback
        return feedback

    def get_feedback(self, feedback_id: str) -> Optional[FeedbackRecord]:
        return self._feedback_records.get(feedback_id)

    def list_feedback(self) -> List[FeedbackRecord]:
        return list(self._feedback_records.values())

    # -------------------------------------------------------------------------
    # Review sessions
    # -------------------------------------------------------------------------

    def save_review_session(self, session: ReviewSession) -> ReviewSession:
        self._review_sessions[session.review_session_id] = session
        return session

    def get_review_session(self, review_session_id: str) -> Optional[ReviewSession]:
        return self._review_sessions.get(review_session_id)

    def list_review_sessions(self) -> List[ReviewSession]:
        return list(self._review_sessions.values())

    # -------------------------------------------------------------------------
    # Review items
    # -------------------------------------------------------------------------

    def save_review_item(self, item: ReviewItem) -> ReviewItem:
        self._review_items[item.review_item_id] = item
        return item

    def get_review_item(self, review_item_id: str) -> Optional[ReviewItem]:
        return self._review_items.get(review_item_id)

    def list_review_items(self) -> List[ReviewItem]:
        return list(self._review_items.values())

    def list_review_items_for_session(self, review_session_id: str) -> List[ReviewItem]:
        return [
            item
            for item in self._review_items.values()
            if item.review_session_id == review_session_id
        ]

    def list_review_items_for_feedback(self, feedback_id: str) -> List[ReviewItem]:
        return [
            item
            for item in self._review_items.values()
            if item.feedback_id == feedback_id
        ]

    # -------------------------------------------------------------------------
    # Decision events
    # -------------------------------------------------------------------------

    def save_decision_event(self, event: ReviewDecisionEvent) -> ReviewDecisionEvent:
        self._decision_events[event.decision_event_id] = event
        return event

    def get_decision_event(self, decision_event_id: str) -> Optional[ReviewDecisionEvent]:
        return self._decision_events.get(decision_event_id)

    def list_decision_events(self) -> List[ReviewDecisionEvent]:
        return list(self._decision_events.values())

    def list_decision_events_for_item(self, review_item_id: str) -> List[ReviewDecisionEvent]:
        return [
            event
            for event in self._decision_events.values()
            if event.review_item_id == review_item_id
        ]

    # -------------------------------------------------------------------------
    # Audit events
    # -------------------------------------------------------------------------

    def save_audit_event(self, event: AuditEvent) -> AuditEvent:
        self._audit_events[event.audit_event_id] = event
        return event

    def get_audit_event(self, audit_event_id: str) -> Optional[AuditEvent]:
        return self._audit_events.get(audit_event_id)

    def list_audit_events(self) -> List[AuditEvent]:
        return list(self._audit_events.values())

    def list_audit_events_for_entity(self, entity_type: str, entity_id: str) -> List[AuditEvent]:
        return [
            event
            for event in self._audit_events.values()
            if event.entity_type == entity_type and event.entity_id == entity_id
        ]

    # -------------------------------------------------------------------------
    # Learning eligibility
    # -------------------------------------------------------------------------

    def save_eligibility_record(
        self,
        record: LearningEligibilityRecord,
    ) -> LearningEligibilityRecord:
        self._eligibility_records[record.eligibility_id] = record
        return record

    def get_eligibility_record(
        self,
        eligibility_id: str,
    ) -> Optional[LearningEligibilityRecord]:
        return self._eligibility_records.get(eligibility_id)

    def list_eligibility_records(self) -> List[LearningEligibilityRecord]:
        return list(self._eligibility_records.values())

    def list_eligibility_records_for_item(
        self,
        review_item_id: str,
    ) -> List[LearningEligibilityRecord]:
        return [
            record
            for record in self._eligibility_records.values()
            if record.review_item_id == review_item_id
        ]

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------

    def clear(self) -> None:
        self._feedback_records.clear()
        self._review_sessions.clear()
        self._review_items.clear()
        self._decision_events.clear()
        self._audit_events.clear()
        self._eligibility_records.clear()

    def snapshot_counts(self) -> dict[str, int]:
        return {
            "feedback_records": len(self._feedback_records),
            "review_sessions": len(self._review_sessions),
            "review_items": len(self._review_items),
            "decision_events": len(self._decision_events),
            "audit_events": len(self._audit_events),
            "eligibility_records": len(self._eligibility_records),
        }