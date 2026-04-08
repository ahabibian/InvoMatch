from __future__ import annotations

from pathlib import Path
from typing import Callable, Literal

from fastapi import APIRouter, HTTPException, Request, status

from invomatch.api.mappers.product_contract import (
    to_product_run_detail,
    to_product_run_list_response,
)
from invomatch.api.product_models.run import (
    ProductRunDetail,
    ProductRunListResponse,
)
from invomatch.api.product_models.run_view import ProductRunView
from invomatch.api.reconciliation_schemas import (
    ApiErrorResponse,
    CreateRunFromIngestionRequest,
    CreateRunRequest,
    IngestionRunResponse,
    to_api_error_response,
)
from invomatch.domain.models import ReconciliationRun, RunStatus
from invomatch.services.artifact_query_service import ArtifactQueryService
from invomatch.services.ingestion_run_integration.runtime_adapter import (
    IngestionRunRuntimeAdapter,
)
from invomatch.services.reconciliation_errors import (
    ReconciliationExecutionError,
    ReconciliationInputValidationError,
    RunStorageError,
)
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_registry import RunRegistry
from invomatch.services.run_view_query_service import RunViewQueryService

router = APIRouter(prefix="/api/reconciliation/runs", tags=["reconciliation-runs"])


@router.post(
    "",
    response_model=ProductRunDetail,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
)
def create_reconciliation_run(request_body: CreateRunRequest, request: Request) -> ProductRunDetail:
    reconcile_and_save: Callable[[Path, Path], ReconciliationRun] = request.app.state.reconcile_and_save
    try:
        run = reconcile_and_save(
            Path(request_body.invoice_csv_path),
            Path(request_body.payment_csv_path),
        )
    except ReconciliationInputValidationError as exc:
        raise HTTPException(status_code=400, detail=to_api_error_response(exc).model_dump(exclude_none=True)) from exc
    except (ReconciliationExecutionError, RunStorageError) as exc:
        raise HTTPException(status_code=500, detail=to_api_error_response(exc).model_dump(exclude_none=True)) from exc
    return to_product_run_detail(run)


@router.post(
    "/ingest",
    response_model=IngestionRunResponse,
    status_code=status.HTTP_200_OK,
)
def create_reconciliation_run_from_ingestion(
    request_body: CreateRunFromIngestionRequest,
    request: Request,
) -> IngestionRunResponse:
    adapter: IngestionRunRuntimeAdapter = request.app.state.ingestion_run_runtime_adapter

    result = adapter.create_run_from_ingestion(
        ingestion_batch_id=request_body.ingestion_batch_id,
        ingestion_succeeded=True,
        accepted_invoices=[item.model_dump(exclude_none=True) for item in request_body.invoices],
        accepted_payments=[item.model_dump(exclude_none=True) for item in request_body.payments],
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
    )

    return IngestionRunResponse(
        status=result.status.value,
        run_id=result.run_id,
        reason_code=result.reason_code,
        ingestion_batch_id=result.ingestion_batch_id,
        accepted_invoice_count=result.accepted_invoice_count,
        accepted_payment_count=result.accepted_payment_count,
        rejected_count=result.rejected_count,
        conflict_count=result.conflict_count,
        partial_ingestion=result.partial_ingestion,
    )


@router.get("", response_model=ProductRunListResponse)
def list_reconciliation_runs(
    request: Request,
    status: RunStatus | None = None,
    limit: int = 50,
    offset: int = 0,
    sort_order: Literal["asc", "desc"] = "desc",
) -> ProductRunListResponse:
    registry: RunRegistry = request.app.state.run_registry
    runs, total = registry.list_runs(
        status=status,
        limit=limit,
        offset=offset,
        sort_order=sort_order,
    )
    return to_product_run_list_response(
        runs=runs,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{run_id}", response_model=ProductRunDetail)
def get_reconciliation_run(run_id: str, request: Request) -> ProductRunDetail:
    registry: RunRegistry = request.app.state.run_registry
    run = registry.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Reconciliation run not found")
    return to_product_run_detail(run)


@router.get("/{run_id}/view", response_model=ProductRunView)
def get_reconciliation_run_view(run_id: str, request: Request) -> ProductRunView:
    registry: RunRegistry = request.app.state.run_registry
    review_store: InMemoryReviewStore | None = getattr(request.app.state, "review_store", None)
    artifact_query_service: ArtifactQueryService | None = getattr(
        request.app.state,
        "artifact_query_service",
        None,
    )

    query_service = RunViewQueryService(
        run_store=registry,
        review_store=review_store,
        artifact_query_service=artifact_query_service,
    )
    run_view = query_service.get_run_view(run_id)

    if run_view is None:
        raise HTTPException(status_code=404, detail="Reconciliation run not found")

    return run_view