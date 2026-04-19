from datetime import datetime, timedelta, timezone

from invomatch.services.startup_repair_coordinator import StartupRepairCoordinator


def _now() -> datetime:
    return datetime.now(timezone.utc)


class FakeRun:
    def __init__(
        self,
        *,
        run_id: str,
        status: str,
        claimed_by=None,
        lease_expires_at=None,
    ) -> None:
        self.run_id = run_id
        self.status = status
        self.claimed_by = claimed_by
        self.lease_expires_at = lease_expires_at


class FakeRunStore:
    def __init__(self, runs):
        self._runs = runs

    def list_runs(self, limit=100000, offset=0):
        return list(self._runs), len(self._runs)


class FakeRepairResult:
    def __init__(self, *, repaired_status: str, reason: str) -> None:
        self.repaired_status = repaired_status
        self.reason = reason


class FakeRepairService:
    def __init__(self, results_by_run_id=None, failing_run_ids=None) -> None:
        self._results_by_run_id = results_by_run_id or {}
        self._failing_run_ids = set(failing_run_ids or [])

    def repair_run(self, run_id: str):
        if run_id in self._failing_run_ids:
            raise RuntimeError("repair failed")
        return self._results_by_run_id.get(
            run_id,
            FakeRepairResult(repaired_status="completed", reason="no_repair_needed"),
        )


def test_startup_repair_coordinator_skips_active_lease() -> None:
    now = _now()
    run = FakeRun(
        run_id="run-lease",
        status="processing",
        claimed_by="worker-1",
        lease_expires_at=now + timedelta(minutes=5),
    )

    coordinator = StartupRepairCoordinator(
        run_store=FakeRunStore([run]),
        review_store=None,
        repair_service=FakeRepairService(),
        now_provider=lambda: now,
    )

    result = coordinator.run_startup_scan()

    assert result.total_runs_scanned == 1
    assert result.skipped_due_to_active_lease == 1
    assert result.repairs_applied == 0
    assert result.readiness_ok is True
    assert result.readiness_reason == "ready_with_startup_skips"


def test_startup_repair_coordinator_skips_terminal_protected_run() -> None:
    now = _now()
    run = FakeRun(
        run_id="run-terminal",
        status="failed",
    )

    coordinator = StartupRepairCoordinator(
        run_store=FakeRunStore([run]),
        review_store=None,
        repair_service=FakeRepairService(),
        now_provider=lambda: now,
    )

    result = coordinator.run_startup_scan()

    assert result.total_runs_scanned == 1
    assert result.skipped_due_to_terminal_protection == 1
    assert result.repairs_applied == 0
    assert result.readiness_ok is True
    assert result.readiness_reason == "ready_with_startup_skips"


def test_startup_repair_coordinator_records_applied_repair() -> None:
    now = _now()
    run = FakeRun(
        run_id="run-repair",
        status="processing",
    )

    repair_service = FakeRepairService(
        results_by_run_id={
            "run-repair": FakeRepairResult(
                repaired_status="review_required",
                reason="active_review_cases_present",
            )
        }
    )

    coordinator = StartupRepairCoordinator(
        run_store=FakeRunStore([run]),
        review_store=None,
        repair_service=repair_service,
        now_provider=lambda: now,
    )

    result = coordinator.run_startup_scan()

    assert result.total_runs_scanned == 1
    assert result.repairs_applied == 1
    assert result.repairable_mismatches_found == 1
    assert result.readiness_ok is True
    assert result.readiness_reason == "ready"


def test_startup_repair_coordinator_records_failed_repair_as_not_ready() -> None:
    now = _now()
    run = FakeRun(
        run_id="run-fail",
        status="review_required",
    )

    coordinator = StartupRepairCoordinator(
        run_store=FakeRunStore([run]),
        review_store=None,
        repair_service=FakeRepairService(failing_run_ids={"run-fail"}),
        now_provider=lambda: now,
    )

    result = coordinator.run_startup_scan()

    assert result.total_runs_scanned == 1
    assert result.failed_repairs == 1
    assert result.unresolved_mismatches == 1
    assert result.readiness_ok is False
    assert result.readiness_reason == "startup_repair_unresolved"