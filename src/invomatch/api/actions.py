from __future__ import annotations

from fastapi import APIRouter, Request

from invomatch.api.mappers.product_contract import (
    to_internal_action_command,
    to_product_action_response,
)
from invomatch.api.product_models.action import (
    ProductActionRequest,
    ProductActionResponse,
)
from invomatch.services.action_service import ActionService

router = APIRouter(prefix="/api/reconciliation/runs", tags=["reconciliation-actions"])


@router.post("/{run_id}/actions", response_model=ProductActionResponse)
def post_reconciliation_run_action(
    run_id: str,
    request_body: ProductActionRequest,
    request: Request,
) -> ProductActionResponse:
    action_service = getattr(request.app.state, "action_service", None)
    if action_service is None:
        action_service = ActionService()

    internal_command = to_internal_action_command(request_body)
    result = action_service.execute(
        run_id=run_id,
        request=request_body,
    )

    return to_product_action_response(
        run_id=result.run_id,
        request=request_body,
        accepted=result.accepted,
        status=result.status,
        message=result.message,
    )