from __future__ import annotations

from pathlib import Path

from invomatch.domain.input_boundary.models import (
    InputError,
    InputErrorType,
    InputSession,
    InputType,
)
from invomatch.services.input_boundary.sqlite_repository import SqliteInputSessionRepository


def test_create_and_get_round_trip(tmp_path: Path) -> None:
    repo = SqliteInputSessionRepository(tmp_path / "input_sessions.sqlite3")

    session = InputSession(input_type=InputType.JSON)
    created = repo.create(session)
    fetched = repo.get(created.input_id)

    assert fetched is not None
    assert fetched.input_id == created.input_id
    assert fetched.input_type == InputType.JSON
    assert fetched.status == created.status


def test_save_persists_updates(tmp_path: Path) -> None:
    repo = SqliteInputSessionRepository(tmp_path / "input_sessions.sqlite3")

    session = repo.create(InputSession(input_type=InputType.FILE))
    session.mark_validated()
    session.mark_ingested("batch-123")
    session.mark_run_created("run-123")
    repo.save(session)

    fetched = repo.get_by_input_id(session.input_id)

    assert fetched is not None
    assert fetched.status == session.status
    assert fetched.ingestion_batch_id == "batch-123"
    assert fetched.run_id == "run-123"


def test_errors_are_persisted(tmp_path: Path) -> None:
    repo = SqliteInputSessionRepository(tmp_path / "input_sessions.sqlite3")

    session = repo.create(InputSession(input_type=InputType.JSON))
    session.mark_failed([
        InputError(
            type=InputErrorType.VALIDATION,
            code="invalid_value",
            message="Invalid input",
            field="invoices.0.amount",
        )
    ])
    repo.save(session)

    fetched = repo.get(session.input_id)

    assert fetched is not None
    assert len(fetched.validation_errors) == 1
    assert fetched.validation_errors[0].code == "invalid_value"
    assert fetched.validation_errors[0].field == "invoices.0.amount"


def test_persistence_survives_repository_recreation(tmp_path: Path) -> None:
    db_path = tmp_path / "input_sessions.sqlite3"

    repo1 = SqliteInputSessionRepository(db_path)
    session = repo1.create(InputSession(input_type=InputType.JSON))
    session.mark_validated()
    session.mark_ingested("batch-xyz")
    repo1.save(session)

    repo2 = SqliteInputSessionRepository(db_path)
    fetched = repo2.get(session.input_id)

    assert fetched is not None
    assert fetched.input_id == session.input_id
    assert fetched.status == session.status
    assert fetched.ingestion_batch_id == "batch-xyz"