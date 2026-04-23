from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ProductAuditCategory(str, Enum):
    OPERATIONAL = "operational"
    SECURITY = "security"


class ProductAuditEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sequence_id: int = Field(ge=1)
    event_id: str = Field(min_length=1)
    occurred_at: datetime
    recorded_at: datetime
    event_type: str = Field(min_length=1)
    category: ProductAuditCategory
    run_id: str | None = None
    user_id: str | None = None
    correlation_id: str | None = None
    outcome: str | None = None
    decision: str | None = None
    reason_code: str | None = None
    previous_state: str | None = None
    new_state: str | None = None
    related_failure_code: str | None = None
    attempt_number: int | None = Field(default=None, ge=0)
    capability: str | None = None
    request_path: str | None = None
    request_method: str | None = None
    metadata: dict = Field(default_factory=dict)


class ProductAuditEventListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    events: list[ProductAuditEvent] = Field(default_factory=list)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)