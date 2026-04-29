from invomatch.domain.operational.models import (
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
)
from invomatch.repositories.audit_event_repository_sqlite import SqliteAuditEventRepository
from invomatch.services.operational.operational_audit import (
    OperationalAuditService,
    OperationalAuditWrite,
    PersistentOperationalAuditRepository,
)


def test_persistent_operational_audit_repository_records_to_repository(tmp_path) -> None:
    db_path = tmp_path / "audit_events.sqlite3"
    sqlite_repository = SqliteAuditEventRepository(str(db_path))
    repository = PersistentOperationalAuditRepository(sqlite_repository)
    service = OperationalAuditService(repository)

    event = service.record(
        OperationalAuditWrite(
            tenant_id="tenant-test",
            run_id="run-1",
            event_type="startup_repair_applied",
            decision=OperationalDecision.REENTRY_TRIGGERED,
            reason_code=OperationalReasonCode.STUCK_PROCESSING,
            previous_operational_state=OperationalCondition.HEALTHY,
            new_operational_state=OperationalCondition.REENTRY_PENDING,
            correlation_id="startup-repair:run-1",
            metadata={"source": "startup_consistency_scan"},
        )
    )

    assert event.tenant_id == "tenant-test"
    assert event.run_id == "run-1"

    stored = repository.list_events(tenant_id="tenant-test")
    assert len(stored) == 1
    assert stored[0].tenant_id == "tenant-test"
    assert stored[0].run_id == "run-1"
    assert stored[0].event_type == "startup_repair_applied"
    assert stored[0].new_operational_state == OperationalCondition.REENTRY_PENDING