from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime

from invomatch.domain.audit.models import AuditCategory, AuditEvent, AuditEventQuery
from invomatch.domain.audit.repository import AuditEventRepository


class SqliteAuditEventRepository(AuditEventRepository):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._initialize()

    def create(self, event: AuditEvent) -> AuditEvent:
        with self._connect() as conn:
            cursor = conn.execute(
                '''
                INSERT INTO audit_events (
                    event_id,
                    tenant_id,
                    occurred_at,
                    recorded_at,
                    event_type,
                    category,
                    run_id,
                    user_id,
                    correlation_id,
                    outcome,
                    decision,
                    reason_code,
                    previous_state,
                    new_state,
                    related_failure_code,
                    attempt_number,
                    capability,
                    request_path,
                    request_method,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    event.event_id,
                    event.tenant_id,
                    self._serialize_datetime(event.occurred_at),
                    self._serialize_datetime(event.recorded_at),
                    event.event_type,
                    event.category.value,
                    event.run_id,
                    event.user_id,
                    event.correlation_id,
                    event.outcome,
                    event.decision,
                    event.reason_code,
                    event.previous_state,
                    event.new_state,
                    event.related_failure_code,
                    event.attempt_number,
                    event.capability,
                    event.request_path,
                    event.request_method,
                    json.dumps(event.metadata, sort_keys=True),
                ),
            )
            conn.commit()
            sequence_id = int(cursor.lastrowid)

        return AuditEvent(
            event_id=event.event_id,
            sequence_id=sequence_id,
            tenant_id=event.tenant_id,
            occurred_at=event.occurred_at,
            recorded_at=event.recorded_at,
            event_type=event.event_type,
            category=event.category,
            run_id=event.run_id,
            user_id=event.user_id,
            correlation_id=event.correlation_id,
            outcome=event.outcome,
            decision=event.decision,
            reason_code=event.reason_code,
            previous_state=event.previous_state,
            new_state=event.new_state,
            related_failure_code=event.related_failure_code,
            attempt_number=event.attempt_number,
            capability=event.capability,
            request_path=event.request_path,
            request_method=event.request_method,
            metadata=event.metadata,
        )

    def list_events(self, query: AuditEventQuery) -> list[AuditEvent]:
        where_clauses: list[str] = []
        params: list[object] = []

        where_clauses.append("tenant_id = ?")
        params.append(query.tenant_id)

        if query.run_id is not None:
            where_clauses.append("run_id = ?")
            params.append(query.run_id)

        if query.user_id is not None:
            where_clauses.append("user_id = ?")
            params.append(query.user_id)

        if query.event_type is not None:
            where_clauses.append("event_type = ?")
            params.append(query.event_type)

        if query.category is not None:
            where_clauses.append("category = ?")
            params.append(query.category.value)

        if query.occurred_from is not None:
            where_clauses.append("occurred_at >= ?")
            params.append(self._serialize_datetime(query.occurred_from))

        if query.occurred_to is not None:
            where_clauses.append("occurred_at <= ?")
            params.append(self._serialize_datetime(query.occurred_to))

        sql = '''
        SELECT
            sequence_id,
            event_id,
            tenant_id,
            occurred_at,
            recorded_at,
            event_type,
            category,
            run_id,
            user_id,
            correlation_id,
            outcome,
            decision,
            reason_code,
            previous_state,
            new_state,
            related_failure_code,
            attempt_number,
            capability,
            request_path,
            request_method,
            metadata_json
        FROM audit_events
        '''

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY sequence_id ASC LIMIT ? OFFSET ?"
        params.append(query.limit)
        params.append(query.offset)

        with self._connect() as conn:
            rows = conn.execute(sql, tuple(params)).fetchall()

        return [self._row_to_event(row) for row in rows]

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS audit_events (
                    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    tenant_id TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    run_id TEXT NULL,
                    user_id TEXT NULL,
                    correlation_id TEXT NULL,
                    outcome TEXT NULL,
                    decision TEXT NULL,
                    reason_code TEXT NULL,
                    previous_state TEXT NULL,
                    new_state TEXT NULL,
                    related_failure_code TEXT NULL,
                    attempt_number INTEGER NULL,
                    capability TEXT NULL,
                    request_path TEXT NULL,
                    request_method TEXT NULL,
                    metadata_json TEXT NOT NULL
                )
                '''
            )
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(audit_events)").fetchall()
            }
            if "tenant_id" not in columns:
                conn.execute(
                    "ALTER TABLE audit_events ADD COLUMN tenant_id TEXT NOT NULL DEFAULT 'legacy-tenant'"
                )

            conn.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_run_sequence
                ON audit_events (tenant_id, run_id, sequence_id)
                '''
            )
            conn.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_user_sequence
                ON audit_events (tenant_id, user_id, sequence_id)
                '''
            )
            conn.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_type_sequence
                ON audit_events (tenant_id, event_type, sequence_id)
                '''
            )
            conn.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_audit_events_tenant_occurred_at
                ON audit_events (tenant_id, occurred_at)
                '''
            )
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> AuditEvent:
        return AuditEvent(
            event_id=row["event_id"],
            sequence_id=row["sequence_id"],
            tenant_id=row["tenant_id"],
            occurred_at=SqliteAuditEventRepository._deserialize_datetime(row["occurred_at"]),
            recorded_at=SqliteAuditEventRepository._deserialize_datetime(row["recorded_at"]),
            event_type=row["event_type"],
            category=AuditCategory(row["category"]),
            run_id=row["run_id"],
            user_id=row["user_id"],
            correlation_id=row["correlation_id"],
            outcome=row["outcome"],
            decision=row["decision"],
            reason_code=row["reason_code"],
            previous_state=row["previous_state"],
            new_state=row["new_state"],
            related_failure_code=row["related_failure_code"],
            attempt_number=row["attempt_number"],
            capability=row["capability"],
            request_path=row["request_path"],
            request_method=row["request_method"],
            metadata=json.loads(row["metadata_json"]),
        )

    @staticmethod
    def _serialize_datetime(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        else:
            value = value.astimezone(UTC)
        return value.isoformat()

    @staticmethod
    def _deserialize_datetime(value: str) -> datetime:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)