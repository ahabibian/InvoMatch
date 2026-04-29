from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class AuditCategory(StrEnum):
    OPERATIONAL = "operational"
    SECURITY = "security"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: str
    sequence_id: int | None
    occurred_at: datetime
    recorded_at: datetime
    event_type: str
    category: AuditCategory
    tenant_id: str
    run_id: str | None = None
    user_id: str | None = None
    correlation_id: str | None = None
    outcome: str | None = None
    decision: str | None = None
    reason_code: str | None = None
    previous_state: str | None = None
    new_state: str | None = None
    related_failure_code: str | None = None
    attempt_number: int | None = None
    capability: str | None = None
    request_path: str | None = None
    request_method: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AuditEventQuery:
    tenant_id: str
    run_id: str | None = None
    user_id: str | None = None
    event_type: str | None = None
    category: AuditCategory | None = None
    occurred_from: datetime | None = None
    occurred_to: datetime | None = None
    limit: int = 100
    offset: int = 0