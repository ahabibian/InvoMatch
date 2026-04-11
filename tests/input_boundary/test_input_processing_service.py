from __future__ import annotations

from dataclasses import dataclass

from invomatch.services.input_boundary.input_processing_service import InputProcessingService
from invomatch.services.input_boundary.json_input_service import JsonInputService
from invomatch.services.input_boundary.repository import InMemoryInputSessionRepository


@dataclass
class DummyRunResult:
    run_id: str | None
    reason_code: str
    status: str


def _valid_payload() -> dict:
    return {
        "invoices": [
            {
                "id": "inv-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
                "reference": "ref-001",
            }
        ],
        "payments": [
            {
                "id": "pay-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
                "reference": "ref-001",
            }
        ],
    }


def test_process_json_marks_rejected_for_invalid_payload() -> None:
    repo = InMemoryInputSessionRepository()
    service = InputProcessingService(
        repository=repo,
        json_service=JsonInputService(),
        run_from_ingestion_service=lambda ingestion_batch_id, payload: None,
    )

    session = service.process_json({
        "invoices": [{"id": "inv-001", "date": "2026-04-12", "amount": "", "currency": "USD"}],
        "payments": [{"id": "pay-001", "date": "2026-04-12", "amount": "100.00", "currency": "USD"}],
    })

    assert session.status == "rejected"
    assert session.ingestion_batch_id is None
    assert session.run_id is None
    assert session.validation_errors


def test_process_json_marks_run_created_for_success() -> None:
    repo = InMemoryInputSessionRepository()

    def _run_from_ingestion(ingestion_batch_id: str, payload: dict) -> DummyRunResult:
        assert ingestion_batch_id
        assert payload["invoices"]
        assert payload["payments"]
        return DummyRunResult(
            run_id="run-123",
            reason_code="run_created",
            status="run_created",
        )

    service = InputProcessingService(
        repository=repo,
        json_service=JsonInputService(),
        run_from_ingestion_service=_run_from_ingestion,
    )

    session = service.process_json(_valid_payload())

    assert session.status == "run_created"
    assert session.ingestion_batch_id == session.input_id
    assert session.run_id == "run-123"


def test_process_json_marks_failed_when_run_not_created() -> None:
    repo = InMemoryInputSessionRepository()

    service = InputProcessingService(
        repository=repo,
        json_service=JsonInputService(),
        run_from_ingestion_service=lambda ingestion_batch_id, payload: DummyRunResult(
            run_id=None,
            reason_code="no_accepted_invoices",
            status="run_rejected",
        ),
    )

    session = service.process_json(_valid_payload())

    assert session.status == "failed"
    assert session.ingestion_batch_id == session.input_id
    assert session.run_id is None
    assert session.validation_errors[0].code == "no_accepted_invoices"


def test_process_json_marks_failed_when_runtime_raises() -> None:
    repo = InMemoryInputSessionRepository()

    def _explode(ingestion_batch_id: str, payload: dict):
        raise RuntimeError("boom")

    service = InputProcessingService(
        repository=repo,
        json_service=JsonInputService(),
        run_from_ingestion_service=_explode,
    )

    session = service.process_json(_valid_payload())

    assert session.status == "failed"
    assert session.validation_errors[0].code == "processing_failed"