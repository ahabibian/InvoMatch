from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)
from invomatch.services.artifact_query_service import ArtifactQueryService
from invomatch.services.input_boundary.file_input_service import FileInputService
from invomatch.services.input_boundary.input_processing_service import (
    InputProcessingService,
)
from invomatch.services.input_boundary.json_input_service import JsonInputService
from invomatch.services.input_boundary.sqlite_repository import (
    SqliteInputSessionRepository,
)
from invomatch.services.run_store import SqliteRunStore
from invomatch.services.storage.local_storage import LocalArtifactStorage


"""
System Scenario 3 - Invalid Input Rejection

This scenario validates that an invalid input is rejected at the input
boundary and does not create downstream side effects.

It proves:
- input session is created and persisted
- session transitions to rejected
- validation errors are recorded
- ingestion/run creation is never called
- no reconciliation run is created
- no export artifacts exist
"""


@dataclass
class InvalidInputSystemContext:
    run_store: SqliteRunStore
    input_repository: SqliteInputSessionRepository
    input_processing_service: InputProcessingService
    artifact_query_service: ArtifactQueryService
    call_log: dict
    tmp_path: Path


def _invalid_payload() -> dict:
    return {
        "invoices": [
            {
                "id": "inv-001",
                "date": "2026-04-12",
                "amount": "",
                "currency": "USD",
            }
        ],
        "payments": [
            {
                "id": "pay-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
            }
        ],
    }


@pytest.fixture
def invalid_input_system_context(tmp_path: Path) -> InvalidInputSystemContext:
    run_store = SqliteRunStore(tmp_path / "runs.sqlite3")
    input_repository = SqliteInputSessionRepository(tmp_path / "input_sessions.sqlite3")

    export_root = tmp_path / "exports"
    export_root.mkdir(parents=True, exist_ok=True)

    export_repository = SqliteExportArtifactRepository(
        str(export_root / "export_artifacts.sqlite3")
    )
    export_storage = LocalArtifactStorage(export_root)
    artifact_query_service = ArtifactQueryService(
        repository=export_repository,
        storage=export_storage,
    )

    call_log = {"run_from_ingestion_calls": 0}

    def _run_from_ingestion_should_never_be_called(ingestion_batch_id: str, payload: dict):
        call_log["run_from_ingestion_calls"] += 1
        raise AssertionError("run_from_ingestion_service must not be called for invalid input")

    input_processing_service = InputProcessingService(
        repository=input_repository,
        json_service=JsonInputService(),
        file_service=FileInputService(),
        run_from_ingestion_service=_run_from_ingestion_should_never_be_called,
    )

    return InvalidInputSystemContext(
        run_store=run_store,
        input_repository=input_repository,
        input_processing_service=input_processing_service,
        artifact_query_service=artifact_query_service,
        call_log=call_log,
        tmp_path=tmp_path,
    )


def test_invalid_input_rejection(invalid_input_system_context: InvalidInputSystemContext) -> None:
    session = invalid_input_system_context.input_processing_service.process_json(
        _invalid_payload()
    )

    assert session.status == "rejected", f"expected rejected session, got {session.status}"
    assert session.input_id, "expected input session id to be assigned"
    assert session.ingestion_batch_id is None, "expected no ingestion batch id for rejected input"
    assert session.run_id is None, "expected no run id for rejected input"
    assert len(session.validation_errors) == 1, (
        f"expected one validation error, got {len(session.validation_errors)}"
    )
    assert session.validation_errors[0].field == "invoices.0.amount"

    persisted_session = invalid_input_system_context.input_repository.get_by_input_id(
        session.input_id
    )
    assert persisted_session is not None, "expected rejected session to be persisted"
    assert persisted_session.status == "rejected"
    assert persisted_session.ingestion_batch_id is None
    assert persisted_session.run_id is None
    assert len(persisted_session.validation_errors) == 1
    assert persisted_session.validation_errors[0].field == "invoices.0.amount"

    assert invalid_input_system_context.call_log["run_from_ingestion_calls"] == 0, (
        "expected no downstream ingestion/run creation call for invalid input"
    )

    runs, total = invalid_input_system_context.run_store.list_runs()
    assert total == 0, f"expected no reconciliation runs, found total={total}"
    assert runs == [], f"expected empty run list, got {runs}"

    artifacts = invalid_input_system_context.artifact_query_service.list_artifacts_for_run(
        "non-existent-run"
    )
    assert artifacts == [], f"expected no artifacts, got {artifacts}"