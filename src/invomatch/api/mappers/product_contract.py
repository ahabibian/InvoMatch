from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from invomatch.api.product_models.action import (
    ProductActionRequest,
    ProductActionResponse,
)
from invomatch.api.product_models.export import ProductExportModel
from invomatch.api.product_models.export_artifact import (
    ArtifactErrorResponse,
    ArtifactLifecycleState,
    ExportArtifactListResponse,
    ExportArtifactMetadataResponse,
    ExportArtifactResource,
)
from invomatch.api.product_models.match_result import ProductMatchResult
from invomatch.api.product_models.review_case import ProductReviewCase
from invomatch.api.product_models.run import (
    ProductRunDetail,
    ProductRunListResponse,
    ProductRunSummary,
)


def _safe_match_count(run: Any) -> int:
    report = getattr(run, "report", None)
    if report is None:
        return 0
    return int(getattr(report, "matched", 0) or 0)


def _normalize_datetime_for_comparison(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _is_expired(expires_at: datetime | None) -> bool:
    if expires_at is None:
        return False

    normalized_expires_at = _normalize_datetime_for_comparison(expires_at)
    now_utc = datetime.now(timezone.utc)
    return normalized_expires_at <= now_utc


def _to_artifact_lifecycle_state(artifact: Any) -> ArtifactLifecycleState:
    raw_status = str(getattr(artifact, "status", "") or "").strip().lower()
    expires_at = getattr(artifact, "expires_at", None)

    failed_statuses = {"failed", "error"}
    deleted_statuses = {"deleted", "removed"}

    if raw_status in failed_statuses:
        return ArtifactLifecycleState.FAILED

    if raw_status in deleted_statuses:
        return ArtifactLifecycleState.DELETED

    if _is_expired(expires_at):
        return ArtifactLifecycleState.EXPIRED

    return ArtifactLifecycleState.AVAILABLE


def _artifact_download_available(artifact: Any) -> bool:
    return _to_artifact_lifecycle_state(artifact) == ArtifactLifecycleState.AVAILABLE


def _artifact_type(artifact: Any) -> str:
    value = getattr(artifact, "artifact_type", None)
    if value:
        return str(value)
    return "run_export"


def _artifact_format(artifact: Any) -> str:
    value = getattr(artifact, "format", None)
    if value:
        return str(value)
    return "unknown"


def _artifact_file_name(artifact: Any) -> str:
    value = getattr(artifact, "file_name", None)
    if value:
        return str(value)
    return "artifact"


def _artifact_content_type(artifact: Any) -> str:
    value = getattr(artifact, "content_type", None)
    if value:
        return str(value)
    return "application/octet-stream"


def _artifact_size_bytes(artifact: Any) -> int:
    value = getattr(artifact, "byte_size", getattr(artifact, "size_bytes", 0))
    return int(value or 0)


def to_product_run_summary(run: Any) -> ProductRunSummary:
    return ProductRunSummary(
        run_id=str(run.run_id),
        status=str(run.status),
        created_at=run.created_at,
        updated_at=getattr(run, "updated_at", None),
        match_count=_safe_match_count(run),
        review_required_count=0,
    )


def to_product_run_list_response(
    runs: Iterable[Any],
    total: int,
    limit: int,
    offset: int,
) -> ProductRunListResponse:
    return ProductRunListResponse(
        items=[to_product_run_summary(run) for run in runs],
        total=int(total),
        limit=int(limit),
        offset=int(offset),
    )


def to_product_run_detail(run: Any) -> ProductRunDetail:
    return ProductRunDetail(
        run_id=str(run.run_id),
        status=str(run.status),
        created_at=run.created_at,
        updated_at=getattr(run, "updated_at", None),
        match_count=_safe_match_count(run),
        review_required_count=0,
        matches=[],
    )


def to_product_match_result(match: Any) -> ProductMatchResult:
    return ProductMatchResult(
        match_id=str(getattr(match, "match_id", getattr(match, "id", ""))),
        invoice_id=str(getattr(match, "invoice_id", "")),
        payment_id=getattr(match, "payment_id", None),
        status=str(getattr(match, "status", "unmatched")),
        confidence=getattr(match, "confidence", None),
        explanation=[],
    )


def to_product_review_case(projection: Any) -> ProductReviewCase:
    return ProductReviewCase(
        case_id=str(projection.case_id),
        run_id=str(projection.run_id),
        status=str(projection.status),
        reason_code=str(projection.reason_code),
        match_id=getattr(projection, "match_id", None),
        explanation=[],
        recommended_action=getattr(projection, "recommended_action", None),
    )


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


def to_product_export_model(export: Any) -> ProductExportModel:
    return ProductExportModel(
        run_id=str(export.run_id),
        export_status=str(getattr(export, "status", "not_ready")),
        export_format=str(getattr(export, "format", "json")),
        download_url=getattr(export, "download_url", None),
        generated_at=getattr(export, "generated_at", None),
    )


def to_export_artifact_resource(artifact: Any) -> ExportArtifactResource:
    return ExportArtifactResource(
        artifact_id=str(getattr(artifact, "id")),
        run_id=str(getattr(artifact, "run_id")),
        artifact_type=_artifact_type(artifact),
        format=_artifact_format(artifact),
        file_name=_artifact_file_name(artifact),
        content_type=_artifact_content_type(artifact),
        size_bytes=_artifact_size_bytes(artifact),
        state=_to_artifact_lifecycle_state(artifact),
        created_at=getattr(artifact, "created_at"),
        expires_at=getattr(artifact, "expires_at", None),
        download_available=_artifact_download_available(artifact),
    )


def to_export_artifact_list_response(
    run_id: str,
    artifacts: Iterable[Any],
) -> ExportArtifactListResponse:
    sorted_artifacts = sorted(
        list(artifacts),
        key=lambda artifact: (
            getattr(artifact, "created_at", datetime.min.replace(tzinfo=timezone.utc)),
            str(getattr(artifact, "id", "")),
        ),
        reverse=True,
    )

    return ExportArtifactListResponse(
        run_id=str(run_id),
        artifacts=[to_export_artifact_resource(artifact) for artifact in sorted_artifacts],
    )


def to_export_artifact_metadata_response(
    artifact: Any,
) -> ExportArtifactMetadataResponse:
    return ExportArtifactMetadataResponse(
        artifact=to_export_artifact_resource(artifact),
    )


def to_artifact_error_response(
    code: str,
    message: str,
) -> ArtifactErrorResponse:
    return ArtifactErrorResponse(
        code=code,
        message=message,
    )