from invomatch.domain.security import AuthenticatedPrincipal, Role, UserStatus
from invomatch.repositories.audit_event_repository_sqlite import SqliteAuditEventRepository
from invomatch.services.security.security_audit_service import PersistentSecurityAuditService


def test_persistent_security_audit_service_records_to_repository(tmp_path) -> None:
    db_path = tmp_path / "audit_events.sqlite3"
    repository = SqliteAuditEventRepository(str(db_path))
    service = PersistentSecurityAuditService(repository)

    principal = AuthenticatedPrincipal(
        user_id="user-1",
        username="operator",
        role=Role.OPERATOR,
        status=UserStatus.ACTIVE,
        auth_source="token",
        tenant_id="tenant-test",
    )

    event = service.record(
        event_type="authentication_success",
        principal=principal,
        request_path="/api/reconciliation/runs",
        request_method="GET",
        outcome="allowed",
        metadata={"source": "test"},
    )

    assert event.event_type == "authentication_success"
    assert event.user_id == "user-1"
    assert event.tenant_id == "tenant-test"

    stored = service.list_events(tenant_id="tenant-test")
    assert len(stored) == 1
    assert stored[0].event_type == "authentication_success"
    assert stored[0].user_id == "user-1"
    assert stored[0].tenant_id == "tenant-test"