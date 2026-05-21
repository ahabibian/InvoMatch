
Phase E Match Detail Backend Implementation Start

Mini-EPIC: 33.13.E

Purpose

This document starts the backend implementation phase for the product-facing Match Detail / Evidence read path by inspecting the confirmed target files before code changes are applied.

This is an implementation-start and source-inspection boundary.

This document does not implement backend behavior.

This document does not add an endpoint.

This document does not add a DTO/read model.

This document does not add an adapter/service implementation.

This document does not add contract tests.

This document does not authorize Base44 binding.

This document does not authorize live UI wiring.

This document does not claim Scenario 15 completion.

Starting State

Starting commit subject:

docs(epic-33): confirm match detail backend implementation targets

Starting HEAD:

a714de029324f7590e6b058f589d3e37539ae684

Prior target confirmation:

docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_FILE_TARGET_CONFIRMATION.md

Confirmed Implementation Targets

Route/API target:

src/invomatch/api/review_cases.py

Service/adapter target:

src/invomatch/services/match_detail_read_service.py

DTO/product model target:

src/invomatch/api/product_models/review_case.py

Mapper companion target:

src/invomatch/api/mappers/product_contract.py

Contract test target:

tests/contracts/test_match_detail_evidence_api.py

Target File Existence

Route/API file exists: True

Service/adapter file exists: False

DTO/product model file exists: True

Mapper companion file exists: True

Contract test file exists: False

Implementation Boundary

The implementation must expose backend-owned Match Detail / Evidence as product-facing truth.

The implementation must preserve this path:

Review Queue -> stable match_id -> product-facing Match Detail retrieval -> backend-owned evidence payload -> backend-owned traceability payload -> explicit failure semantics -> UI-displayable response without frontend truth synthesis.

The implementation must remain backend-side only.

The implementation must not create or modify Base44 prompts.

The implementation must not perform live UI wiring.

The implementation must not claim Scenario 15 completion.

Route/API Inspection Signals

C:\dev\InvoMatch\src\invomatch\api\review_cases.py:3: from fastapi import APIRouter, HTTPException, Request
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:5: from invomatch.api.mappers.product_contract import to_product_review_case
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:6: from invomatch.api.product_models.review_case import ProductReviewCase
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:7: from invomatch.api.security import require_permission
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:8: from invomatch.domain.security import Permission
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:9: from invomatch.services.review_queries import ReviewQueryService
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:11: router = APIRouter(prefix="/api/reconciliation/runs", tags=["reconciliation-review"])
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:14: @router.get("/{run_id}/review", response_model=ProductReviewCase)
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:15: def get_reconciliation_run_review(run_id: str, request: Request) -> ProductReviewCase:
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:16: require_permission(request, permission=Permission.RUNS_READ_REVIEW)
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:18: review_store = getattr(request.app.state, "review_store", None)
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:19: if review_store is None:
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:20: raise HTTPException(status_code=404, detail="Review case not found")
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:22: query_service = ReviewQueryService(review_store=review_store)
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:23: projection = query_service.get_review_case_for_run(run_id)
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:26: raise HTTPException(status_code=404, detail="Review case not found")
C:\dev\InvoMatch\src\invomatch\api\review_cases.py:28: return to_product_review_case(projection)

DTO/Product Model Inspection Signals

