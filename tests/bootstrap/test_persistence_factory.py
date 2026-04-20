from dataclasses import replace

from invomatch.bootstrap.persistence_factory import build_persistence_dependencies
from invomatch.config.settings import load_application_settings
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import JsonRunStore, SqliteRunStore
from invomatch.services.sqlite_review_store import SqliteReviewStore


def test_build_persistence_dependencies_builds_sqlite_stores(monkeypatch, tmp_path):
    monkeypatch.setenv("INVOMATCH_ENV", "local")

    settings = load_application_settings()
    persistence = replace(
        settings.persistence,
        run_store_backend="sqlite",
        run_store_path=tmp_path / "runs.sqlite3",
        review_store_backend="sqlite",
        review_store_path=tmp_path / "review.sqlite3",
    )
    settings = replace(settings, persistence=persistence)

    deps = build_persistence_dependencies(settings)

    assert isinstance(deps.run_store, SqliteRunStore)
    assert isinstance(deps.review_store, SqliteReviewStore)


def test_build_persistence_dependencies_builds_json_and_memory(monkeypatch, tmp_path):
    monkeypatch.setenv("INVOMATCH_ENV", "local")

    settings = load_application_settings()
    persistence = replace(
        settings.persistence,
        run_store_backend="json",
        run_store_path=tmp_path / "runs.json",
        review_store_backend="memory",
    )
    settings = replace(settings, persistence=persistence)

    deps = build_persistence_dependencies(settings)

    assert isinstance(deps.run_store, JsonRunStore)
    assert isinstance(deps.review_store, InMemoryReviewStore)