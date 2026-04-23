from __future__ import annotations

from typing import Protocol

from invomatch.domain.audit.models import AuditEvent, AuditEventQuery


class AuditEventRepository(Protocol):
    def create(self, event: AuditEvent) -> AuditEvent:
        ...

    def list_events(self, query: AuditEventQuery) -> list[AuditEvent]:
        ...