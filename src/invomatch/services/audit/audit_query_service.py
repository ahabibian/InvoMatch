from __future__ import annotations

from invomatch.domain.audit.models import AuditEvent, AuditEventQuery
from invomatch.domain.audit.repository import AuditEventRepository


class AuditQueryService:
    def __init__(self, repository: AuditEventRepository) -> None:
        self._repository = repository

    def list_events(self, query: AuditEventQuery) -> list[AuditEvent]:
        return self._repository.list_events(query)