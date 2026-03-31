from __future__ import annotations

from typing import Any, Iterable

from invomatch.api.product_models.run import (
    ProductRunDetail,
    ProductRunListResponse,
    ProductRunSummary,
)
from invomatch.api.product_models.match_result import ProductMatchResult
from invomatch.api.product_models.review_case import ProductReviewCase
from invomatch.api.product_models.action import (
    ProductActionRequest,
    ProductActionResponse,
)
from invomatch.api.product_models.export import ProductExportModel


def _safe_match_count(run: Any) -> int:
    report = getattr(run, "report", None)
    if report is None:
        return 0
    return int(getattr(report, "matched", 0) or 0)


def to_product_run_summary(run: Any) -> ProductRunSummary:
    return ProductRunSummary(
        run_id=str(run.run_id),
        status=str(run.status),
        created_at=run.created_at,
        updated_at=getattr(run, "updated_at", None),
        match_count=_safe_match_count(run),
        review_required_count=0,
    )


def to_product_run_list_response(
    runs: Iterable[Any],
    total: int,
    limit: int,
    offset: int,
) -> ProductRunListResponse:
    return ProductRunListResponse(
        items=[to_product_run_summary(run) for run in runs],
        total=int(total),
        limit=int(limit),
        offset=int(offset),
    )


def to_product_run_detail(run: Any) -> ProductRunDetail:
    return ProductRunDetail(
        run_id=str(run.run_id),
        status=str(run.status),
        created_at=run.created_at,
        updated_at=getattr(run, "updated_at", None),
        match_count=_safe_match_count(run),
        review_required_count=0,
        matches=[],
    )


def to_product_match_result(match: Any) -> ProductMatchResult:
    return ProductMatchResult(
        match_id=str(getattr(match, "match_id", getattr(match, "id", ""))),
        invoice_id=str(getattr(match, "invoice_id", "")),
        payment_id=getattr(match, "payment_id", None),
        status=str(getattr(match, "status", "unmatched")),
        confidence=getattr(match, "confidence", None),
        explanation=[],
    )


def to_product_review_case(projection: Any) -> ProductReviewCase:
    return ProductReviewCase(
        case_id=str(projection.case_id),
        run_id=str(projection.run_id),
        status=str(projection.status),
        reason_code=str(projection.reason_code),
        match_id=getattr(projection, "match_id", None),
        explanation=[],
        recommended_action=getattr(projection, "recommended_action", None),
    )


def to_internal_action_command(request: ProductActionRequest) -> dict[str, Any]:
    return {
        "action_type": request.action_type,
        "target_id": request.target_id,
        "payload": request.payload,
        "note": request.note,
    }


def to_product_action_response(
    run_id: str,
    request: ProductActionRequest,
    accepted: bool,
    status: str,
    message: str | None = None,
) -> ProductActionResponse:
    return ProductActionResponse(
        run_id=run_id,
        action_type=request.action_type,
        accepted=accepted,
        status=status,
        message=message,
    )


def to_product_export_model(export: Any) -> ProductExportModel:
    return ProductExportModel(
        run_id=str(export.run_id),
        export_status=str(getattr(export, "status", "not_ready")),
        export_format=str(getattr(export, "format", "json")),
        download_url=getattr(export, "download_url", None),
        generated_at=getattr(export, "generated_at", None),
    )