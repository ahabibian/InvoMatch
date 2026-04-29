from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from pathlib import Path

import pytest

from invomatch.domain.export import ExportFormat
from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)
from invomatch.services.artifact_query_service import ArtifactQueryService
from invomatch.services.export import ExportService
from invomatch.services.export.finalized_projection_store import SqliteFinalizedProjectionStore
from invomatch.services.export_delivery_service import ExportDeliveryService
from invomatch.services.ingestion_run_integration.runtime_adapter import (
    IngestionRunRuntimeAdapter,
)
from invomatch.services.input_boundary.file_input_service import FileInputService
from invomatch.services.input_boundary.input_processing_service import (
    InputProcessingService,
)
from invomatch.services.input_boundary.json_input_service import JsonInputService
from invomatch.services.input_boundary.sqlite_repository import (
    SqliteInputSessionRepository,
)
from invomatch.services.orchestration.export_readiness_evaluator import (
    ExportReadinessEvaluator,
)
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import SqliteRunStore
from invomatch.services.run_view_query_service import RunViewQueryService
from invomatch.services.storage.local_storage import LocalArtifactStorage


"""
System Scenario 1 ÃƒÆ’Ã†â€™Ãƒâ€ Ã¢â‚¬â„¢ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬Ãƒâ€¦Ã‚Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â¢ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡Ãƒâ€šÃ‚Â¬ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â Happy Path Full Flow

Valid input enters the system, passes ingestion and run creation,
completes reconciliation without requiring review, reaches export-ready
state, produces an export artifact, and exposes a consistent final
product run view.

This test validates product-level wiring across:
- input boundary
- ingestion -> run integration
- reconciliation execution
- export readiness
- export delivery
- artifact query
- unified run view
"""


@dataclass
class SystemContext:
    run_store: SqliteRunStore
    review_store: InMemoryReviewStore
    input_processing_service: InputProcessingService
    export_delivery_service: ExportDeliveryService
    artifact_query_service: ArtifactQueryService
    export_readiness_evaluator: ExportReadinessEvaluator
    projection_store: SqliteFinalizedProjectionStore
    run_view_query_service: RunViewQueryService
    tmp_path: Path


def build_valid_happy_path_payload() -> dict:
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


@pytest.fixture
def system_context(tmp_path: Path) -> SystemContext:
    run_store_path = tmp_path / "runs.sqlite3"
    input_sessions_path = tmp_path / "input_sessions.sqlite3"
    ingestion_batch_root = tmp_path / "ingestion_batches"
    export_root = tmp_path / "exports"
    export_root.mkdir(parents=True, exist_ok=True)
    export_db_path = export_root / "export_artifacts.sqlite3"

    run_store = SqliteRunStore(run_store_path)
    review_store = InMemoryReviewStore()
    projection_store = SqliteFinalizedProjectionStore(tmp_path / "finalized_projections.sqlite3")

    reconcile_and_save_bound = partial(
        reconcile_and_save,
        run_store=run_store,
        review_store=review_store,
        projection_store=projection_store,
    )

    runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=reconcile_and_save_bound,
        batch_root=ingestion_batch_root,
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
        repository=SqliteInputSessionRepository(input_sessions_path),
        json_service=JsonInputService(),
        file_service=FileInputService(),
        run_from_ingestion_service=_run_from_ingestion_adapter,
    )

    export_service = ExportService(
        run_store=run_store,
        projection_store=projection_store,
    )

    export_repository = SqliteExportArtifactRepository(str(export_db_path))
    export_storage = LocalArtifactStorage(export_root)

    def _export_generator(run_id: str, format: str, *, tenant_id: str | None = None) -> bytes:
        run = run_store.get_run(run_id)
        assert run is not None

        return export_service.export(
            run_id=run_id,
            tenant_id=run.tenant_id,
            export_format=ExportFormat(format),
        ).content

    export_delivery_service = ExportDeliveryService(
        repository=export_repository,
        storage=export_storage,
        export_generator=_export_generator,
    )

    artifact_query_service = ArtifactQueryService(
        repository=export_repository,
        storage=export_storage,
    )

    export_readiness_evaluator = ExportReadinessEvaluator(
        run_store=run_store,
        review_store=review_store,
        projection_store=projection_store,
    )

    run_view_query_service = RunViewQueryService(
        run_store=run_store,
        review_store=review_store,
        artifact_query_service=artifact_query_service,
        export_readiness_evaluator=export_readiness_evaluator,
    )

    return SystemContext(
        run_store=run_store,
        review_store=review_store,
        input_processing_service=input_processing_service,
        export_delivery_service=export_delivery_service,
        artifact_query_service=artifact_query_service,
        export_readiness_evaluator=export_readiness_evaluator,
        projection_store=projection_store,
        run_view_query_service=run_view_query_service,
        tmp_path=tmp_path,
    )


def test_happy_path_full_flow(system_context: SystemContext) -> None:
    payload = build_valid_happy_path_payload()

    session = system_context.input_processing_service.process_json(payload)

    assert session.status == "run_created", f"expected run_created session, got {session.status}"
    assert session.input_id, "expected input session id to be assigned"
    assert (
        session.ingestion_batch_id == session.input_id
    ), "expected ingestion batch id to reuse input session id"
    assert session.run_id, "expected happy-path submission to create a run"

    run = system_context.run_store.get_run(session.run_id)
    assert run is not None, f"expected persisted run for run_id={session.run_id}"
    assert run.run_id == session.run_id
    assert str(run.status) == "completed", f"expected completed run, got {run.status}"
    assert run.invoice_csv_path, "expected invoice csv path on persisted run"
    assert run.payment_csv_path, "expected payment csv path on persisted run"
    assert run.finished_at is not None, "expected completed run to have finished_at"

    readiness = system_context.export_readiness_evaluator.evaluate(session.run_id)
    assert getattr(readiness, "is_export_ready", False) is True, (
        f"expected export-ready run, got readiness={getattr(readiness, 'is_export_ready', None)} "
        f"reason={getattr(readiness, 'reason', None)}"
    )

    preexisting_artifacts = system_context.artifact_query_service.list_artifacts_for_run(
        session.run_id
    )
    assert preexisting_artifacts == [], "expected no artifacts before explicit export generation"

    artifact = system_context.export_delivery_service.create_export_artifact(
        session.run_id,
        "json",
    )

    assert artifact.run_id == session.run_id
    assert artifact.format == "json"
    assert artifact.byte_size is not None and artifact.byte_size > 0
    assert artifact.storage_key, "expected storage key for export artifact"

    artifacts = system_context.artifact_query_service.list_artifacts_for_run(session.run_id)
    assert len(artifacts) == 1, f"expected one artifact, got {len(artifacts)}"
    assert artifacts[0].id == artifact.id

    downloadable = system_context.artifact_query_service.get_downloadable_artifact_by_id(
        artifact.id
    )
    assert downloadable.id == artifact.id
    assert downloadable.run_id == session.run_id

    run_view = system_context.run_view_query_service.get_run_view(session.run_id)
    assert run_view is not None, "expected run view for completed run"
    assert run_view.run_id == session.run_id
    assert run_view.status == "completed", f"expected completed run view, got {run_view.status}"
    assert run_view.review_summary.total_items == 0
    assert run_view.review_summary.open_items == 0
    assert run_view.export_summary.status == "exported", (
        f"expected exported run view after artifact creation, got {run_view.export_summary.status}"
    )
    assert len(run_view.artifacts) == 1, f"expected one artifact in run view, got {len(run_view.artifacts)}"






