from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import Literal

from fastapi import FastAPI

from invomatch.api.actions import router as actions_router
from invomatch.api.export import router as export_router
from invomatch.api.health import router as health_router
from invomatch.api.reconciliation_runs import router as reconciliation_runs_router
from invomatch.api.review_cases import router as review_cases_router
from invomatch.services.action_service import ActionService
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.reconciliation_runs import DEFAULT_RUN_STORE_PATH
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_registry import RunRegistry
from invomatch.services.run_store import JsonRunStore, RunStore, SqliteRunStore

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
) -> FastAPI:
    app = FastAPI(title="InvoMatch")
    resolved_run_store = run_store or _build_run_store(backend=run_store_backend, path=run_store_path)
    app.state.run_store = resolved_run_store
    app.state.run_registry = RunRegistry(run_store=resolved_run_store)
    app.state.reconcile_and_save = partial(reconcile_and_save, run_store=resolved_run_store)

    # Current review API support is intentionally backed by in-memory review storage.
    # This gives EPIC 6 a real product-facing boundary now; sqlite-backed review query
    # support can be introduced in a follow-up step.
    app.state.review_store = InMemoryReviewStore()
    app.state.action_service = ActionService()

    app.include_router(health_router)
    app.include_router(reconciliation_runs_router)
    app.include_router(review_cases_router)
    app.include_router(actions_router)
    app.include_router(export_router)
    return app


app = create_app()