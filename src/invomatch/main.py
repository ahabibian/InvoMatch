from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from invomatch.api.actions import router as actions_router
from invomatch.api.audit_events import router as audit_events_router
from invomatch.api.export import router as export_router
from invomatch.api.export_artifacts import router as export_artifacts_router
from invomatch.api.health import router as health_router
from invomatch.api.reconciliation_runs import router as reconciliation_runs_router
from invomatch.api.review_cases import router as review_cases_router
from invomatch.api.routes.input_boundary import router as input_boundary_router
from invomatch.bootstrap.persistence_factory import build_persistence_dependencies
from invomatch.bootstrap.runtime_factory import build_runtime_dependencies
from invomatch.bootstrap.storage_factory import build_storage_dependencies
from invomatch.bootstrap.validation_factory import validate_startup_configuration
from invomatch.config.settings import load_application_settings
from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)
from invomatch.services.action_service import ActionService
from invomatch.services.artifact_query_service import ArtifactQueryService
from invomatch.services.audit import AuditQueryService
from invomatch.services.export import ExportService, RunFinalizedResultReader
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
from invomatch.services.operational import (
    OperationalAuditService,
    PersistentOperationalAuditRepository,
)
from invomatch.services.operational.operational_metrics import (
    InMemoryOperationalMetricsStore,
    OperationalMetricsService,
)
from invomatch.services.orchestration.export_readiness_evaluator import (
    ExportReadinessEvaluator,
)
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.restart_consistency_repair_service import (
    RestartConsistencyRepairService,
)
from invomatch.services.run_registry import RunRegistry
from invomatch.services.run_store import RunStore
from invomatch.services.security import (
    AuthenticationService,
    AuthorizationService,
    PersistentSecurityAuditService,
    StaticTokenProvider,
)
from invomatch.services.startup_repair_coordinator import StartupRepairCoordinator

RunStoreBackend = Literal["json", "sqlite"]
ReviewStoreBackend = Literal["memory", "sqlite"]


