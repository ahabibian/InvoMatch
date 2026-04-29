from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class TenantStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DISABLED = "disabled"


@dataclass(frozen=True, slots=True)
class Tenant:
    tenant_id: str
    name: str
    status: TenantStatus
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class UserTenantAssociation:
    user_id: str
    tenant_id: str
    is_active: bool = True


@dataclass(frozen=True, slots=True)
class TenantContext:
    tenant_id: str
    user_id: str
    authentication_source: str | None = None
    correlation_id: str | None = None