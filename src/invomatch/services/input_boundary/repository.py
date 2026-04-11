from __future__ import annotations

from dataclasses import replace
from typing import Protocol

from invomatch.domain.input_boundary.models import InputSession


class InputSessionRepository(Protocol):
    def create(self, session: InputSession) -> InputSession: ...

    def save(self, session: InputSession) -> InputSession: ...

    def get(self, input_id: str) -> InputSession | None: ...

    def get_by_input_id(self, input_id: str) -> InputSession | None: ...


class InMemoryInputSessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, InputSession] = {}

    def create(self, session: InputSession) -> InputSession:
        stored = replace(session)
        self._sessions[stored.input_id] = stored
        return replace(stored)

    def save(self, session: InputSession) -> InputSession:
        stored = replace(session)
        self._sessions[stored.input_id] = stored
        return replace(stored)

    def get(self, input_id: str) -> InputSession | None:
        session = self._sessions.get(input_id)
        if session is None:
            return None
        return replace(session)

    def get_by_input_id(self, input_id: str) -> InputSession | None:
        return self.get(input_id)