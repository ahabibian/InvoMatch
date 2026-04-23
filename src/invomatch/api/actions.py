from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response, status

from invomatch.api.mappers.product_contract import to_product_action_response
from invomatch.api.product_models.action import (
    ProductActionRequest,
    ProductActionResponse,
)
from invomatch.api.security import record_privileged_success, require_permission
from invomatch.domain.security import Permission
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


def _permission_for_action_type(action_type: str) -> Permission:
    normalized = str(action_type).strip().lower()

    if normalized == "resolve_review":
        return Permission.ACTIONS_RESOLVE_REVIEW

    if normalized == "export_run":
        return Permission.ACTIONS_EXPORT_RUN

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Unsupported action type: {action_type}",
    )


@router.post("/{run_id}/actions", response_model=ProductActionResponse)
def post_reconciliation_run_action(
    run_id: str,
    request_body: ProductActionRequest,
    request: Request,
    response: Response = None,
) -> ProductActionResponse:
    permission = _permission_for_action_type(str(request_body.action_type))
    principal = require_permission(request, permission=permission)

    action_service = _resolve_action_service(request)

    result = action_service.execute(
        run_id=run_id,
        request=request_body,
        principal=principal,
    )

    if response is not None:
        response.status_code = _http_status_for_action_result(result)

    if result.accepted:
        record_privileged_success(
            request,
            principal=principal,
            permission=permission,
            metadata={
                "run_id": run_id,
                "action_type": str(request_body.action_type),
            },
        )

    return to_product_action_response(
        run_id,
        request_body,
        result.accepted,
        result.status,
        message=result.message,
    )