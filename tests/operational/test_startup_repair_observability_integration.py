from datetime import datetime, timezone

from invomatch.services.operational.operational_audit import (
    InMemoryOperationalAuditRepository,
    OperationalAuditService,
)
from invomatch.services.operational.operational_metrics import (
    InMemoryOperationalMetricsStore,
    OperationalMetricsService,
)
from invomatch.services.startup_repair_coordinator import StartupRepairCoordinator


def _now() -> datetime:
    return datetime.now(timezone.utc)


class FakeRun:
    def __init__(self, *, run_id: str, status: str) -> None:
        self.run_id = run_id
        self.status = status
        self.claimed_by = None
        self.lease_expires_at = None


class FakeRunStore:
    def __init__(self, runs) -> None:
        self._runs = runs

    def list_runs(self, limit=100000, offset=0):
        return list(self._runs), len(self._runs)


class FakeRepairResult:
    def __init__(self, *, repaired_status: str, reason: str) -> None:
        self.repaired_status = repaired_status
        self.reason = reason


class FakeRepairService:
    def repair_run(self, run_id: str):
        return FakeRepairResult(
            repaired_status="review_required",
            reason="active_review_cases_present",
        )


def test_startup_repair_emits_audit_and_metrics_for_applied_repair() -> None:
    audit_repository = InMemoryOperationalAuditRepository()
    audit_service = OperationalAuditService(audit_repository)

    metrics_store = InMemoryOperationalMetricsStore()
    metrics_service = OperationalMetricsService(metrics_store)

    coordinator = StartupRepairCoordinator(
        run_store=FakeRunStore([FakeRun(run_id="run-1", status="processing")]),
        review_store=None,
        repair_service=FakeRepairService(),
        audit_service=audit_service,
        metrics_service=metrics_service,
        now_provider=_now,
    )

    result = coordinator.run_startup_scan()

    snapshot = metrics_service.snapshot()
    events = audit_repository.list_events()

    assert result.repairs_applied == 1
    assert snapshot.counters["startup_repair_items_total"] == 1
    assert snapshot.counters["startup_repairs_applied_total"] == 1

    assert len(events) == 1
    assert events[0].run_id == "run-1"
    assert events[0].event_type == "startup_repair_applied"
    assert events[0].metadata["source"] == "startup_consistency_scan"
    assert events[0].metadata["repair_applied"] == "true"