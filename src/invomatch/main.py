from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from invomatch.api.actions import router as actions_router
from invomatch.api.export import router as export_router
from invomatch.api.export_artifacts import router as export_artifacts_router
from invomatch.api.health import router as health_router
from invomatch.api.reconciliation_runs import router as reconciliation_runs_router
from invomatch.api.review_cases import router as review_cases_router
from invomatch.api.routes.input_boundary import router as input_boundary_router
from invomatch.services.input_boundary.input_processing_service import InputProcessingService
from invomatch.services.input_boundary.json_input_service import JsonInputService
from invomatch.services.input_boundary.file_input_service import FileInputService
from invomatch.services.input_boundary.repository import InMemoryInputSessionRepository
from invomatch.services.input_boundary.sqlite_repository import SqliteInputSessionRepository
from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)
from invomatch.services.action_service import ActionService
from invomatch.services.artifact_query_service import ArtifactQueryService
from invomatch.services.export import ExportService, RunFinalizedResultReader
from invomatch.services.export_delivery_service import ExportDeliveryService
from invomatch.services.ingestion_run_integration.runtime_adapter import IngestionRunRuntimeAdapter
from invomatch.services.orchestration.export_readiness_evaluator import ExportReadinessEvaluator
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.reconciliation_runs import DEFAULT_RUN_STORE_PATH
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_registry import RunRegistry
from invomatch.services.run_store import JsonRunStore, RunStore, SqliteRunStore
from invomatch.services.storage.local_storage import LocalArtifactStorage

RunStoreBackend = Literal["json", "sqlite"]
DEFAULT_SQLITE_RUN_STORE_PATH = Path("output") / "reconciliation_runs.sqlite3"


def _build_run_store(*, backend: RunStoreBackend, path: Path | None = None) -> RunStore:
    if backend == "sqlite":
        return SqliteRunStore(path or DEFAULT_SQLITE_RUN_STORE_PATH)
    return JsonRunStore(path or DEFAULT_RUN_STORE_PATH)


def create_app(
    *,
    run_store: RunStore | None = None,
    run_store_backend: RunStoreBackend = "json",
    run_store_path: Path | None = None,
    export_base_dir: Path | None = None,
) -> FastAPI:
    app = FastAPI(title="InvoMatch")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    resolved_run_store = run_store or _build_run_store(
        backend=run_store_backend,
        path=run_store_path,
    )

    export_root = Path(export_base_dir or (Path("output") / "exports"))
    export_root.mkdir(parents=True, exist_ok=True)

    app.state.run_store = resolved_run_store
    app.state.run_registry = RunRegistry(run_store=resolved_run_store)
    app.state.reconcile_and_save = partial(reconcile_and_save, run_store=resolved_run_store)
    app.state.ingestion_run_runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=app.state.reconcile_and_save,
    )

    # Current review API support is intentionally backed by in-memory review storage.
    # This gives EPIC 6 a real product-facing boundary now; sqlite-backed review query
    # support can be introduced in a follow-up step.
    app.state.review_store = InMemoryReviewStore()

    export_service = ExportService(
        reader=RunFinalizedResultReader(
            run_store=resolved_run_store,
            review_store=app.state.review_store,
        ),
        run_store=resolved_run_store,
    )

    export_artifact_repository = SqliteExportArtifactRepository(
        str(export_root / "export_artifacts.sqlite3")
    )
    export_artifact_storage = LocalArtifactStorage(export_root)

    def export_generator(run_id: str, format: str) -> bytes:
        from invomatch.domain.export import ExportFormat

        return export_service.export(
            run_id=run_id,
            export_format=ExportFormat(format),
        ).content

    export_delivery_service = ExportDeliveryService(
        repository=export_artifact_repository,
        storage=export_artifact_storage,
        export_generator=export_generator,
    )
    artifact_query_service = ArtifactQueryService(
        repository=export_artifact_repository,
        storage=export_artifact_storage,
    )
    export_readiness_evaluator = ExportReadinessEvaluator(
        run_store=resolved_run_store,
        review_store=app.state.review_store,
    )

    app.state.export_service = export_service
    app.state.export_artifact_repository = export_artifact_repository
    app.state.export_artifact_storage = export_artifact_storage
    app.state.export_delivery_service = export_delivery_service
    app.state.artifact_query_service = artifact_query_service
    app.state.export_readiness_evaluator = export_readiness_evaluator

    app.state.action_service = ActionService(
        run_store=resolved_run_store,
        export_base_dir=export_root,
    )

    # --- EPIC 20: Input Boundary Wiring ---
    input_session_repo = SqliteInputSessionRepository(Path("output") / "input_sessions.sqlite3")
    json_input_service = JsonInputService()
    file_input_service = FileInputService()
    file_input_service = FileInputService()

    def _run_from_ingestion_adapter(ingestion_batch_id, payload):
        adapter = app.state.ingestion_run_runtime_adapter
        return adapter.create_run_from_ingestion(
            ingestion_batch_id=ingestion_batch_id,
            ingestion_succeeded=True,
            accepted_invoices=payload["invoices"],
            accepted_payments=payload["payments"],
            rejected_count=0,
            conflict_count=0,
            blocking_conflict=False,
        )

    input_processing_service = InputProcessingService(
        repository=input_session_repo,
        json_service=json_input_service,
        file_service=file_input_service,
        run_from_ingestion_service=_run_from_ingestion_adapter,
    )

    app.state.input_session_repository = input_session_repo
    app.state.input_processing_service = input_processing_service
    app.state.file_input_service = file_input_service
    app.include_router(input_boundary_router)
    # --- END EPIC 20 ---
    app.include_router(health_router)
    app.include_router(reconciliation_runs_router)
    app.include_router(review_cases_router)
    app.include_router(actions_router)
    app.include_router(export_router)
    app.include_router(export_artifacts_router)
    return app


app = create_app()



