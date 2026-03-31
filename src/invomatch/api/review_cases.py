from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from invomatch.api.mappers.product_contract import to_product_review_case
from invomatch.api.product_models.review_case import ProductReviewCase
from invomatch.services.review_queries import ReviewQueryService

router = APIRouter(prefix="/api/reconciliation/runs", tags=["reconciliation-review"])


@router.get("/{run_id}/review", response_model=ProductReviewCase)
def get_reconciliation_run_review(run_id: str, request: Request) -> ProductReviewCase:
    review_store = getattr(request.app.state, "review_store", None)
    if review_store is None:
        raise HTTPException(status_code=404, detail="Review case not found")

    query_service = ReviewQueryService(review_store=review_store)
    projection = query_service.get_review_case_for_run(run_id)

    if projection is None:
        raise HTTPException(status_code=404, detail="Review case not found")

    return to_product_review_case(projection)