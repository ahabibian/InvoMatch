from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from invomatch.domain.audit.models import AuditCategory, AuditEvent, AuditEventQuery
from invomatch.domain.audit.repository import AuditEventRepository
from invomatch.domain.security import AuthenticatedPrincipal


@dataclass(frozen=True)
class SecurityAuditEvent:
    event_type: str
    occurred_at: datetime
    user_id: str | None = None
    username: str | None = None
    role: str | None = None
    request_path: str | None = None
    request_method: str | None = None
    capability: str | None = None
    outcome: str | None = None
    reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class InMemorySecurityAuditService:
    def __init__(self) -> None:
        self._events: list[SecurityAuditEvent] = []

    def record(
        self,
        *,
        event_type: str,
        principal: AuthenticatedPrincipal | None = None,
        request_path: str | None = None,
        request_method: str | None = None,
        capability: str | None = None,
        outcome: str | None = None,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityAuditEvent:
        event = SecurityAuditEvent(
            event_type=event_type,
            occurred_at=datetime.now(UTC),
            user_id=principal.user_id if principal is not None else None,
            username=principal.username if principal is not None else None,
            role=principal.role.value if principal is not None else None,
            request_path=request_path,
            request_method=request_method,
            capability=capability,
            outcome=outcome,
            reason=reason,
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def list_events(self) -> list[SecurityAuditEvent]:
        return list(self._events)


class PersistentSecurityAuditService:
    def __init__(self, repository: AuditEventRepository) -> None:
        self._repository = repository

    def record(
        self,
        *,
        event_type: str,
        principal: AuthenticatedPrincipal | None = None,
        request_path: str | None = None,
        request_method: str | None = None,
        capability: str | None = None,
        outcome: str | None = None,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SecurityAuditEvent:
        occurred_at = datetime.now(UTC)
        payload_metadata = dict(metadata or {})
        if principal is not None:
            payload_metadata.setdefault("username", principal.username)
            payload_metadata.setdefault("role", principal.role.value)
        if reason is not None:
            payload_metadata.setdefault("reason", reason)

        self._repository.create(
            AuditEvent(
                event_id=str(uuid4()),
                sequence_id=None,
                occurred_at=occurred_at,
                recorded_at=occurred_at,
                event_type=event_type,
                category=AuditCategory.SECURITY,
                user_id=principal.user_id if principal is not None else None,
                outcome=outcome,
                reason_code=reason,
                capability=capability,
                request_path=request_path,
                request_method=request_method,
                metadata=payload_metadata,
            )
        )

        return SecurityAuditEvent(
            event_type=event_type,
            occurred_at=occurred_at,
            user_id=principal.user_id if principal is not None else None,
            username=principal.username if principal is not None else None,
            role=principal.role.value if principal is not None else None,
            request_path=request_path,
            request_method=request_method,
            capability=capability,
            outcome=outcome,
            reason=reason,
            metadata=metadata or {},
        )

    def list_events(self) -> list[SecurityAuditEvent]:
        events = self._repository.list_events(
            AuditEventQuery(category=AuditCategory.SECURITY, limit=10000, offset=0)
        )
        return [
            SecurityAuditEvent(
                event_type=event.event_type,
                occurred_at=event.occurred_at,
                user_id=event.user_id,
                username=(event.metadata or {}).get("username"),
                role=(event.metadata or {}).get("role"),
                request_path=event.request_path,
                request_method=event.request_method,
                capability=event.capability,
                outcome=event.outcome,
                reason=event.reason_code,
                metadata=dict(event.metadata or {}),
            )
            for event in events
        ]