from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Request

from invomatch.api.product_models.audit_event import (
    ProductAuditCategory,
    ProductAuditEvent,
    ProductAuditEventListResponse,
)
from invomatch.api.security import get_tenant_context, require_permission
from invomatch.domain.audit.models import AuditCategory, AuditEventQuery
from invomatch.domain.security import Permission
from invomatch.services.audit import AuditQueryService

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/events", response_model=ProductAuditEventListResponse)
def list_audit_events(
    request: Request,
    run_id: str | None = None,
    user_id: str | None = None,
    event_type: str | None = None,
    category: ProductAuditCategory | None = None,
    occurred_from: datetime | None = None,
    occurred_to: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> ProductAuditEventListResponse:
    require_permission(request, permission=Permission.OPERATIONS_VIEW_METRICS)
    tenant_context = get_tenant_context(request)

    query_service: AuditQueryService = request.app.state.audit_query_service

    query = AuditEventQuery(
        tenant_id=tenant_context.tenant_id,
        run_id=run_id,
        user_id=user_id,
        event_type=event_type,
        category=AuditCategory(category.value) if category is not None else None,
        occurred_from=occurred_from,
        occurred_to=occurred_to,
        limit=limit,
        offset=offset,
    )
    events = query_service.list_events(query)

    return ProductAuditEventListResponse(
        events=[
            ProductAuditEvent(
                sequence_id=event.sequence_id or 0,
                event_id=event.event_id,
                occurred_at=event.occurred_at,
                recorded_at=event.recorded_at,
                event_type=event.event_type,
                category=ProductAuditCategory(event.category.value),
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
                metadata=dict(event.metadata or {}),
            )
            for event in events
        ],
        limit=limit,
        offset=offset,
    )