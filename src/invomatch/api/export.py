from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from invomatch.api.security import record_privileged_success, require_permission
from invomatch.domain.export import ExportFormat
from invomatch.domain.security import Permission
from invomatch.services.export import (
    ExportDataIncompleteError,
    ExportError,
    RunNotExportableError,
    RunNotFoundError,
    UnsupportedExportFormatError,
)

router = APIRouter(prefix="/api/reconciliation/runs", tags=["reconciliation-export"])


@router.get("/{run_id}/export")
def export_reconciliation_run(
    run_id: str,
    format: str = "json",
    request: Request = None,
):
    principal = require_permission(request, permission=Permission.EXPORTS_DOWNLOAD_DIRECT)

    delivery_service = getattr(request.app.state, "export_delivery_service", None)
    artifact_storage = getattr(request.app.state, "export_artifact_storage", None)

    if delivery_service is None or artifact_storage is None:
        raise HTTPException(
            status_code=500,
            detail="export delivery services are not configured on application state",
        )

    try:
        export_format = _parse_format(format)

        artifact = delivery_service.create_export_artifact(
            run_id=run_id,
            format=export_format.value,
        )

        with artifact_storage.open_read(artifact.storage_key) as handle:
            content = handle.read()

    except UnsupportedExportFormatError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except RunNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    except RunNotExportableError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    except ExportDataIncompleteError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    except ExportError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    record_privileged_success(
        request,
        principal=principal,
        permission=Permission.EXPORTS_DOWNLOAD_DIRECT,
        metadata={"run_id": run_id, "format": export_format.value},
    )

    return Response(
        content=content,
        media_type=artifact.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{artifact.file_name}"'
        },
    )


def _parse_format(value: str) -> ExportFormat:
    normalized = str(value).lower().strip()

    if normalized == "json":
        return ExportFormat.JSON

    if normalized == "csv":
        return ExportFormat.CSV

    raise UnsupportedExportFormatError(
        f"Format '{value}' is not supported. Allowed formats: json, csv."
    )