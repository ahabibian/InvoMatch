from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from invomatch.services.match_detail_read_service import (
    MatchDetailReadError,
    read_match_detail_by_id,
)
from invomatch.api.mappers.product_contract import (
 to_product_review_case,
 to_product_review_queue_item,
)
from invomatch.api.product_models.review_case import (
    ProductMatchDetailResponse,
    ProductReviewCase,
 ProductReviewQueueItem,
)
from invomatch.api.security import require_permission
from invomatch.domain.security import Permission
from invomatch.services.review_queries import ReviewQueryService


router = APIRouter(tags=["reconciliation-review"])


@router.get("/api/review/queue", response_model=list[ProductReviewQueueItem])
def list_review_queue(request: Request) -> list[ProductReviewQueueItem]:
    """Return backend-owned product-facing Review Queue rows."""

    require_permission(request, permission=Permission.RUNS_READ_REVIEW)

    review_store = getattr(request.app.state, "review_store", None)
    if review_store is None:
        raise HTTPException(status_code=404, detail="Review queue not found")

    query_service = ReviewQueryService()
    query_service._review_store = review_store

    return [
        to_product_review_queue_item(row)
        for row in query_service.list_review_queue_rows()
    ]

@router.get("/api/reconciliation/runs/{run_id}/review", response_model=ProductReviewCase)
def get_reconciliation_run_review(run_id: str, request: Request) -> ProductReviewCase:
    require_permission(request, permission=Permission.RUNS_READ_REVIEW)

    review_store = getattr(request.app.state, "review_store", None)
    if review_store is None:
        raise HTTPException(status_code=404, detail="Review case not found")

    query_service = ReviewQueryService()
    query_service._review_store = review_store
    projection = query_service.get_review_case_for_run(run_id)

    if projection is None:
        raise HTTPException(status_code=404, detail="Review case not found")

    return to_product_review_case(projection)


@router.get(
    "/api/review/matches/{match_id}/detail",
    response_model=ProductMatchDetailResponse,
)
def get_match_detail_evidence(match_id: str, request: Request) -> ProductMatchDetailResponse:
    """Return backend-owned product-facing Match Detail / Evidence."""

    review_store = getattr(request.app.state, "review_store", None)
    if review_store is None:
        raise HTTPException(status_code=404, detail="Review case not found")

    query_service = ReviewQueryService()
    query_service._review_store = review_store

    try:
        return read_match_detail_by_id(
            match_id=match_id,
            matches=query_service.list_match_detail_candidates(),
        )
    except MatchDetailReadError as exc:
        raise HTTPException(
            status_code=404 if exc.failure_code.value == "match_not_found" else 422,
            detail=exc.to_failure().model_dump(),
        ) from exc




