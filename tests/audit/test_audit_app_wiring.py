from invomatch.main import create_app
from invomatch.repositories.audit_event_repository_sqlite import SqliteAuditEventRepository
from invomatch.services.audit import AuditQueryService
from invomatch.services.operational.operational_audit import OperationalAuditService
from invomatch.services.security.security_audit_service import PersistentSecurityAuditService


def test_create_app_wires_persistent_audit_services(tmp_path) -> None:
    app = create_app(
        run_store_backend="sqlite",
        run_store_path=tmp_path / "runs.sqlite3",
        review_store_backend="sqlite",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )

    assert isinstance(app.state.audit_event_repository, SqliteAuditEventRepository)
    assert isinstance(app.state.audit_query_service, AuditQueryService)
    assert isinstance(app.state.security_audit_service, PersistentSecurityAuditService)
    assert isinstance(app.state.operational_audit_service, OperationalAuditService)