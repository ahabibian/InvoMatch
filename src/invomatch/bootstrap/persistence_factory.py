from dataclasses import dataclass

from invomatch.config.models import ApplicationSettings
from invomatch.repositories.audit_event_repository_sqlite import SqliteAuditEventRepository
from invomatch.services.reconciliation_runs import DEFAULT_RUN_STORE_PATH
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import JsonRunStore, SqliteRunStore
from invomatch.services.sqlite_review_store import SqliteReviewStore


@dataclass(frozen=True)
class PersistenceDependencies:
    run_store: object
    review_store: object
    audit_event_repository: object
    run_store_backend: str
    review_store_backend: str
    feedback_store_backend: str
    match_record_store_backend: str


def _build_run_store(settings: ApplicationSettings) -> object:
    backend = settings.persistence.run_store_backend.strip().lower()
    if backend == "sqlite":
        return SqliteRunStore(settings.persistence.run_store_path)
    if backend == "json":
        return JsonRunStore(settings.persistence.run_store_path or DEFAULT_RUN_STORE_PATH)
    raise ValueError(f"Unsupported run store backend: {settings.persistence.run_store_backend}")


def _build_review_store(settings: ApplicationSettings) -> object:
    backend = settings.persistence.review_store_backend.strip().lower()
    if backend == "sqlite":
        return SqliteReviewStore(settings.persistence.review_store_path)
    if backend == "memory":
        return InMemoryReviewStore()
    raise ValueError(
        f"Unsupported review store backend: {settings.persistence.review_store_backend}"
    )


def build_persistence_dependencies(settings: ApplicationSettings) -> PersistenceDependencies:
    return PersistenceDependencies(
        run_store=_build_run_store(settings),
        review_store=_build_review_store(settings),
        audit_event_repository=SqliteAuditEventRepository(
            str(settings.persistence.audit_event_db_path)
        ),
        run_store_backend=settings.persistence.run_store_backend,
        review_store_backend=settings.persistence.review_store_backend,
        feedback_store_backend=settings.persistence.feedback_store_backend,
        match_record_store_backend=settings.persistence.match_record_store_backend,
    )