from __future__ import annotations

from fastapi import APIRouter, Request

from invomatch.api.product_models.input_boundary import (
    ProductInputSubmissionResponse,
    ProductInputError,
)


router = APIRouter(prefix="/api/reconciliation/input", tags=["input-boundary"])


def _map_errors(errors):
    return [
        ProductInputError(
            type=e.type,
            code=e.code,
            message=e.message,
            field=e.field,
        )
        for e in errors
    ]


@router.post("/json", response_model=ProductInputSubmissionResponse)
async def submit_json(request: Request):
    payload = await request.json()

    service = request.app.state.input_processing_service

    session = service.process_json(payload)

    return ProductInputSubmissionResponse(
        input_id=session.input_id,
        status=session.status,
        ingestion_batch_id=session.ingestion_batch_id,
        run_id=session.run_id,
        errors=_map_errors(session.validation_errors),
    )