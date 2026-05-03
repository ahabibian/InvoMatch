from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from invomatch.api.security import require_permission
from invomatch.domain.security import Permission
from invomatch.services.operational.condition_detector import (
    OperationalConditionDetector,
)

router = APIRouter(prefix="/api/operations", tags=["operations"])


def _get_metrics_snapshot(request: Request):
    metrics_service = getattr(request.app.state, "operational_metrics_service", None)
    if metrics_service is None:
        raise HTTPException(
            status_code=500,
            detail="operational metrics service is not configured",
        )

    return metrics_service.snapshot()


def _build_condition_detector(request: Request) -> OperationalConditionDetector:
    detector = getattr(request.app.state, "operational_condition_detector", None)
    if detector is not None:
        return detector

    return OperationalConditionDetector()


@router.get("/metrics")
def get_operational_metrics(request: Request) -> dict[str, Any]:
    require_permission(request, permission=Permission.OPERATIONS_VIEW_METRICS)

    snapshot = _get_metrics_snapshot(request)

    counters = dict(getattr(snapshot, "counters", {}) or {})
    decision_counts = dict(getattr(snapshot, "decision_counts", {}) or {})
    reason_counts = dict(getattr(snapshot, "reason_counts", {}) or {})

    condition = _build_condition_detector(request).evaluate(counters=counters)

    return {
        "status": condition.status,
        "generated_at": condition.generated_at,
        "signals": condition.signals,
        "counters": counters,
        "decision_counts": decision_counts,
        "reason_counts": reason_counts,
    }


@router.get("/health-summary")
def get_operational_health_summary(request: Request) -> dict[str, Any]:
    require_permission(request, permission=Permission.OPERATIONS_VIEW_METRICS)

    snapshot = _get_metrics_snapshot(request)
    counters = dict(getattr(snapshot, "counters", {}) or {})

    condition = _build_condition_detector(request).evaluate(counters=counters)

    return {
        "status": condition.status,
        "generated_at": condition.generated_at,
        "summary": condition.summary,
        "signals": condition.signals,
        "recommended_action": condition.recommended_action,
    }
