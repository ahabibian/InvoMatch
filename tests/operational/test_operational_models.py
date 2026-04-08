from datetime import datetime, timezone

from invomatch.domain.operational.models import (
    OperationalActorType,
    OperationalAuditEvent,
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
    RunOperationalMetadata,
)


def test_run_operational_metadata_defaults_to_healthy() -> None:
    metadata = RunOperationalMetadata()

    assert metadata.condition == OperationalCondition.HEALTHY
    assert metadata.retry_count == 0
    assert metadata.retry_budget_remaining == 0
    assert metadata.last_failure_code is None


def test_operational_audit_event_preserves_structured_fields() -> None:
    now = datetime.now(timezone.utc)

    event = OperationalAuditEvent(
        event_id="evt-1",
        run_id="run-1",
        event_type="retry_triggered",
        event_time=now,
        actor_type=OperationalActorType.SYSTEM,
        decision=OperationalDecision.RETRY_TRIGGERED,
        reason_code=OperationalReasonCode.RECOVERABLE_FAILURE,
        previous_operational_state=OperationalCondition.HEALTHY,
        new_operational_state=OperationalCondition.RETRY_PENDING,
        attempt_number=2,
        metadata={"failure_code": "runtime_error"},
    )

    assert event.event_id == "evt-1"
    assert event.actor_type == OperationalActorType.SYSTEM
    assert event.decision == OperationalDecision.RETRY_TRIGGERED
    assert event.reason_code == OperationalReasonCode.RECOVERABLE_FAILURE
    assert event.metadata["failure_code"] == "runtime_error"