from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

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