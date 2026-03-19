from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from invomatch.domain.models import ReconciliationRun, RunStatus


class CreateRunRequest(BaseModel):
    invoice_csv_path: str = Field(min_length=1)
    payment_csv_path: str = Field(min_length=1)


class RunSummaryResponse(BaseModel):
    run_id: str
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    invoice_csv_path: str
    payment_csv_path: str
    match_count: int | None
    unmatched_invoice_count: int | None
    unmatched_payment_count: int | None
    error_message: str | None


class RunListResponse(BaseModel):
    items: list[RunSummaryResponse]
    total: int
    limit: int
    offset: int


class RunDetailResponse(BaseModel):
    run_id: str
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    invoice_csv_path: str
    payment_csv_path: str
    error_message: str | None
    report: dict[str, Any] | None


def to_run_summary_response(run: ReconciliationRun) -> RunSummaryResponse:
    return RunSummaryResponse(
        run_id=run.run_id,
        status=run.status,
        created_at=run.created_at,
        updated_at=run.updated_at,
        started_at=run.started_at,
        finished_at=run.finished_at,
        invoice_csv_path=run.invoice_csv_path,
        payment_csv_path=run.payment_csv_path,
        match_count=run.report.matched if run.report is not None else None,
        unmatched_invoice_count=run.report.unmatched if run.report is not None else None,
        unmatched_payment_count=run.report.unmatched if run.report is not None else None,
        error_message=run.error_message,
    )


def to_run_detail_response(run: ReconciliationRun) -> RunDetailResponse:
    return RunDetailResponse(
        run_id=run.run_id,
        status=run.status,
        created_at=run.created_at,
        updated_at=run.updated_at,
        started_at=run.started_at,
        finished_at=run.finished_at,
        invoice_csv_path=run.invoice_csv_path,
        payment_csv_path=run.payment_csv_path,
        error_message=run.error_message,
        report=run.report.model_dump(mode="json") if run.report is not None else None,
    )
