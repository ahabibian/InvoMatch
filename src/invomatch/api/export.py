from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from invomatch.domain.export import ExportFormat
from invomatch.services.export import (
    ExportDataIncompleteError,
    ExportError,
    ExportService,
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
    export_service = getattr(request.app.state, "export_service", None)
    if export_service is None:
        raise HTTPException(
            status_code=500,
            detail="export_service is not configured on application state",
        )

    try:
        export_format = _parse_format(format)

        result = export_service.export(
            run_id=run_id,
            export_format=export_format,
        )

        return Response(
            content=result.content,
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"'
            },
        )

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


def _parse_format(value: str) -> ExportFormat:
    normalized = str(value).lower().strip()

    if normalized == "json":
        return ExportFormat.JSON

    if normalized == "csv":
        return ExportFormat.CSV

    raise UnsupportedExportFormatError(
        f"Format '{value}' is not supported. Allowed formats: json, csv."
    )
