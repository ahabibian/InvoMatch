from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import logging
import os
from pathlib import Path
import sqlite3

router = APIRouter()
logger = logging.getLogger(__name__)


def _dependency_errors(request: Request) -> list[str]:
    settings = getattr(request.app.state, "application_settings", None)
    if settings is None:
        return ["application_settings_unavailable"]

    errors: list[str] = []
    sqlite_paths = [
        settings.persistence.audit_event_db_path,
        settings.persistence.input_session_db_path,
    ]
    if settings.persistence.run_store_backend.strip().lower() == "sqlite":
        sqlite_paths.append(settings.persistence.run_store_path)
    if settings.persistence.review_store_backend.strip().lower() == "sqlite":
        sqlite_paths.append(settings.persistence.review_store_path)
    for database_path in sqlite_paths:
        path = Path(database_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(path) as connection:
                connection.execute("SELECT 1")
        except (OSError, sqlite3.Error):
            errors.append(f"sqlite_unavailable:{path.name}")

    storage = settings.storage
    for directory in (
        storage.artifact_root_path,
        storage.export_directory,
        storage.upload_root_path,
        storage.temp_directory,
        storage.log_directory,
    ):
        path = Path(directory)
        if not path.is_dir() or not os.access(path, os.W_OK):
            errors.append(f"storage_unwritable:{path.name}")
    return errors


@router.get("/health")
def health(request: Request):
    startup_result = getattr(request.app.state, "startup_repair_result", None)

    if startup_result is None:
        return {
            "status": "ok",
            "startup_scan_failed": False,
            "readiness_ok": True,
            "readiness_reason": "startup_result_unavailable",
        }

    return {
        "status": "ok",
        "startup_scan_failed": bool(getattr(startup_result, "startup_scan_failed", False)),
        "readiness_ok": bool(getattr(startup_result, "readiness_ok", True)),
        "readiness_reason": str(
            getattr(startup_result, "readiness_reason", "unknown")
        ),
    }


@router.get("/readiness")
def readiness(request: Request):
    startup_result = getattr(request.app.state, "startup_repair_result", None)
    dependency_errors = _dependency_errors(request)

    if startup_result is None:
        payload = {
            "status": "not_ready",
            "startup_scan_failed": False,
            "readiness_reason": "startup_result_unavailable",
            "dependency_errors": dependency_errors,
            "repairs_applied": 0,
            "unresolved_mismatches": 0,
            "skipped_due_to_active_lease": 0,
            "skipped_due_to_terminal_protection": 0,
        }
        logger.warning("Readiness failed reason=startup_result_unavailable")
        return JSONResponse(status_code=503, content=payload)

    readiness_ok = bool(getattr(startup_result, "readiness_ok", False)) and not dependency_errors

    payload = {
        "status": "ready" if readiness_ok else "not_ready",
        "startup_scan_failed": bool(getattr(startup_result, "startup_scan_failed", False)),
        "readiness_reason": str(
            "dependency_unavailable"
            if dependency_errors
            else getattr(startup_result, "readiness_reason", "unknown")
        ),
        "dependency_errors": dependency_errors,
        "repairs_applied": int(getattr(startup_result, "repairs_applied", 0)),
        "unresolved_mismatches": int(
            getattr(startup_result, "unresolved_mismatches", 0)
        ),
        "skipped_due_to_active_lease": int(
            getattr(startup_result, "skipped_due_to_active_lease", 0)
        ),
        "skipped_due_to_terminal_protection": int(
            getattr(startup_result, "skipped_due_to_terminal_protection", 0)
        ),
    }
    if not readiness_ok:
        logger.warning(
            "Readiness failed reason=%s dependencies=%s",
            payload["readiness_reason"],
            ",".join(dependency_errors) or "none",
        )
    return JSONResponse(status_code=200 if readiness_ok else 503, content=payload)
