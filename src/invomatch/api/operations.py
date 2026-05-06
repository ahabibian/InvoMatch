from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from invomatch.api.security import require_permission
from invomatch.api.operations_models import (
    OperationalAlertsResponse,
    OperationalHealthSummaryResponse,
    OperationalMetricsResponse,
    OperationalReleaseIdentityResponse,
)
from invomatch.domain.security import Permission
from invomatch.services.operational.alert_policy import OperationalAlertPolicy
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

def _build_alert_policy(request: Request) -> OperationalAlertPolicy:
    policy = getattr(request.app.state, "operational_alert_policy", None)
    if policy is not None:
        return policy

    return OperationalAlertPolicy()


@router.get("/metrics", response_model=OperationalMetricsResponse)
def get_operational_metrics(request: Request) -> OperationalMetricsResponse:
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


@router.get("/health-summary", response_model=OperationalHealthSummaryResponse)
def get_operational_health_summary(request: Request) -> OperationalHealthSummaryResponse:
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

@router.get("/alerts", response_model=OperationalAlertsResponse)
def get_operational_alerts(request: Request) -> OperationalAlertsResponse:
    require_permission(request, permission=Permission.OPERATIONS_VIEW_METRICS)

    snapshot = _get_metrics_snapshot(request)
    counters = dict(getattr(snapshot, "counters", {}) or {})

    condition = _build_condition_detector(request).evaluate(counters=counters)
    alert_snapshot = _build_alert_policy(request).evaluate(signals=condition.signals)

    return {
        "status": alert_snapshot.status,
        "generated_at": alert_snapshot.generated_at,
        "alerts": [
            {
                "code": alert.code,
                "severity": alert.severity,
                "message": alert.message,
                "recommended_action": alert.recommended_action,
                "signal": alert.signal,
                "value": alert.value,
            }
            for alert in alert_snapshot.alerts
        ],
    }

@router.get("/release-identity", response_model=OperationalReleaseIdentityResponse)
def get_operational_release_identity(request: Request) -> OperationalReleaseIdentityResponse:
    require_permission(request, permission=Permission.OPERATIONS_VIEW_METRICS)

    release_identity_service = getattr(request.app.state, "release_identity_service", None)
    if release_identity_service is None:
        raise HTTPException(
            status_code=500,
            detail="release identity service is not configured",
        )

    identity = release_identity_service.get_release_identity()

    return {
        "application_name": identity.application_name,
        "application_version": identity.application_version,
        "git_commit_sha": identity.git_commit_sha,
        "git_branch": identity.git_branch,
        "build_timestamp_utc": identity.build_timestamp_utc,
        "environment": identity.environment,
        "validation_status": identity.validation_status,
        "metadata_available": identity.metadata_available,
    }
