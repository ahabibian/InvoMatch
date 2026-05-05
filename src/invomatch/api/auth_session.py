from __future__ import annotations

from fastapi import APIRouter, Request

from invomatch.api.product_models.auth_session import (
    ProductAuthSessionResponse,
    ProductAuthSessionUser,
)
from invomatch.api.security import get_authenticated_principal
from invomatch.domain.security import Permission
from invomatch.services.security import get_permissions_for_role


router = APIRouter(prefix="/api/auth", tags=["auth"])


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