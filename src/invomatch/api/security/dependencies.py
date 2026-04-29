from __future__ import annotations

from fastapi import Request

from invomatch.api.security.errors import forbidden, unauthorized
from invomatch.domain.security import AuthenticatedPrincipal, Permission
from invomatch.domain.tenant import TenantContext


def _record_security_event(
    request: Request,
    *,
    event_type: str,
    principal=None,
    capability: str | None = None,
    outcome: str | None = None,
    reason: str | None = None,
    metadata: dict | None = None,
) -> None:
    audit_service = getattr(request.app.state, "security_audit_service", None)
    if audit_service is None:
        return

    audit_enabled = bool(
        getattr(getattr(request.app.state, "security_settings", None), "security_audit_enabled", True)
    )
    if not audit_enabled:
        return

    audit_service.record(
        event_type=event_type,
        principal=principal,
        request_path=str(getattr(request.url, "path", "")) if getattr(request, "url", None) else None,
        request_method=getattr(request, "method", None),
        capability=capability,
        outcome=outcome,
        reason=reason,
        metadata=metadata or {},
    )


def get_authenticated_principal(request: Request) -> AuthenticatedPrincipal:
    security_settings = getattr(request.app.state, "security_settings", None)
    auth_enabled = bool(getattr(security_settings, "auth_enabled", True))

    if not auth_enabled:
        raise unauthorized("Authentication boundary is disabled unexpectedly")

    authentication_service = getattr(request.app.state, "authentication_service", None)
    if authentication_service is None:
        raise RuntimeError("authentication_service is not configured on application state")

    authorization_header = None
    headers = getattr(request, "headers", None)
    if headers is not None:
        authorization_header = headers.get("Authorization")

    result = authentication_service.authenticate_authorization_header(authorization_header)

    if not result.is_authenticated:
        _record_security_event(
            request,
            event_type="authentication_failure",
            outcome="denied",
            reason=result.failure_reason,
        )
        raise unauthorized("Authentication required")

    principal = result.principal

    if principal is None:
        _record_security_event(
            request,
            event_type="authentication_failure",
            outcome="denied",
            reason="missing_principal",
        )
        raise unauthorized("Authentication required")

    if not principal.is_active:
        _record_security_event(
            request,
            event_type="inactive_user_blocked",
            principal=principal,
            outcome="denied",
            reason="inactive_user",
        )
        raise forbidden("User is inactive")

    _record_security_event(
        request,
        event_type="authentication_success",
        principal=principal,
        outcome="allowed",
    )
    return principal



def get_tenant_context(request: Request) -> TenantContext:
    principal = get_authenticated_principal(request)

    tenant_id = getattr(principal, "tenant_id", None)
    if tenant_id is None:
        tenant_id = getattr(principal, "organization_id", None)

    if tenant_id is None:
        _record_security_event(
            request,
            event_type="tenant_resolution_failure",
            principal=principal,
            outcome="denied",
            reason="missing_tenant_id",
        )
        raise forbidden("Tenant context is required")

    return TenantContext(
        tenant_id=str(tenant_id),
        user_id=str(principal.user_id),
        authentication_source="api_auth",
        correlation_id=None,
    )
def require_permission(
    request: Request,
    *,
    permission: Permission,
) -> AuthenticatedPrincipal:
    principal = get_authenticated_principal(request)

    authorization_service = getattr(request.app.state, "authorization_service", None)
    if authorization_service is None:
        raise RuntimeError("authorization_service is not configured on application state")

    result = authorization_service.authorize(
        principal=principal,
        permission=permission,
    )

    if not result.allowed:
        _record_security_event(
            request,
            event_type="authorization_denied",
            principal=principal,
            capability=permission.value,
            outcome="denied",
            reason=result.denial_reason,
        )
        raise forbidden("Permission denied")

    return principal


def record_privileged_success(
    request: Request,
    *,
    principal: AuthenticatedPrincipal,
    permission: Permission,
    metadata: dict | None = None,
) -> None:
    _record_security_event(
        request,
        event_type="privileged_action_executed",
        principal=principal,
        capability=permission.value,
        outcome="allowed",
        metadata=metadata or {},
    )