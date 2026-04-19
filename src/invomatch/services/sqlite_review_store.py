from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from invomatch.domain.review.models import (
    AuditEvent,
    DecisionType,
    EligibilityStatus,
    FeedbackRecord,
    LearningEligibilityRecord,
    ReviewDecisionEvent,
    ReviewItem,
    ReviewItemStatus,
    ReviewSession,
    ReviewSessionStatus,
)


def _dt(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.isoformat()


def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    return datetime.fromisoformat(value)


class SqliteReviewStore:
    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback_records (
                    feedback_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_reference TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    raw_payload_json TEXT NOT NULL,
                    submitted_by TEXT NOT NULL,
                    submitted_at TEXT NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS review_sessions (
                    review_session_id TEXT PRIMARY KEY,
                    created_by TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    session_status TEXT NOT NULL,
                    assigned_reviewer_id TEXT NULL,
                    assigned_at TEXT NULL,
                    completed_at TEXT NULL,
                    session_notes TEXT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS review_items (
                    review_item_id TEXT PRIMARY KEY,
                    review_session_id TEXT NOT NULL,
                    feedback_id TEXT NOT NULL,
                    item_status TEXT NOT NULL,
                    current_decision TEXT NULL,
                    decision_reason TEXT NULL,
                    reviewed_payload_json TEXT NULL,
                    reviewed_by TEXT NULL,
                    reviewed_at TEXT NULL,
                    requires_followup INTEGER NOT NULL,
                    learning_eligible INTEGER NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS review_decision_events (
                    decision_event_id TEXT PRIMARY KEY,
                    review_item_id TEXT NOT NULL,
                    decision_type TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    previous_state TEXT NOT NULL,
                    new_state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    decision_reason TEXT NULL,
                    decision_payload_json TEXT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS review_audit_events (
                    audit_event_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    context_reference TEXT NULL,
                    event_payload_json TEXT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS review_eligibility_records (
                    eligibility_id TEXT PRIMARY KEY,
                    review_item_id TEXT NOT NULL,
                    feedback_id TEXT NOT NULL,
                    eligibility_status TEXT NOT NULL,
                    eligibility_reason TEXT NULL,
                    derived_payload_json TEXT NULL,
                    created_at TEXT NOT NULL,
                    created_by_system TEXT NOT NULL,
                    invalidated_at TEXT NULL
                )
                """
            )

            conn.commit()

    # -------------------------------------------------------------------------
    # Feedback
    # -------------------------------------------------------------------------

    def save_feedback(self, feedback: FeedbackRecord) -> FeedbackRecord:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO feedback_records (
                    feedback_id,
                    run_id,
                    source_type,
                    source_reference,
                    feedback_type,
                    raw_payload_json,
                    submitted_by,
                    submitted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    feedback.feedback_id,
                    feedback.run_id,
                    feedback.source_type,
                    feedback.source_reference,
                    feedback.feedback_type,
                    json.dumps(feedback.raw_payload, sort_keys=True),
                    feedback.submitted_by,
                    _dt(feedback.submitted_at),
                ),
            )
            conn.commit()
        return feedback

    def get_feedback(self, feedback_id: str) -> Optional[FeedbackRecord]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    feedback_id,
                    run_id,
                    source_type,
                    source_reference,
                    feedback_type,
                    raw_payload_json,
                    submitted_by,
                    submitted_at
                FROM feedback_records
                WHERE feedback_id = ?
                """,
                (feedback_id,),
            ).fetchone()

        if row is None:
            return None

        return FeedbackRecord(
            feedback_id=row["feedback_id"],
            run_id=row["run_id"],
            source_type=row["source_type"],
            source_reference=row["source_reference"],
            feedback_type=row["feedback_type"],
            raw_payload=json.loads(row["raw_payload_json"]),
            submitted_by=row["submitted_by"],
            submitted_at=_parse_dt(row["submitted_at"]) or datetime.now(),
        )

    def list_feedback(self) -> list[FeedbackRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    feedback_id,
                    run_id,
                    source_type,
                    source_reference,
                    feedback_type,
                    raw_payload_json,
                    submitted_by,
                    submitted_at
                FROM feedback_records
                ORDER BY submitted_at ASC, feedback_id ASC
                """
            ).fetchall()

        return [
            FeedbackRecord(
                feedback_id=row["feedback_id"],
                run_id=row["run_id"],
                source_type=row["source_type"],
                source_reference=row["source_reference"],
                feedback_type=row["feedback_type"],
                raw_payload=json.loads(row["raw_payload_json"]),
                submitted_by=row["submitted_by"],
                submitted_at=_parse_dt(row["submitted_at"]) or datetime.now(),
            )
            for row in rows
        ]

    # -------------------------------------------------------------------------
    # Review sessions
    # -------------------------------------------------------------------------

    def save_review_session(self, session: ReviewSession) -> ReviewSession:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO review_sessions (
                    review_session_id,
                    created_by,
                    created_at,
                    session_status,
                    assigned_reviewer_id,
                    assigned_at,
                    completed_at,
                    session_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.review_session_id,
                    session.created_by,
                    _dt(session.created_at),
                    session.session_status.value,
                    session.assigned_reviewer_id,
                    _dt(session.assigned_at),
                    _dt(session.completed_at),
                    session.session_notes,
                ),
            )
            conn.commit()
        return session

    def get_review_session(self, review_session_id: str) -> Optional[ReviewSession]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    review_session_id,
                    created_by,
                    created_at,
                    session_status,
                    assigned_reviewer_id,
                    assigned_at,
                    completed_at,
                    session_notes
                FROM review_sessions
                WHERE review_session_id = ?
                """,
                (review_session_id,),
            ).fetchone()

        if row is None:
            return None

        return ReviewSession(
            review_session_id=row["review_session_id"],
            created_by=row["created_by"],
            created_at=_parse_dt(row["created_at"]) or datetime.now(),
            session_status=ReviewSessionStatus(row["session_status"]),
            assigned_reviewer_id=row["assigned_reviewer_id"],
            assigned_at=_parse_dt(row["assigned_at"]),
            completed_at=_parse_dt(row["completed_at"]),
            session_notes=row["session_notes"],
        )

    def list_review_sessions(self) -> list[ReviewSession]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    review_session_id,
                    created_by,
                    created_at,
                    session_status,
                    assigned_reviewer_id,
                    assigned_at,
                    completed_at,
                    session_notes
                FROM review_sessions
                ORDER BY created_at ASC, review_session_id ASC
                """
            ).fetchall()

        return [
            ReviewSession(
                review_session_id=row["review_session_id"],
                created_by=row["created_by"],
                created_at=_parse_dt(row["created_at"]) or datetime.now(),
                session_status=ReviewSessionStatus(row["session_status"]),
                assigned_reviewer_id=row["assigned_reviewer_id"],
                assigned_at=_parse_dt(row["assigned_at"]),
                completed_at=_parse_dt(row["completed_at"]),
                session_notes=row["session_notes"],
            )
            for row in rows
        ]

    # -------------------------------------------------------------------------
    # Review items
    # -------------------------------------------------------------------------

    def save_review_item(self, item: ReviewItem) -> ReviewItem:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO review_items (
                    review_item_id,
                    review_session_id,
                    feedback_id,
                    item_status,
                    current_decision,
                    decision_reason,
                    reviewed_payload_json,
                    reviewed_by,
                    reviewed_at,
                    requires_followup,
                    learning_eligible
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.review_item_id,
                    item.review_session_id,
                    item.feedback_id,
                    item.item_status.value,
                    item.current_decision.value if item.current_decision else None,
                    item.decision_reason,
                    json.dumps(item.reviewed_payload, sort_keys=True) if item.reviewed_payload is not None else None,
                    item.reviewed_by,
                    _dt(item.reviewed_at),
                    1 if item.requires_followup else 0,
                    1 if item.learning_eligible else 0,
                ),
            )
            conn.commit()
        return item

    def get_review_item(self, review_item_id: str) -> Optional[ReviewItem]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    review_item_id,
                    review_session_id,
                    feedback_id,
                    item_status,
                    current_decision,
                    decision_reason,
                    reviewed_payload_json,
                    reviewed_by,
                    reviewed_at,
                    requires_followup,
                    learning_eligible
                FROM review_items
                WHERE review_item_id = ?
                """,
                (review_item_id,),
            ).fetchone()

        if row is None:
            return None

        return ReviewItem(
            review_item_id=row["review_item_id"],
            review_session_id=row["review_session_id"],
            feedback_id=row["feedback_id"],
            item_status=ReviewItemStatus(row["item_status"]),
            current_decision=DecisionType(row["current_decision"]) if row["current_decision"] else None,
            decision_reason=row["decision_reason"],
            reviewed_payload=json.loads(row["reviewed_payload_json"]) if row["reviewed_payload_json"] else None,
            reviewed_by=row["reviewed_by"],
            reviewed_at=_parse_dt(row["reviewed_at"]),
            requires_followup=bool(row["requires_followup"]),
            learning_eligible=bool(row["learning_eligible"]),
        )

    def list_review_items(self) -> list[ReviewItem]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    review_item_id,
                    review_session_id,
                    feedback_id,
                    item_status,
                    current_decision,
                    decision_reason,
                    reviewed_payload_json,
                    reviewed_by,
                    reviewed_at,
                    requires_followup,
                    learning_eligible
                FROM review_items
                ORDER BY review_item_id ASC
                """
            ).fetchall()

        return [
            ReviewItem(
                review_item_id=row["review_item_id"],
                review_session_id=row["review_session_id"],
                feedback_id=row["feedback_id"],
                item_status=ReviewItemStatus(row["item_status"]),
                current_decision=DecisionType(row["current_decision"]) if row["current_decision"] else None,
                decision_reason=row["decision_reason"],
                reviewed_payload=json.loads(row["reviewed_payload_json"]) if row["reviewed_payload_json"] else None,
                reviewed_by=row["reviewed_by"],
                reviewed_at=_parse_dt(row["reviewed_at"]),
                requires_followup=bool(row["requires_followup"]),
                learning_eligible=bool(row["learning_eligible"]),
            )
            for row in rows
        ]

    def list_review_items_for_session(self, review_session_id: str) -> list[ReviewItem]:
        return [
            item for item in self.list_review_items()
            if item.review_session_id == review_session_id
        ]

    def list_review_items_for_feedback(self, feedback_id: str) -> list[ReviewItem]:
        return [
            item for item in self.list_review_items()
            if item.feedback_id == feedback_id
        ]

    # -------------------------------------------------------------------------
    # Decision events
    # -------------------------------------------------------------------------

    def save_decision_event(self, event: ReviewDecisionEvent) -> ReviewDecisionEvent:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO review_decision_events (
                    decision_event_id,
                    review_item_id,
                    decision_type,
                    actor_id,
                    previous_state,
                    new_state,
                    created_at,
                    decision_reason,
                    decision_payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.decision_event_id,
                    event.review_item_id,
                    event.decision_type.value,
                    event.actor_id,
                    event.previous_state,
                    event.new_state,
                    _dt(event.created_at),
                    event.decision_reason,
                    json.dumps(event.decision_payload, sort_keys=True) if event.decision_payload is not None else None,
                ),
            )
            conn.commit()
        return event

    def get_decision_event(self, decision_event_id: str) -> Optional[ReviewDecisionEvent]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    decision_event_id,
                    review_item_id,
                    decision_type,
                    actor_id,
                    previous_state,
                    new_state,
                    created_at,
                    decision_reason,
                    decision_payload_json
                FROM review_decision_events
                WHERE decision_event_id = ?
                """,
                (decision_event_id,),
            ).fetchone()

        if row is None:
            return None

        return ReviewDecisionEvent(
            decision_event_id=row["decision_event_id"],
            review_item_id=row["review_item_id"],
            decision_type=DecisionType(row["decision_type"]),
            actor_id=row["actor_id"],
            previous_state=row["previous_state"],
            new_state=row["new_state"],
            created_at=_parse_dt(row["created_at"]) or datetime.now(),
            decision_reason=row["decision_reason"],
            decision_payload=json.loads(row["decision_payload_json"]) if row["decision_payload_json"] else None,
        )

    def list_decision_events(self) -> list[ReviewDecisionEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    decision_event_id,
                    review_item_id,
                    decision_type,
                    actor_id,
                    previous_state,
                    new_state,
                    created_at,
                    decision_reason,
                    decision_payload_json
                FROM review_decision_events
                ORDER BY created_at ASC, decision_event_id ASC
                """
            ).fetchall()

        return [
            ReviewDecisionEvent(
                decision_event_id=row["decision_event_id"],
                review_item_id=row["review_item_id"],
                decision_type=DecisionType(row["decision_type"]),
                actor_id=row["actor_id"],
                previous_state=row["previous_state"],
                new_state=row["new_state"],
                created_at=_parse_dt(row["created_at"]) or datetime.now(),
                decision_reason=row["decision_reason"],
                decision_payload=json.loads(row["decision_payload_json"]) if row["decision_payload_json"] else None,
            )
            for row in rows
        ]

    def list_decision_events_for_item(self, review_item_id: str) -> list[ReviewDecisionEvent]:
        return [
            event for event in self.list_decision_events()
            if event.review_item_id == review_item_id
        ]

    # -------------------------------------------------------------------------
    # Audit events
    # -------------------------------------------------------------------------

    def save_audit_event(self, event: AuditEvent) -> AuditEvent:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO review_audit_events (
                    audit_event_id,
                    entity_type,
                    entity_id,
                    action_type,
                    actor_id,
                    occurred_at,
                    context_reference,
                    event_payload_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.audit_event_id,
                    event.entity_type,
                    event.entity_id,
                    event.action_type,
                    event.actor_id,
                    _dt(event.occurred_at),
                    event.context_reference,
                    json.dumps(event.event_payload, sort_keys=True) if event.event_payload is not None else None,
                ),
            )
            conn.commit()
        return event

    def get_audit_event(self, audit_event_id: str) -> Optional[AuditEvent]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    audit_event_id,
                    entity_type,
                    entity_id,
                    action_type,
                    actor_id,
                    occurred_at,
                    context_reference,
                    event_payload_json
                FROM review_audit_events
                WHERE audit_event_id = ?
                """,
                (audit_event_id,),
            ).fetchone()

        if row is None:
            return None

        return AuditEvent(
            audit_event_id=row["audit_event_id"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            action_type=row["action_type"],
            actor_id=row["actor_id"],
            occurred_at=_parse_dt(row["occurred_at"]) or datetime.now(),
            context_reference=row["context_reference"],
            event_payload=json.loads(row["event_payload_json"]) if row["event_payload_json"] else None,
        )

    def list_audit_events(self) -> list[AuditEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    audit_event_id,
                    entity_type,
                    entity_id,
                    action_type,
                    actor_id,
                    occurred_at,
                    context_reference,
                    event_payload_json
                FROM review_audit_events
                ORDER BY occurred_at ASC, audit_event_id ASC
                """
            ).fetchall()

        return [
            AuditEvent(
                audit_event_id=row["audit_event_id"],
                entity_type=row["entity_type"],
                entity_id=row["entity_id"],
                action_type=row["action_type"],
                actor_id=row["actor_id"],
                occurred_at=_parse_dt(row["occurred_at"]) or datetime.now(),
                context_reference=row["context_reference"],
                event_payload=json.loads(row["event_payload_json"]) if row["event_payload_json"] else None,
            )
            for row in rows
        ]

    def list_audit_events_for_entity(self, entity_type: str, entity_id: str) -> list[AuditEvent]:
        return [
            event for event in self.list_audit_events()
            if event.entity_type == entity_type and event.entity_id == entity_id
        ]

    # -------------------------------------------------------------------------
    # Eligibility records
    # -------------------------------------------------------------------------

    def save_eligibility_record(self, record: LearningEligibilityRecord) -> LearningEligibilityRecord:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO review_eligibility_records (
                    eligibility_id,
                    review_item_id,
                    feedback_id,
                    eligibility_status,
                    eligibility_reason,
                    derived_payload_json,
                    created_at,
                    created_by_system,
                    invalidated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.eligibility_id,
                    record.review_item_id,
                    record.feedback_id,
                    record.eligibility_status.value,
                    record.eligibility_reason,
                    json.dumps(record.derived_payload, sort_keys=True) if record.derived_payload is not None else None,
                    _dt(record.created_at),
                    "true" if record.created_by_system else "false",
                    _dt(record.invalidated_at),
                ),
            )
            conn.commit()
        return record

    def get_eligibility_record(self, eligibility_id: str) -> Optional[LearningEligibilityRecord]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT
                    eligibility_id,
                    review_item_id,
                    feedback_id,
                    eligibility_status,
                    eligibility_reason,
                    derived_payload_json,
                    created_at,
                    created_by_system,
                    invalidated_at
                FROM review_eligibility_records
                WHERE eligibility_id = ?
                """,
                (eligibility_id,),
            ).fetchone()

        if row is None:
            return None

        return LearningEligibilityRecord(
            eligibility_id=row["eligibility_id"],
            review_item_id=row["review_item_id"],
            feedback_id=row["feedback_id"],
            eligibility_status=EligibilityStatus(row["eligibility_status"]),
            eligibility_reason=row["eligibility_reason"],
            derived_payload=json.loads(row["derived_payload_json"]) if row["derived_payload_json"] else None,
            created_at=_parse_dt(row["created_at"]) or datetime.now(),
            created_by_system=str(row["created_by_system"]).lower() == "true",
            invalidated_at=_parse_dt(row["invalidated_at"]),
        )

    def list_eligibility_records(self) -> list[LearningEligibilityRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    eligibility_id,
                    review_item_id,
                    feedback_id,
                    eligibility_status,
                    eligibility_reason,
                    derived_payload_json,
                    created_at,
                    created_by_system,
                    invalidated_at
                FROM review_eligibility_records
                ORDER BY created_at ASC, eligibility_id ASC
                """
            ).fetchall()

        return [
            LearningEligibilityRecord(
                eligibility_id=row["eligibility_id"],
                review_item_id=row["review_item_id"],
                feedback_id=row["feedback_id"],
                eligibility_status=EligibilityStatus(row["eligibility_status"]),
                eligibility_reason=row["eligibility_reason"],
                derived_payload=json.loads(row["derived_payload_json"]) if row["derived_payload_json"] else None,
                created_at=_parse_dt(row["created_at"]) or datetime.now(),
                created_by_system=str(row["created_by_system"]).lower() == "true",
                invalidated_at=_parse_dt(row["invalidated_at"]),
            )
            for row in rows
        ]

    def list_eligibility_records_for_item(self, review_item_id: str) -> list[LearningEligibilityRecord]:
        return [
            record for record in self.list_eligibility_records()
            if record.review_item_id == review_item_id
        ]