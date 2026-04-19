from fastapi import APIRouter, Request

router = APIRouter()


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

    if startup_result is None:
        return {
            "status": "ready",
            "startup_scan_failed": False,
            "readiness_reason": "startup_result_unavailable",
            "repairs_applied": 0,
            "unresolved_mismatches": 0,
            "skipped_due_to_active_lease": 0,
            "skipped_due_to_terminal_protection": 0,
        }

    readiness_ok = bool(getattr(startup_result, "readiness_ok", False))

    return {
        "status": "ready" if readiness_ok else "not_ready",
        "startup_scan_failed": bool(getattr(startup_result, "startup_scan_failed", False)),
        "readiness_reason": str(
            getattr(startup_result, "readiness_reason", "unknown")
        ),
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