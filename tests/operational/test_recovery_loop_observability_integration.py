from invomatch.domain.operational.models import OperationalDecision
from invomatch.services.operational.operational_audit import (
    InMemoryOperationalAuditRepository,
    OperationalAuditService,
)
from invomatch.services.operational.operational_metrics import (
    InMemoryOperationalMetricsStore,
    OperationalMetricsService,
)
from invomatch.services.operational.recovery_eligibility_policy import (
    RecoveryEligibilityInput,
)
from invomatch.services.operational.recovery_loop_service import (
    RecoveryCandidate,
    RecoveryLoopService,
)


def test_recovery_loop_emits_audit_and_metrics_for_retry() -> None:
    audit_repository = InMemoryOperationalAuditRepository()
    audit_service = OperationalAuditService(audit_repository)

    metrics_store = InMemoryOperationalMetricsStore()
    metrics_service = OperationalMetricsService(metrics_store)

    calls: list[str] = []

    service = RecoveryLoopService(
        retry_executor=lambda run_id: calls.append(run_id),
        audit_service=audit_service,
        metrics_service=metrics_service,
    )

    result = service.process(
        RecoveryCandidate(
            run_id="run-1",
            incident_key="incident-1",
            eligibility=RecoveryEligibilityInput(
                business_status="failed",
                retry_count=0,
                retry_limit=3,
                failure_code="runtime_error",
                failure_is_recoverable=True,
            ),
        )
    )

    snapshot = metrics_service.snapshot()
    events = audit_repository.list_events()

    assert result.decision == OperationalDecision.RETRY_TRIGGERED
    assert calls == ["run-1"]

    assert snapshot.counters["recovery_attempts_total"] == 1
    assert snapshot.counters["retries_triggered_total"] == 1
    assert snapshot.counters["recovery_action_taken_total"] == 1

    assert len(events) == 1
    assert events[0].run_id == "run-1"
    assert events[0].event_type == "retry_triggered"
    assert events[0].correlation_id == "incident-1"
    assert events[0].metadata["action_taken"] == "true"
    assert events[0].metadata["action_name"] == "retry"