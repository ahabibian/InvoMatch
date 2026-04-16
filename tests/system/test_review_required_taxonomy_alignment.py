from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path

import pytest

from invomatch.services.input_boundary.file_input_service import FileInputService
from invomatch.services.input_boundary.input_processing_service import InputProcessingService
from invomatch.services.input_boundary.json_input_service import JsonInputService
from invomatch.services.input_boundary.sqlite_repository import SqliteInputSessionRepository
from invomatch.services.ingestion_run_integration.runtime_adapter import IngestionRunRuntimeAdapter
from invomatch.services.orchestration.run_orchestration_service import RunOrchestrationService
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import SqliteRunStore


@dataclass
class ScenarioContext:
    run_store: SqliteRunStore
    review_store: InMemoryReviewStore
    orchestration_service: RunOrchestrationService
    input_processing_service: InputProcessingService
    tmp_path: Path


@pytest.fixture
def scenario_context(tmp_path: Path) -> ScenarioContext:
    run_store = SqliteRunStore(tmp_path / "runs.sqlite3")
    review_store = InMemoryReviewStore()
    review_service = ReviewService()

    reconcile_and_save_bound = partial(
        reconcile_and_save,
        run_store=run_store,
    )

    runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=reconcile_and_save_bound,
        batch_root=tmp_path / "ingestion_batches",
    )

    def _run_from_ingestion_adapter(ingestion_batch_id: str, payload: dict):
        return runtime_adapter.create_run_from_ingestion(
            ingestion_batch_id=ingestion_batch_id,
            ingestion_succeeded=True,
            accepted_invoices=payload["invoices"],
            accepted_payments=payload["payments"],
            rejected_count=0,
            conflict_count=0,
            blocking_conflict=False,
        )

    input_processing_service = InputProcessingService(
        repository=SqliteInputSessionRepository(tmp_path / "input_sessions.sqlite3"),
        json_service=JsonInputService(),
        file_service=FileInputService(),
        run_from_ingestion_service=_run_from_ingestion_adapter,
    )

    orchestration_service = RunOrchestrationService(
        review_store=review_store,
        review_service=review_service,
    )

    return ScenarioContext(
        run_store=run_store,
        review_store=review_store,
        orchestration_service=orchestration_service,
        input_processing_service=input_processing_service,
        tmp_path=tmp_path,
    )


def _payload_with_two_same_amount_payments_but_no_invoice_binding() -> dict:
    return {
        "invoices": [
            {
                "id": "inv-dup-001",
                "date": "2026-04-16",
                "amount": "100.00",
                "currency": "USD",
                "reference": "INV-DUP-001",
            }
        ],
        "payments": [
            {
                "id": "pay-dup-001",
                "date": "2026-04-16",
                "amount": "100.00",
                "currency": "USD",
                "reference": "INV-DUP-001",
            },
            {
                "id": "pay-dup-002",
                "date": "2026-04-17",
                "amount": "100.00",
                "currency": "USD",
                "reference": "INV-DUP-001",
            },
        ],
    }


def test_json_input_boundary_does_not_materialize_duplicate_review_required_taxonomy(
    scenario_context: ScenarioContext,
) -> None:
    session = scenario_context.input_processing_service.process_json(
        _payload_with_two_same_amount_payments_but_no_invoice_binding()
    )

    assert session.status == "run_created"
    assert session.run_id is not None

    run = scenario_context.run_store.get_run(session.run_id)
    assert run is not None
    assert str(run.status) == "completed"

    assert run.report is not None
    assert len(run.report.results) == 1

    result = run.report.results[0]
    assert result.invoice_id == "inv-dup-001"
    assert result.match_result.status == "unmatched"

    reconciliation_outcomes = [
        {
            "invoice_id": result.invoice_id,
            "status": result.match_result.status,
            "reason": "derived_from_runtime_report",
        }
    ]

    orchestration_result = scenario_context.orchestration_service.orchestrate_post_matching(
        run_id=run.run_id,
        reconciliation_outcomes=reconciliation_outcomes,
    )

    assert orchestration_result.run_status == "review_required"
    assert len(orchestration_result.review_cases) == 1
    assert orchestration_result.review_cases[0]["invoice_id"] == "inv-dup-001"