from dataclasses import dataclass

from invomatch.config.models import ApplicationSettings


@dataclass(frozen=True)
class PersistenceDependencies:
    run_store_backend: str
    review_store_backend: str
    feedback_store_backend: str
    match_record_store_backend: str


def build_persistence_dependencies(settings: ApplicationSettings) -> PersistenceDependencies:
    return PersistenceDependencies(
        run_store_backend=settings.persistence.run_store_backend,
        review_store_backend=settings.persistence.review_store_backend,
        feedback_store_backend=settings.persistence.feedback_store_backend,
        match_record_store_backend=settings.persistence.match_record_store_backend,
    )