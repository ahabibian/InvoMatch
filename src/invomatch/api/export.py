from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from invomatch.api.product_models.export import ProductExportModel
from invomatch.services.run_registry import RunRegistry

router = APIRouter(prefix="/api/reconciliation/runs", tags=["reconciliation-export"])


@router.get("/{run_id}/export", response_model=ProductExportModel)
def get_reconciliation_run_export(run_id: str, request: Request) -> ProductExportModel:
    registry: RunRegistry = request.app.state.run_registry
    run = registry.get_run(run_id)

    if run is None:
        raise HTTPException(status_code=404, detail="Reconciliation run not found")

    return ProductExportModel(
        run_id=str(run.run_id),
        export_status="not_ready",
        export_format="json",
        download_url=None,
        generated_at=None,
    )