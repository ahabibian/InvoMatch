from __future__ import annotations

from dataclasses import dataclass

from invomatch.domain.security import AuthenticatedPrincipal
from invomatch.services.security.token_provider import StaticTokenProvider


@dataclass(frozen=True)
class AuthenticationResult:
    principal: AuthenticatedPrincipal | None
    failure_reason: str | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.principal is not None


class AuthenticationService:
    def __init__(self, token_provider: StaticTokenProvider) -> None:
        self._token_provider = token_provider

    def authenticate_authorization_header(self, authorization_header: str | None) -> AuthenticationResult:
        if authorization_header is None or not authorization_header.strip():
            return AuthenticationResult(
                principal=None,
                failure_reason="missing_authorization_header",
            )

        parts = authorization_header.strip().split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return AuthenticationResult(
                principal=None,
                failure_reason="malformed_authorization_header",
            )

        token = parts[1].strip()
        if not token:
            return AuthenticationResult(
                principal=None,
                failure_reason="empty_bearer_token",
            )

        principal = self._token_provider.get_principal_for_token(token)
        if principal is None:
            return AuthenticationResult(
                principal=None,
                failure_reason="unknown_token",
            )

        return AuthenticationResult(principal=principal)