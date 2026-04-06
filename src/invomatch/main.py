from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Literal

from fastapi import FastAPI

from invomatch.api.actions import router as actions_router
from invomatch.api.export import router as export_router
from invomatch.api.export_artifacts import router as export_artifacts_router
from invomatch.api.health import router as health_router
from invomatch.api.reconciliation_runs import router as reconciliation_runs_router
from invomatch.api.review_cases import router as review_cases_router
from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)
from invomatch.services.action_service import ActionService
from invomatch.services.artifact_query_service import ArtifactQueryService
from invomatch.services.export import ExportService, RunFinalizedResultReader
from invomatch.services.export_delivery_service import ExportDeliveryService
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
    resolved_run_store = run_store or _build_run_store(
        backend=run_store_backend,
        path=run_store_path,
    )

    export_root = Path(export_base_dir or (Path("output") / "exports"))
    export_root.mkdir(parents=True, exist_ok=True)

    app.state.run_store = resolved_run_store
    app.state.run_registry = RunRegistry(run_store=resolved_run_store)
    app.state.reconcile_and_save = partial(reconcile_and_save, run_store=resolved_run_store)

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

    app.include_router(health_router)
    app.include_router(reconciliation_runs_router)
    app.include_router(review_cases_router)
    app.include_router(actions_router)
    app.include_router(export_router)
    app.include_router(export_artifacts_router)
    return app


app = create_app()