def create_app(
    *,
    run_store: RunStore | None = None,
    review_store=None,
    export_artifact_repository=None,
    artifact_storage=None,
    run_store_backend: RunStoreBackend | None = None,
    run_store_path: Path | None = None,
    review_store_backend: ReviewStoreBackend | None = None,
    review_store_path: Path | None = None,
    export_base_dir: Path | None = None,
    startup_now_provider=None,
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

    settings = load_application_settings()

    effective_run_store_backend = run_store_backend or settings.persistence.run_store_backend
    effective_review_store_backend = (
        review_store_backend or settings.persistence.review_store_backend
    )
    effective_run_store_path = run_store_path or settings.persistence.run_store_path
    effective_review_store_path = (
        review_store_path or settings.persistence.review_store_path
    )

    if (
        effective_run_store_backend != settings.persistence.run_store_backend
        or effective_review_store_backend != settings.persistence.review_store_backend
        or effective_run_store_path != settings.persistence.run_store_path
        or effective_review_store_path != settings.persistence.review_store_path
    ):
        settings = load_application_settings()
        settings = settings.__class__(
            environment=settings.environment,
            persistence=settings.persistence.__class__(
                run_store_backend=effective_run_store_backend,
                run_store_path=effective_run_store_path,
                review_store_backend=effective_review_store_backend,
                review_store_path=effective_review_store_path,
                feedback_store_backend=settings.persistence.feedback_store_backend,
                feedback_store_path=settings.persistence.feedback_store_path,
                match_record_store_backend=settings.persistence.match_record_store_backend,
                match_record_store_path=settings.persistence.match_record_store_path,
                export_artifact_db_path=settings.persistence.export_artifact_db_path,
                audit_event_db_path=settings.persistence.audit_event_db_path,
                input_session_db_path=settings.persistence.input_session_db_path,
                ingestion_batch_root=settings.persistence.ingestion_batch_root,
            ),
            storage=settings.storage,
            runtime=settings.runtime,
            observability=settings.observability,
            upload=settings.upload,
            scheduler=settings.scheduler,
            feature_flags=settings.feature_flags,
            security=settings.security,
        )

    runtime_dependencies = build_runtime_dependencies(settings)
    startup_validation_result = validate_startup_configuration(settings)

    if runtime_dependencies.startup_validation_enabled and not startup_validation_result.is_valid:
        raise ValueError(
            "Invalid startup configuration: "
            + "; ".join(startup_validation_result.errors)
        )

    persistence_dependencies = build_persistence_dependencies(settings)
    storage_dependencies = build_storage_dependencies(
        settings,
        export_base_dir=export_base_dir,
    )

    resolved_run_store = run_store or persistence_dependencies.run_store
    resolved_review_store = review_store or persistence_dependencies.review_store
    audit_event_repository = persistence_dependencies.audit_event_repository
    audit_query_service = AuditQueryService(audit_event_repository)
    export_root = storage_dependencies.export_root
    export_root.mkdir(parents=True, exist_ok=True)

    token_provider = StaticTokenProvider(settings.security.seed_tokens_json)
    authentication_service = AuthenticationService(token_provider=token_provider)
    authorization_service = AuthorizationService()
    security_audit_service = PersistentSecurityAuditService(audit_event_repository)
    operational_audit_service = OperationalAuditService(
        PersistentOperationalAuditRepository(audit_event_repository)
    )

    app.state.application_settings = settings
    app.state.security_settings = settings.security
    app.state.token_provider = token_provider
    app.state.authentication_service = authentication_service
    app.state.authorization_service = authorization_service
    app.state.security_audit_service = security_audit_service
    app.state.operational_audit_service = operational_audit_service
    app.state.startup_validation_result = startup_validation_result
    app.state.persistence_dependencies = persistence_dependencies
    app.state.storage_dependencies = storage_dependencies
    app.state.runtime_dependencies = runtime_dependencies
    app.state.audit_event_repository = audit_event_repository
    app.state.audit_query_service = audit_query_service
    app.state.run_store = resolved_run_store
    app.state.run_registry = RunRegistry(run_store=resolved_run_store)
    app.state.reconcile_and_save = partial(
        reconcile_and_save,
        run_store=resolved_run_store,
    )
    app.state.ingestion_run_runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=app.state.reconcile_and_save,
    )

    app.state.review_store = resolved_review_store

    operational_metrics_store = InMemoryOperationalMetricsStore()
    operational_metrics_service = OperationalMetricsService(
        operational_metrics_store
    )
    restart_consistency_repair_service = RestartConsistencyRepairService(
        run_store=resolved_run_store,
        review_store=app.state.review_store,
    )
    startup_repair_coordinator = StartupRepairCoordinator(
        run_store=resolved_run_store,
        review_store=app.state.review_store,
        repair_service=restart_consistency_repair_service,
        metrics_service=operational_metrics_service,
        audit_service=operational_audit_service,
        now_provider=startup_now_provider,
    )

    if runtime_dependencies.startup_repair_enabled:
        startup_repair_result = startup_repair_coordinator.run_startup_scan()
    else:
        startup_repair_result = None

    app.state.operational_metrics_store = operational_metrics_store
    app.state.operational_metrics_service = operational_metrics_service
    app.state.restart_consistency_repair_service = restart_consistency_repair_service
    app.state.startup_repair_coordinator = startup_repair_coordinator
    app.state.startup_repair_result = startup_repair_result

    export_service = ExportService(
        reader=RunFinalizedResultReader(
            run_store=resolved_run_store,
            review_store=app.state.review_store,
        ),
        run_store=resolved_run_store,
    )

    resolved_export_artifact_repository = (
        export_artifact_repository
        or SqliteExportArtifactRepository(
            str(export_root / "export_artifacts.sqlite3")
        )
    )
    resolved_artifact_storage = (
        artifact_storage or storage_dependencies.artifact_storage
    )

    def export_generator(run_id: str, format: str) -> bytes:
        from invomatch.domain.export import ExportFormat

        return export_service.export(
            run_id=run_id,
            export_format=ExportFormat(format),
        ).content

    export_delivery_service = ExportDeliveryService(
        repository=resolved_export_artifact_repository,
        storage=resolved_artifact_storage,
        export_generator=export_generator,
    )
    artifact_query_service = ArtifactQueryService(
        repository=resolved_export_artifact_repository,
        storage=resolved_artifact_storage,
    )
    export_readiness_evaluator = ExportReadinessEvaluator(
        run_store=resolved_run_store,
        review_store=app.state.review_store,
    )

    app.state.export_service = export_service
    app.state.export_artifact_repository = resolved_export_artifact_repository
    app.state.export_artifact_storage = resolved_artifact_storage
    app.state.export_delivery_service = export_delivery_service
    app.state.artifact_query_service = artifact_query_service
    app.state.export_readiness_evaluator = export_readiness_evaluator

    app.state.action_service = ActionService(
        run_store=resolved_run_store,
        export_base_dir=export_root,
    )

    input_session_repo = SqliteInputSessionRepository(
        settings.persistence.input_session_db_path
    )
    json_input_service = JsonInputService()
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
    app.include_router(health_router)
    app.include_router(audit_events_router)
    app.include_router(reconciliation_runs_router)
    app.include_router(review_cases_router)
    app.include_router(actions_router)
    app.include_router(export_router)
    app.include_router(export_artifacts_router)

    return app


app = create_app()