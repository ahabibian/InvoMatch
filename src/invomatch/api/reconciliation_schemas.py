from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from invomatch.domain.models import ReconciliationRun


class RunSummaryResponse(BaseModel):
    run_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    invoice_csv_path: str
    payment_csv_path: str
    match_count: int
    unmatched_invoice_count: int
    unmatched_payment_count: int


class RunListResponse(BaseModel):
    items: list[RunSummaryResponse]
    total: int
    limit: int
    offset: int


class RunDetailResponse(BaseModel):
    run_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    invoice_csv_path: str
    payment_csv_path: str
    report: dict[str, Any]


def to_run_summary_response(run: ReconciliationRun) -> RunSummaryResponse:
    return RunSummaryResponse(
        run_id=run.run_id,
        status="completed",
        created_at=run.created_at,
        updated_at=run.created_at,
        invoice_csv_path=run.invoice_csv_path,
        payment_csv_path=run.payment_csv_path,
        match_count=run.report.matched,
        unmatched_invoice_count=run.report.unmatched,
        unmatched_payment_count=run.report.unmatched,
    )


def to_run_detail_response(run: ReconciliationRun) -> RunDetailResponse:
    return RunDetailResponse(
        run_id=run.run_id,
        status="completed",
        created_at=run.created_at,
        updated_at=run.created_at,
        invoice_csv_path=run.invoice_csv_path,
        payment_csv_path=run.payment_csv_path,
        report=run.report.model_dump(mode="json"),
    )
