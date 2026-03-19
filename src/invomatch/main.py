from __future__ import annotations

from functools import partial

from fastapi import FastAPI

from invomatch.api.health import router as health_router
from invomatch.api.reconciliation_runs import router as reconciliation_runs_router
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.reconciliation_runs import DEFAULT_RUN_STORE_PATH
from invomatch.services.run_registry import RunRegistry
from invomatch.services.run_store import JsonRunStore


def create_app() -> FastAPI:
    app = FastAPI(title="InvoMatch")
    run_store = JsonRunStore(DEFAULT_RUN_STORE_PATH)
    app.state.run_store = run_store
    app.state.run_registry = RunRegistry(run_store=run_store)
    app.state.reconcile_and_save = partial(reconcile_and_save, run_store=run_store)

    app.include_router(health_router)
    app.include_router(reconciliation_runs_router)
    return app


app = create_app()
