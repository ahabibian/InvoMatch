from __future__ import annotations

from invomatch.domain.input_boundary.models import InputSession, InputType
from invomatch.services.input_boundary.repository import InMemoryInputSessionRepository


def test_create_and_get_returns_copy() -> None:
    repo = InMemoryInputSessionRepository()

    session = InputSession(input_type=InputType.JSON)
    created = repo.create(session)
    fetched = repo.get(created.input_id)

    assert fetched is not None
    assert fetched.input_id == created.input_id
    assert fetched is not created


def test_save_persists_updated_session() -> None:
    repo = InMemoryInputSessionRepository()

    session = repo.create(InputSession(input_type=InputType.JSON))
    session.mark_validated()
    repo.save(session)

    fetched = repo.get_by_input_id(session.input_id)

    assert fetched is not None
    assert fetched.status == session.status


def test_get_missing_returns_none() -> None:
    repo = InMemoryInputSessionRepository()

    assert repo.get("missing") is None
    assert repo.get_by_input_id("missing") is None