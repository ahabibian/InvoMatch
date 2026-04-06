from __future__ import annotations

from fastapi import APIRouter, Request, Response, status

from invomatch.api.mappers.product_contract import to_product_action_response
from invomatch.api.product_models.action import (
    ProductActionRequest,
    ProductActionResponse,
)
from invomatch.services.action_service import (
    ActionExecutionResult,
    ActionService,
)

router = APIRouter(prefix="/api/reconciliation/runs", tags=["reconciliation-actions"])


def _http_status_for_action_result(result: ActionExecutionResult) -> int:
    if result.status == "accepted":
        return status.HTTP_200_OK
    if result.status == "not_found":
        return status.HTTP_404_NOT_FOUND
    if result.status in {"invalid_request", "unsupported_action"}:
        return status.HTTP_400_BAD_REQUEST
    if result.status == "conflict":
        return status.HTTP_409_CONFLICT
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def _resolve_action_service(request: Request) -> ActionService:
    existing = getattr(request.app.state, "action_service", None)
    if existing is not None:
        return existing

    return ActionService(
        run_store=getattr(request.app.state, "run_store", None),
        review_store=getattr(request.app.state, "review_store", None),
    )


@router.post("/{run_id}/actions", response_model=ProductActionResponse)
def post_reconciliation_run_action(
    run_id: str,
    request_body: ProductActionRequest,
    request: Request,
    response: Response = None,
) -> ProductActionResponse:
    action_service = _resolve_action_service(request)

    result = action_service.execute(
        run_id=run_id,
        request=request_body,
    )

    if response is not None:
        response.status_code = _http_status_for_action_result(result)

    return to_product_action_response(
        run_id,
        request_body,
        result.accepted,
        result.status,
        message=result.message,
    )