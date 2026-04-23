from __future__ import annotations

from dataclasses import dataclass

from invomatch.domain.security import AuthenticatedPrincipal, Permission
from invomatch.services.security.permission_matrix import role_has_permission


@dataclass(frozen=True)
class AuthorizationResult:
    allowed: bool
    denial_reason: str | None = None


class AuthorizationService:
    def authorize(
        self,
        *,
        principal: AuthenticatedPrincipal,
        permission: Permission,
    ) -> AuthorizationResult:
        if not principal.is_active:
            return AuthorizationResult(
                allowed=False,
                denial_reason="inactive_user",
            )

        if not role_has_permission(principal.role, permission):
            return AuthorizationResult(
                allowed=False,
                denial_reason="missing_permission",
            )

        return AuthorizationResult(allowed=True)