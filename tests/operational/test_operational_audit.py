from invomatch.domain.operational.models import (
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
)
from invomatch.services.operational.operational_audit import (
    InMemoryOperationalAuditRepository,
    OperationalAuditService,
    OperationalAuditWrite,
)


def test_operational_audit_service_records_structured_event() -> None:
    repository = InMemoryOperationalAuditRepository()
    service = OperationalAuditService(repository)

    event = service.record(
        OperationalAuditWrite(
            run_id="run-1",
            event_type="retry_triggered",
            decision=OperationalDecision.RETRY_TRIGGERED,
            reason_code=OperationalReasonCode.RECOVERABLE_FAILURE,
            previous_operational_state=OperationalCondition.HEALTHY,
            new_operational_state=OperationalCondition.RETRY_PENDING,
            related_failure_code="runtime_error",
            attempt_number=2,
            correlation_id="corr-1",
            reason_detail="retry approved by policy",
            metadata={"source": "recovery_loop"},
        )
    )

    events = repository.list_events()

    assert len(events) == 1
    assert events[0] == event
    assert event.run_id == "run-1"
    assert event.event_type == "retry_triggered"
    assert event.decision == OperationalDecision.RETRY_TRIGGERED
    assert event.reason_code == OperationalReasonCode.RECOVERABLE_FAILURE
    assert event.related_failure_code == "runtime_error"
    assert event.attempt_number == 2
    assert event.metadata["source"] == "recovery_loop"
    assert event.event_id