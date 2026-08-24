from __future__ import annotations

from fastapi import APIRouter, Request, Response

from invomatch.api.product_models.auth_session import (
    ProductAuthSessionResponse,
    ProductAuthSessionUser,
    ProductAuthLoginRequest,
    ProductAuthLoginResponse,
)
from invomatch.api.security import get_authenticated_principal
from invomatch.api.security.errors import forbidden, unauthorized
from invomatch.domain.security import Permission
from invomatch.services.security import get_permissions_for_role


router = APIRouter(prefix="/api/auth", tags=["auth"])
SESSION_COOKIE_NAME = "invomatch_session"


@router.post("/login", response_model=ProductAuthLoginResponse)
def login(
    payload: ProductAuthLoginRequest,
    request: Request,
    response: Response,
) -> ProductAuthLoginResponse:
    authentication_service = request.app.state.authentication_service
    result = authentication_service.authenticate_token(payload.credential.get_secret_value())
    if not result.is_authenticated or result.principal is None:
        raise unauthorized("Invalid or expired pilot credential")
    if not result.principal.is_active:
        raise forbidden("User is inactive")

    session = request.app.state.browser_session_service.create(result.principal)
    settings = request.app.state.security_settings
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session.session_id,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="strict",
        path="/",
    )
    return ProductAuthLoginResponse(authenticated=True)


@router.post("/logout", response_model=ProductAuthLoginResponse)
def logout(request: Request, response: Response) -> ProductAuthLoginResponse:
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    request.app.state.browser_session_service.revoke(session_id)
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        secure=request.app.state.security_settings.session_cookie_secure,
        samesite="strict",
        path="/",
    )
    return ProductAuthLoginResponse(authenticated=False)


@router.get("/session", response_model=ProductAuthSessionResponse)
def get_current_auth_session(request: Request) -> ProductAuthSessionResponse:
    principal = get_authenticated_principal(request)
    permissions = get_permissions_for_role(principal.role)
    ordered_permission_values = [
        permission.value
        for permission in Permission
        if permission in permissions
    ]

    return ProductAuthSessionResponse(
        user=ProductAuthSessionUser(
            user_id=principal.user_id,
            username=principal.username,
            role=principal.role.value,
            status=principal.status.value,
            tenant_id=principal.tenant_id,
            auth_source=principal.auth_source,
        ),
        permissions=ordered_permission_values,
    )
