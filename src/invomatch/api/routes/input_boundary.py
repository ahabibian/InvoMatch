from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, File, HTTPException, Request, UploadFile

from invomatch.api.product_models.input_boundary import (
    ProductInputError,
    ProductInputSessionView,
    ProductInputSubmissionResponse,
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
async def submit_json(
    request: Request,
    payload: dict[str, Any] = Body(...),
):
    service = request.app.state.input_processing_service
    session = service.process_json(payload)

    return ProductInputSubmissionResponse(
        input_id=session.input_id,
        status=session.status,
        ingestion_batch_id=session.ingestion_batch_id,
        run_id=session.run_id,
        errors=_map_errors(session.validation_errors),
    )


@router.post("/file", response_model=ProductInputSubmissionResponse)
async def submit_file(request: Request, file: UploadFile = File(...)):
    service = request.app.state.input_processing_service
    content = await file.read()

    session = service.process_file(
        filename=file.filename,
        content_type=file.content_type,
        content_bytes=content,
    )

    return ProductInputSubmissionResponse(
        input_id=session.input_id,
        status=session.status,
        ingestion_batch_id=session.ingestion_batch_id,
        run_id=session.run_id,
        errors=_map_errors(session.validation_errors),
    )


@router.get("/{input_id}", response_model=ProductInputSessionView)
async def get_input_session(input_id: str, request: Request):
    repository = request.app.state.input_session_repository
    session = repository.get_by_input_id(input_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Input session not found")

    return ProductInputSessionView(
        input_id=session.input_id,
        input_type=session.input_type,
        status=session.status,
        source_filename=session.source_filename,
        source_size_bytes=session.source_size_bytes,
        ingestion_batch_id=session.ingestion_batch_id,
        run_id=session.run_id,
        errors=_map_errors(session.validation_errors),
        created_at=session.created_at,
        updated_at=session.updated_at,
    )