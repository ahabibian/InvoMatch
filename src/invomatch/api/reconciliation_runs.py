from __future__ import annotations

from pathlib import Path
from typing import Callable, Literal

from fastapi import APIRouter, HTTPException, Request, status

from invomatch.api.reconciliation_schemas import (
    ApiErrorResponse,
    CreateRunRequest,
    RunDetailResponse,
    RunListResponse,
    to_api_error_response,
    to_run_detail_response,
    to_run_summary_response,
)
from invomatch.domain.models import ReconciliationRun, RunStatus
from invomatch.services.reconciliation_errors import (
    ReconciliationExecutionError,
    ReconciliationInputValidationError,
    RunStorageError,
)
from invomatch.services.run_registry import RunRegistry

router = APIRouter(prefix="/api/reconciliation/runs", tags=["reconciliation-runs"])


@router.post(
    "",
    response_model=RunDetailResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ApiErrorResponse}, 500: {"model": ApiErrorResponse}},
)
def create_reconciliation_run(request_body: CreateRunRequest, request: Request) -> RunDetailResponse:
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
    return to_run_detail_response(run)


@router.get("", response_model=RunListResponse)
def list_reconciliation_runs(
    request: Request,
    status: RunStatus | None = None,
    limit: int = 50,
    offset: int = 0,
    sort_order: Literal["asc", "desc"] = "desc",
) -> RunListResponse:
    registry: RunRegistry = request.app.state.run_registry
    runs, total = registry.list_runs(
        status=status,
        limit=limit,
        offset=offset,
        sort_order=sort_order,
    )
    return RunListResponse(
        items=[to_run_summary_response(run) for run in runs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{run_id}", response_model=RunDetailResponse)
def get_reconciliation_run(run_id: str, request: Request) -> RunDetailResponse:
    registry: RunRegistry = request.app.state.run_registry
    run = registry.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Reconciliation run not found")
    return to_run_detail_response(run)
