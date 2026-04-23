from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, File, HTTPException, Request, UploadFile

from invomatch.api.product_models.input_boundary import (
    ProductInputError,
    ProductInputSessionView,
    ProductInputSubmissionResponse,
)
from invomatch.api.security import record_privileged_success, require_permission
from invomatch.domain.security import Permission

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
    principal = require_permission(request, permission=Permission.INPUT_SUBMIT)

    service = request.app.state.input_processing_service
    session = service.process_json(payload)

    record_privileged_success(
        request,
        principal=principal,
        permission=Permission.INPUT_SUBMIT,
        metadata={
            "input_type": "json",
            "input_id": session.input_id,
            "run_id": session.run_id,
        },
    )

    return ProductInputSubmissionResponse(
        input_id=session.input_id,
        status=session.status,
        ingestion_batch_id=session.ingestion_batch_id,
        run_id=session.run_id,
        errors=_map_errors(session.validation_errors),
    )


@router.post("/file", response_model=ProductInputSubmissionResponse)
async def submit_file(request: Request, file: UploadFile = File(...)):
    principal = require_permission(request, permission=Permission.INPUT_SUBMIT)

    service = request.app.state.input_processing_service
    content = await file.read()

    session = service.process_file(
        filename=file.filename,
        content_type=file.content_type,
        content_bytes=content,
    )

    record_privileged_success(
        request,
        principal=principal,
        permission=Permission.INPUT_SUBMIT,
        metadata={
            "input_type": "file",
            "input_id": session.input_id,
            "run_id": session.run_id,
            "source_filename": file.filename,
        },
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
    require_permission(request, permission=Permission.INPUT_VIEW)

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