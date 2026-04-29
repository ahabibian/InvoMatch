from datetime import UTC, datetime, timedelta

from invomatch.domain.audit.models import AuditCategory, AuditEvent, AuditEventQuery
from invomatch.repositories.audit_event_repository_sqlite import SqliteAuditEventRepository


def test_sqlite_audit_event_repository_persists_and_returns_sequence_ids(tmp_path) -> None:
    db_path = tmp_path / "audit_events.sqlite3"
    repository = SqliteAuditEventRepository(str(db_path))

    base_time = datetime(2026, 4, 23, 12, 0, tzinfo=UTC)

    event_one = AuditEvent(
        event_id="event-1",
        sequence_id=None,
        tenant_id="tenant-a",
        occurred_at=base_time,
        recorded_at=base_time,
        event_type="authentication_success",
        category=AuditCategory.SECURITY,
        user_id="user-1",
        outcome="allowed",
        request_path="/api/reconciliation/runs",
        request_method="GET",
        metadata={"source": "test"},
    )
    event_two = AuditEvent(
        event_id="event-2",
        sequence_id=None,
        tenant_id="tenant-a",
        occurred_at=base_time + timedelta(minutes=1),
        recorded_at=base_time + timedelta(minutes=1),
        event_type="retry_triggered",
        category=AuditCategory.OPERATIONAL,
        run_id="run-1",
        correlation_id="corr-1",
        outcome="allowed",
        decision="retry_triggered",
        reason_code="recoverable_failure",
        new_state="retry_pending",
        attempt_number=2,
        metadata={"source": "recovery_loop"},
    )

    stored_one = repository.create(event_one)
    stored_two = repository.create(event_two)

    assert stored_one.sequence_id == 1
    assert stored_two.sequence_id == 2
    assert stored_one.tenant_id == "tenant-a"
    assert stored_two.tenant_id == "tenant-a"

    events = repository.list_events(AuditEventQuery(tenant_id="tenant-a", limit=10, offset=0))

    assert len(events) == 2
    assert events[0].event_id == "event-1"
    assert events[1].event_id == "event-2"
    assert events[1].run_id == "run-1"
    assert events[1].decision == "retry_triggered"
    assert events[1].reason_code == "recoverable_failure"
    assert events[1].metadata["source"] == "recovery_loop"


def test_sqlite_audit_event_repository_filters_by_run_user_type_and_time(tmp_path) -> None:
    db_path = tmp_path / "audit_events.sqlite3"
    repository = SqliteAuditEventRepository(str(db_path))

    base_time = datetime(2026, 4, 23, 12, 0, tzinfo=UTC)

    repository.create(
        AuditEvent(
            event_id="event-1",
            sequence_id=None,
            tenant_id="tenant-a",
            occurred_at=base_time,
            recorded_at=base_time,
            event_type="authentication_success",
            category=AuditCategory.SECURITY,
            user_id="user-1",
            outcome="allowed",
            metadata={},
        )
    )
    repository.create(
        AuditEvent(
            event_id="event-2",
            sequence_id=None,
            tenant_id="tenant-a",
            occurred_at=base_time + timedelta(minutes=1),
            recorded_at=base_time + timedelta(minutes=1),
            event_type="authorization_denied",
            category=AuditCategory.SECURITY,
            user_id="user-2",
            outcome="denied",
            capability="runs:write",
            metadata={},
        )
    )
    repository.create(
        AuditEvent(
            event_id="event-3",
            sequence_id=None,
            tenant_id="tenant-a",
            occurred_at=base_time + timedelta(minutes=2),
            recorded_at=base_time + timedelta(minutes=2),
            event_type="retry_triggered",
            category=AuditCategory.OPERATIONAL,
            run_id="run-1",
            outcome="allowed",
            decision="retry_triggered",
            metadata={},
        )
    )
    repository.create(
        AuditEvent(
            event_id="event-4",
            sequence_id=None,
            tenant_id="tenant-b",
            occurred_at=base_time + timedelta(minutes=3),
            recorded_at=base_time + timedelta(minutes=3),
            event_type="authentication_success",
            category=AuditCategory.SECURITY,
            user_id="user-1",
            outcome="allowed",
            metadata={},
        )
    )

    run_events = repository.list_events(
        AuditEventQuery(tenant_id="tenant-a", run_id="run-1", limit=10, offset=0)
    )
    assert len(run_events) == 1
    assert run_events[0].event_id == "event-3"

    user_events = repository.list_events(
        AuditEventQuery(tenant_id="tenant-a", user_id="user-2", limit=10, offset=0)
    )
    assert len(user_events) == 1
    assert user_events[0].event_id == "event-2"

    type_events = repository.list_events(
        AuditEventQuery(tenant_id="tenant-a", event_type="authentication_success", limit=10, offset=0)
    )
    assert len(type_events) == 1
    assert type_events[0].event_id == "event-1"

    time_events = repository.list_events(
        AuditEventQuery(
            tenant_id="tenant-a",
            occurred_from=base_time + timedelta(seconds=30),
            occurred_to=base_time + timedelta(minutes=1, seconds=30),
            limit=10,
            offset=0,
        )
    )
    assert len(time_events) == 1
    assert time_events[0].event_id == "event-2"

    tenant_b_events = repository.list_events(
        AuditEventQuery(tenant_id="tenant-b", limit=10, offset=0)
    )
    assert len(tenant_b_events) == 1
    assert tenant_b_events[0].event_id == "event-4"

    tenant_a_events = repository.list_events(
        AuditEventQuery(tenant_id="tenant-a", limit=10, offset=0)
    )
    assert {event.event_id for event in tenant_a_events} == {"event-1", "event-2", "event-3"}