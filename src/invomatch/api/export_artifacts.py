from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from invomatch.api.mappers.product_contract import (
    to_artifact_error_response,
    to_export_artifact_list_response,
    to_export_artifact_metadata_response,
)
from invomatch.api.product_models.export_artifact import (
    ArtifactErrorResponse,
    ExportArtifactListResponse,
    ExportArtifactMetadataResponse,
)
from invomatch.services.artifact_query_service import (
    ArtifactNotFoundError,
    ArtifactQueryService,
)
from invomatch.services.run_registry import RunRegistry

router = APIRouter(prefix="/api/reconciliation", tags=["export-artifacts"])


@router.get(
    "/runs/{run_id}/exports",
    response_model=ExportArtifactListResponse,
    responses={
        404: {"model": ArtifactErrorResponse},
        500: {"model": ArtifactErrorResponse},
    },
)
def list_run_export_artifacts(run_id: str, request: Request) -> ExportArtifactListResponse:
    run_registry: RunRegistry = request.app.state.run_registry
    run = run_registry.get_run(run_id)
    if run is None:
        error = to_artifact_error_response(
            code="run_not_found",
            message="Reconciliation run not found",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.model_dump(exclude_none=True),
        )

    query_service: ArtifactQueryService = request.app.state.artifact_query_service

    try:
        artifacts = query_service.list_artifacts_for_run(run_id)
    except Exception as exc:
        error = to_artifact_error_response(
            code="artifact_unavailable",
            message="Unable to list export artifacts",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(exclude_none=True),
        ) from exc

    return to_export_artifact_list_response(
        run_id=run_id,
        artifacts=artifacts,
    )


@router.get(
    "/exports/{artifact_id}",
    response_model=ExportArtifactMetadataResponse,
    responses={
        404: {"model": ArtifactErrorResponse},
        500: {"model": ArtifactErrorResponse},
    },
)
def get_export_artifact_metadata(
    artifact_id: str,
    request: Request,
) -> ExportArtifactMetadataResponse:
    query_service: ArtifactQueryService = request.app.state.artifact_query_service

    try:
        artifact = query_service.get_artifact_by_id(artifact_id)
    except ArtifactNotFoundError as exc:
        error = to_artifact_error_response(
            code="artifact_not_found",
            message="Export artifact not found",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.model_dump(exclude_none=True),
        ) from exc
    except Exception as exc:
        error = to_artifact_error_response(
            code="artifact_unavailable",
            message="Unable to retrieve export artifact metadata",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.model_dump(exclude_none=True),
        ) from exc

    return to_export_artifact_metadata_response(artifact)