from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from invomatch.domain.audit.models import AuditCategory, AuditEvent, AuditEventQuery
from invomatch.domain.audit.repository import AuditEventRepository
from invomatch.domain.operational.models import (
    OperationalActorType,
    OperationalAuditEvent,
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
)


OPERATIONAL_BOUNDARY_TENANT_ID = "operational-boundary"


class OperationalAuditRepository(Protocol):
    def add(self, event: OperationalAuditEvent) -> None:
        ...

    def list_events(self, *, tenant_id: str = OPERATIONAL_BOUNDARY_TENANT_ID) -> list[OperationalAuditEvent]:
        ...


class InMemoryOperationalAuditRepository:
    def __init__(self) -> None:
        self._events: list[OperationalAuditEvent] = []

    def add(self, event: OperationalAuditEvent) -> None:
        self._events.append(event)

    def list_events(self, *, tenant_id: str = OPERATIONAL_BOUNDARY_TENANT_ID) -> list[OperationalAuditEvent]:
        return [event for event in self._events if event.tenant_id == tenant_id]


class PersistentOperationalAuditRepository:
    def __init__(self, repository: AuditEventRepository) -> None:
        self._repository = repository

    def add(self, event: OperationalAuditEvent) -> None:
        payload_metadata = dict(event.metadata or {})
        if event.reason_detail is not None:
            payload_metadata.setdefault("reason_detail", event.reason_detail)

        self._repository.create(
            AuditEvent(
                event_id=event.event_id,
                sequence_id=None,
                tenant_id=event.tenant_id,
                occurred_at=event.event_time,
                recorded_at=event.event_time,
                event_type=event.event_type,
                category=AuditCategory.OPERATIONAL,
                run_id=event.run_id,
                correlation_id=event.correlation_id,
                outcome=event.decision.value,
                decision=event.decision.value,
                reason_code=event.reason_code.value,
                previous_state=event.previous_operational_state.value if event.previous_operational_state is not None else None,
                new_state=event.new_operational_state.value if event.new_operational_state is not None else None,
                related_failure_code=event.related_failure_code,
                attempt_number=event.attempt_number,
                metadata=payload_metadata,
            )
        )

    def list_events(self, *, tenant_id: str = OPERATIONAL_BOUNDARY_TENANT_ID) -> list[OperationalAuditEvent]:
        events = self._repository.list_events(
            AuditEventQuery(
                tenant_id=tenant_id,
                category=AuditCategory.OPERATIONAL,
                limit=10000,
                offset=0,
            )
        )
        return [
            OperationalAuditEvent(
                event_id=event.event_id,
                tenant_id=event.tenant_id,
                run_id=event.run_id or "",
                event_type=event.event_type,
                event_time=event.occurred_at,
                actor_type=OperationalActorType.SYSTEM,
                decision=OperationalDecision(event.decision or event.outcome or OperationalDecision.ALREADY_RECOVERED_NOOP.value),
                reason_code=OperationalReasonCode(event.reason_code or OperationalReasonCode.NONE.value),
                reason_detail=(event.metadata or {}).get("reason_detail"),
                previous_operational_state=OperationalCondition(event.previous_state) if event.previous_state is not None else None,
                new_operational_state=OperationalCondition(event.new_state) if event.new_state is not None else None,
                related_failure_code=event.related_failure_code,
                attempt_number=event.attempt_number,
                correlation_id=event.correlation_id,
                metadata={str(k): str(v) for k, v in (event.metadata or {}).items()},
            )
            for event in events
        ]


@dataclass(frozen=True, slots=True)
class OperationalAuditWrite:
    tenant_id: str
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
            tenant_id=data.tenant_id,
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