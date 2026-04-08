from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from invomatch.domain.operational.models import (
    OperationalActorType,
    OperationalAuditEvent,
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
)


class OperationalAuditRepository(Protocol):
    def add(self, event: OperationalAuditEvent) -> None:
        ...

    def list_events(self) -> list[OperationalAuditEvent]:
        ...


class InMemoryOperationalAuditRepository:
    def __init__(self) -> None:
        self._events: list[OperationalAuditEvent] = []

    def add(self, event: OperationalAuditEvent) -> None:
        self._events.append(event)

    def list_events(self) -> list[OperationalAuditEvent]:
        return list(self._events)


@dataclass(frozen=True, slots=True)
class OperationalAuditWrite:
    run_id: str
    event_type: str
    decision: OperationalDecision
    reason_code: OperationalReasonCode
    previous_operational_state: OperationalCondition | None = None
    new_operational_state: OperationalCondition | None = None
    related_failure_code: str | None = None
    attempt_number: int | None = None
    correlation_id: str | None = None
    reason_detail: str | None = None
    metadata: dict[str, str] | None = None


class OperationalAuditService:
    def __init__(self, repository: OperationalAuditRepository) -> None:
        self._repository = repository

    def record(self, data: OperationalAuditWrite) -> OperationalAuditEvent:
        event = OperationalAuditEvent(
            event_id=str(uuid4()),
            run_id=data.run_id,
            event_type=data.event_type,
            event_time=datetime.now(timezone.utc),
            actor_type=OperationalActorType.SYSTEM,
            decision=data.decision,
            reason_code=data.reason_code,
            reason_detail=data.reason_detail,
            previous_operational_state=data.previous_operational_state,
            new_operational_state=data.new_operational_state,
            related_failure_code=data.related_failure_code,
            attempt_number=data.attempt_number,
            correlation_id=data.correlation_id,
            metadata=data.metadata or {},
        )
        self._repository.add(event)
        return event