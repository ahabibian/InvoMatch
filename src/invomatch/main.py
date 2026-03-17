from fastapi import FastAPI

from invomatch.api.health import router as health_router
from invomatch.api.reconciliation_runs import router as reconciliation_runs_router
from invomatch.services.run_registry import RunRegistry

app = FastAPI(title="InvoMatch")
app.state.run_registry = RunRegistry()

app.include_router(health_router)
app.include_router(reconciliation_runs_router)
