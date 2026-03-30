from __future__ import annotations

from typing import Any, Iterable

from invomatch.api.product_models.run import (
    ProductRunDetail,
    ProductRunSummary,
)
from invomatch.api.product_models.match_result import ProductMatchResult
from invomatch.api.product_models.review_case import ProductReviewCase
from invomatch.api.product_models.action import (
    ProductActionRequest,
    ProductActionResponse,
)
from invomatch.api.product_models.export import ProductExportModel


# =========================
# RUN MAPPERS
# =========================

def to_product_run_summary(run: Any) -> ProductRunSummary:
    return ProductRunSummary(
        run_id=str(run.id),
        status=str(run.status),
        created_at=run.created_at,
        updated_at=getattr(run, "updated_at", None),
        invoice_count=int(getattr(run, "invoice_count", 0)),
        payment_count=int(getattr(run, "payment_count", 0)),
        match_count=int(getattr(run, "match_count", 0)),
        review_required_count=int(getattr(run, "review_required_count", 0)),
    )


def to_product_run_detail(run: Any, matches: Iterable[Any]) -> ProductRunDetail:
    return ProductRunDetail(
        run_id=str(run.id),
        status=str(run.status),
        created_at=run.created_at,
        updated_at=getattr(run, "updated_at", None),
        invoice_count=int(getattr(run, "invoice_count", 0)),
        payment_count=int(getattr(run, "payment_count", 0)),
        match_count=int(getattr(run, "match_count", 0)),
        review_required_count=int(getattr(run, "review_required_count", 0)),
        matches=[to_product_match_result(m) for m in matches],
    )


# =========================
# MATCH MAPPERS
# =========================

def to_product_match_result(match: Any) -> ProductMatchResult:
    return ProductMatchResult(
        match_id=str(match.id),
        invoice_id=str(match.invoice_id),
        payment_id=getattr(match, "payment_id", None),
        status=str(match.status),
        confidence=getattr(match, "confidence", None),
        explanation=[],
    )


# =========================
# REVIEW MAPPERS
# =========================

def to_product_review_case(case: Any) -> ProductReviewCase:
    return ProductReviewCase(
        case_id=str(case.id),
        run_id=str(case.run_id),
        status=str(case.status),
        reason_code=str(case.reason_code),
        match_id=getattr(case, "match_id", None),
        explanation=[],
        recommended_action=getattr(case, "recommended_action", None),
    )


# =========================
# ACTION MAPPERS
# =========================

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


# =========================
# EXPORT MAPPERS
# =========================

def to_product_export_model(export: Any) -> ProductExportModel:
    return ProductExportModel(
        run_id=str(export.run_id),
        export_status=str(export.status),
        export_format=str(export.format),
        download_url=getattr(export, "download_url", None),
        generated_at=getattr(export, "generated_at", None),
    )