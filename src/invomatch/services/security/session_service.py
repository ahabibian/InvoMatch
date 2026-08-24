from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import secrets
from threading import RLock

from invomatch.domain.security import AuthenticatedPrincipal


@dataclass(frozen=True)
class BrowserSession:
    session_id: str
    principal: AuthenticatedPrincipal
    expires_at: datetime


class InMemoryBrowserSessionService:
    """Opaque, process-local browser sessions for the single-instance pilot runtime."""

    def __init__(self, *, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than zero")
        self._ttl_seconds = ttl_seconds
        self._sessions: dict[str, BrowserSession] = {}
        self._lock = RLock()

    def create(self, principal: AuthenticatedPrincipal) -> BrowserSession:
        session = BrowserSession(
            session_id=secrets.token_urlsafe(32),
            principal=principal,
            expires_at=datetime.now(UTC) + timedelta(seconds=self._ttl_seconds),
        )
        with self._lock:
            self._sessions[session.session_id] = session
        return session

    def resolve(self, session_id: str | None) -> AuthenticatedPrincipal | None:
        if not session_id:
            return None
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None
            if datetime.now(UTC) >= session.expires_at:
                self._sessions.pop(session_id, None)
                return None
            return session.principal

    def revoke(self, session_id: str | None) -> None:
        if not session_id:
            return
        with self._lock:
            self._sessions.pop(session_id, None)