C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:5: from pydantic import BaseModel, ConfigDict, Field
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:7: from .match_result import ProductMatchExplanation
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:10: class ProductReviewQueueItem(BaseModel):
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:13: case_id: str = Field(..., description="Stable product-facing review case identifier.")
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:15: status: Literal["open", "resolved", "dismissed"] = Field(
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:17: description="Product-facing review case status.",
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:19: reason_code: str = Field(..., description="Reason why this case entered review.")
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:26: class ProductReviewCase(BaseModel):
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:29: case_id: str = Field(..., description="Stable product-facing review case identifier.")
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:31: status: Literal["open", "resolved", "dismissed"] = Field(
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:33: description="Product-facing review case status.",
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:35: reason_code: str = Field(..., description="Reason why this case entered review.")
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:36: match_id: Optional[str] = Field(
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:38: description="Associated product-facing match identifier if present.",
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:40: explanation: list[ProductMatchExplanation] = Field(
C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:42: description="Product-facing explanation for why review is needed.",

Mapper Inspection Signals

C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:6: from invomatch.api.product_models.action import (
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:10: from invomatch.api.product_models.export import ProductExportModel
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:11: from invomatch.api.product_models.export_artifact import (
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:18: from invomatch.api.product_models.match_result import ProductMatchResult
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:19: from invomatch.api.product_models.review_case import ProductReviewCase
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:20: from invomatch.api.product_models.run import (
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:27: def _safe_match_count(run: Any) -> int:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:31: return int(getattr(report, "matched", 0) or 0)
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:34: def _normalize_datetime_for_comparison(value: datetime) -> datetime:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:40: def _is_expired(expires_at: datetime | None) -> bool:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:49: def _to_artifact_lifecycle_state(artifact: Any) -> ArtifactLifecycleState:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:68: def _artifact_download_available(artifact: Any) -> bool:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:69: return _to_artifact_lifecycle_state(artifact) == ArtifactLifecycleState.AVAILABLE
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:72: def _artifact_type(artifact: Any) -> str:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:79: def _artifact_format(artifact: Any) -> str:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:86: def _artifact_file_name(artifact: Any) -> str:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:93: def _artifact_content_type(artifact: Any) -> str:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:100: def _artifact_size_bytes(artifact: Any) -> int:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:105: def to_product_run_summary(run: Any) -> ProductRunSummary:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:111: match_count=_safe_match_count(run),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:112: review_required_count=0,
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:116: def to_product_run_list_response(
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:123: items=[to_product_run_summary(run) for run in runs],
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:130: def to_product_run_detail(run: Any) -> ProductRunDetail:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:136: match_count=_safe_match_count(run),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:137: review_required_count=0,
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:138: matches=[],
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:142: def to_product_match_result(match: Any) -> ProductMatchResult:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:143: return ProductMatchResult(
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:144: match_id=str(getattr(match, "match_id", getattr(match, "id", ""))),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:145: invoice_id=str(getattr(match, "invoice_id", "")),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:146: payment_id=getattr(match, "payment_id", None),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:147: status=str(getattr(match, "status", "unmatched")),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:148: confidence=getattr(match, "confidence", None),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:153: def to_product_review_case(projection: Any) -> ProductReviewCase:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:154: return ProductReviewCase(
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:155: case_id=str(projection.case_id),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:159: match_id=getattr(projection, "match_id", None),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:165: def to_internal_action_command(request: ProductActionRequest) -> dict[str, Any]:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:174: def to_product_action_response(
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:190: def to_product_export_model(export: Any) -> ProductExportModel:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:200: def to_export_artifact_resource(artifact: Any) -> ExportArtifactResource:
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:209: state=_to_artifact_lifecycle_state(artifact),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:216: def to_export_artifact_list_response(
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:231: artifacts=[to_export_artifact_resource(artifact) for artifact in sorted_artifacts],
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:235: def to_export_artifact_metadata_response(
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:239: artifact=to_export_artifact_resource(artifact),
C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:243: def to_artifact_error_response(

Related Review/Match/Product Files

- src/invomatch/api/mappers/product_contract.py
- src/invomatch/api/product_models/match_result.py
- src/invomatch/api/product_models/review_case.py
- src/invomatch/api/product_models/run_view.py
- src/invomatch/api/review_cases.py
- src/invomatch/services/match_record_store.py
- src/invomatch/services/orchestration/review_case_factory.py
- src/invomatch/services/orchestration/review_case_generation_service.py
- src/invomatch/services/orchestration/review_integration_service.py
- src/invomatch/services/review_service.py
- src/invomatch/services/run_view_query_service.py
- src/invomatch/services/sqlite_match_record_store.py
- tests/contracts/test_product_contract_actions.py
- tests/contracts/test_product_contract_ingest_run.py
- tests/contracts/test_product_contract_input_boundary.py
- tests/contracts/test_product_contract_review.py
- tests/contracts/test_product_contract_runs.py
- tests/services/test_sqlite_match_record_store.py
- tests/test_restart_app_review_run_view_integrity.py
- tests/test_restart_run_view_consistency.py
- tests/test_review_case_factory.py
- tests/test_review_case_generation_service.py
- tests/test_review_integration_service.py
- tests/test_review_service.py
- tests/test_review_service_store_integration.py
- tests/test_run_view_api.py
- tests/test_run_view_contract.py
- tests/test_run_view_dependency_degradation.py
- tests/test_run_view_export_consistency_integration.py
- tests/test_run_view_projection_resilience.py
- tests/test_run_view_query_service.py


Related Review/Match/Product Test Files

- tests/audit/test_audit_api.py
- tests/contracts/conftest.py
- tests/contracts/test_internal_field_leakage.py
- tests/contracts/test_product_contract_actions.py
- tests/contracts/test_product_contract_ingest_run.py
- tests/contracts/test_product_contract_input_boundary.py
- tests/contracts/test_product_contract_review.py
- tests/contracts/test_product_contract_runs.py
- tests/operational/test_operations_metrics_api.py
- tests/services/test_reconciliation_match_persistence.py
- tests/services/test_sqlite_match_record_store.py
- tests/system/test_review_required_taxonomy_alignment.py
- tests/system/test_review_resolution_flow.py
- tests/test_actions/test_resolve_review.py
- tests/test_actions/test_resolve_review_conflicts.py
- tests/test_actions_api.py
- tests/test_auth_session_api.py
- tests/test_export_api.py
- tests/test_export_artifact_api.py
- tests/test_finalized_projection_no_review.py
- tests/test_ingestion_run_api.py
- tests/test_input_boundary_api.py
- tests/test_match_decision_models.py
- tests/test_match_features.py
- tests/test_match_rules.py
- tests/test_match_taxonomy_and_explanations.py
- tests/test_matching_engine.py
- tests/test_reconciliation_runs_api.py
- tests/test_restart_app_review_run_view_integrity.py
- tests/test_restart_review_persistence_integrity.py
- tests/test_review_api.py
- tests/test_review_case_factory.py
- tests/test_review_case_generation_service.py
- tests/test_review_integration_service.py
- tests/test_review_requirement_evaluator.py
- tests/test_review_resolution_coordinator.py
- tests/test_review_service.py
- tests/test_review_service_store_integration.py
- tests/test_run_view_api.py
- tests/test_sqlite_review_store.py


Route/API File Preview

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from invomatch.api.mappers.product_contract import to_product_review_case
from invomatch.api.product_models.review_case import ProductReviewCase
from invomatch.api.security import require_permission
from invomatch.domain.security import Permission
from invomatch.services.review_queries import ReviewQueryService

router = APIRouter(prefix="/api/reconciliation/runs", tags=["reconciliation-review"])


@router.get("/{run_id}/review", response_model=ProductReviewCase)
def get_reconciliation_run_review(run_id: str, request: Request) -> ProductReviewCase:
    require_permission(request, permission=Permission.RUNS_READ_REVIEW)

    review_store = getattr(request.app.state, "review_store", None)
    if review_store is None:
        raise HTTPException(status_code=404, detail="Review case not found")

    query_service = ReviewQueryService(review_store=review_store)
    projection = query_service.get_review_case_for_run(run_id)

    if projection is None:
        raise HTTPException(status_code=404, detail="Review case not found")

    return to_product_review_case(projection)

DTO/Product Model File Preview

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .match_result import ProductMatchExplanation


class ProductReviewQueueItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(..., description="Stable product-facing review case identifier.")
    run_id: str = Field(..., description="Associated product-facing run identifier.")
    status: Literal["open", "resolved", "dismissed"] = Field(
        ...,
        description="Product-facing review case status.",
    )
    reason_code: str = Field(..., description="Reason why this case entered review.")
    priority: Optional[str] = Field(
        default=None,
        description="Optional product-facing priority label.",
    )


class ProductReviewCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str = Field(..., description="Stable product-facing review case identifier.")
    run_id: str = Field(..., description="Associated product-facing run identifier.")
    status: Literal["open", "resolved", "dismissed"] = Field(
        ...,
        description="Product-facing review case status.",
    )
    reason_code: str = Field(..., description="Reason why this case entered review.")
    match_id: Optional[str] = Field(
        default=None,
        description="Associated product-facing match identifier if present.",
    )
    explanation: list[ProductMatchExplanation] = Field(
        default_factory=list,
        description="Product-facing explanation for why review is needed.",
    )
    recommended_action: Optional[str] = Field(
        default=None,
        description="Optional suggested product-facing user action.",
    )

Mapper Companion File Preview

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

Service/Adapter File Preview

File does not exist yet.

Contract Test File Preview

File does not exist yet.

Implementation Patch Plan for Next Step

The next step may apply backend code changes only after this inspection is committed.

The next patch should be limited to:

add Match Detail / Evidence DTOs to the confirmed DTO/product model file
add a narrowly scoped backend service/adapter in the confirmed service file
add a match_id-based route in the confirmed route/API file
add dedicated contract tests in the confirmed contract test file
use the mapper companion only if existing product-contract conventions require it

The next patch must not:

implement frontend truth synthesis
create Base44 prompts
wire live UI
claim Scenario 15 completion
mix action execution with Match Detail read-path retrieval
make API route code own evidence or traceability truth assembly
Explicit Non-Actions

No endpoint was implemented.

No DTO/read model was implemented.

No adapter/service implementation was added.

No contract tests were added.

No Base44 prompt was created.

No live UI wiring was performed.

No Scenario 15 completion claim was made.

No frontend truth synthesis was authorized.
