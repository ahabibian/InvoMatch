import os
from datetime import UTC, datetime, timedelta

from invomatch.domain.audit.models import AuditEventQuery
from invomatch.domain.models import ReconciliationRun
from invomatch.main import create_app


class StubRepairResult:
    def __init__(self, repaired_status: str, reason: str) -> None:
        self.repaired_status = repaired_status
        self.reason = reason


class StubRepairService:
    def repair_run(self, run_id: str) -> StubRepairResult:
        return StubRepairResult(
            repaired_status="review_required",
            reason="status_repaired_from_processing",
        )


class StubRunStore:
    def __init__(self, run) -> None:
        self._run = run

    def list_runs(self, limit=100000, offset=0):
        return [self._run], 1


class StubReviewStore:
    pass


def test_startup_repair_persists_audit_event(tmp_path) -> None:
    created_at = datetime.now(UTC) - timedelta(minutes=10)

    run = ReconciliationRun(
        tenant_id="tenant-test",

        run_id="run-1",
        status="processing",
        created_at=created_at,
        updated_at=created_at,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        invoices=[],
        payments=[],
        matched_pairs=[],
        unmatched_invoices=[],
        unmatched_payments=[],
        suggested_pairs=[],
        version=0,
        attempt_count=0,
    )

    previous_startup_repair = os.environ.get("INVOMATCH_STARTUP_REPAIR_ENABLED")
    previous_audit_db_path = os.environ.get("INVOMATCH_AUDIT_EVENT_DB_PATH")
    os.environ["INVOMATCH_STARTUP_REPAIR_ENABLED"] = "false"
    os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = str(tmp_path / "audit_events.sqlite3")
    try:
        app = create_app(
            run_store=StubRunStore(run),
            review_store=StubReviewStore(),
            run_store_backend="sqlite",
            run_store_path=tmp_path / "runs.sqlite3",
            review_store_backend="sqlite",
            review_store_path=tmp_path / "reviews.sqlite3",
            export_base_dir=tmp_path / "exports",
        )
    finally:
        if previous_startup_repair is None:
            os.environ.pop("INVOMATCH_STARTUP_REPAIR_ENABLED", None)
        else:
            os.environ["INVOMATCH_STARTUP_REPAIR_ENABLED"] = previous_startup_repair

        if previous_audit_db_path is None:
            os.environ.pop("INVOMATCH_AUDIT_EVENT_DB_PATH", None)
        else:
            os.environ["INVOMATCH_AUDIT_EVENT_DB_PATH"] = previous_audit_db_path

    app.state.startup_repair_coordinator = app.state.startup_repair_coordinator.__class__(
        run_store=StubRunStore(run),
        review_store=StubReviewStore(),
        repair_service=StubRepairService(),
        metrics_service=app.state.operational_metrics_service,
        audit_service=app.state.operational_audit_service,
        now_provider=lambda: datetime.now(UTC),
    )

    result = app.state.startup_repair_coordinator.run_startup_scan()

    assert result.total_runs_scanned == 1

    events = app.state.audit_event_repository.list_events(
        AuditEventQuery(tenant_id="tenant-test",
run_id="run-1", limit=20, offset=0)
    )

    assert len(events) == 1
    assert events[0].event_type == "startup_repair_applied"
    assert events[0].category.value == "operational"