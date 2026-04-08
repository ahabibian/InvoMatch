from invomatch.services.operational.operational_scan_service import (
    OperationalScanRequest,
    OperationalScanSummary,
)
from invomatch.services.operational.operational_scheduler_service import (
    OperationalSchedulerService,
)


class FakeScanService:
    def __init__(self, summary: OperationalScanSummary) -> None:
        self._summary = summary
        self.requests: list[OperationalScanRequest] = []

    def scan(self, request: OperationalScanRequest) -> OperationalScanSummary:
        self.requests.append(request)
        return self._summary


def test_scheduler_runs_single_tick_with_default_limit() -> None:
    summary = OperationalScanSummary(
        requested_limit=25,
        scanned_count=2,
        processed_count=2,
        retry_triggered_count=1,
        reentry_triggered_count=0,
        skipped_count=0,
        terminal_count=0,
        rejected_count=1,
        noop_count=0,
        results=(),
    )
    scan_service = FakeScanService(summary=summary)

    scheduler = OperationalSchedulerService(
        scan_service=scan_service,
        default_scan_limit=25,
    )

    result = scheduler.run_tick()

    assert result.triggered is True
    assert result.skipped is False
    assert result.reason == "tick_executed"
    assert result.summary == summary
    assert len(scan_service.requests) == 1
    assert scan_service.requests[0].limit == 25


def test_scheduler_uses_explicit_limit_when_provided() -> None:
    summary = OperationalScanSummary(
        requested_limit=10,
        scanned_count=1,
        processed_count=1,
        retry_triggered_count=1,
        reentry_triggered_count=0,
        skipped_count=0,
        terminal_count=0,
        rejected_count=0,
        noop_count=0,
        results=(),
    )
    scan_service = FakeScanService(summary=summary)

    scheduler = OperationalSchedulerService(
        scan_service=scan_service,
        default_scan_limit=25,
    )

    result = scheduler.run_tick(limit=10)

    assert result.triggered is True
    assert result.skipped is False
    assert result.summary == summary
    assert scan_service.requests[0].limit == 10


def test_scheduler_rejects_invalid_default_limit() -> None:
    try:
        OperationalSchedulerService(
            scan_service=FakeScanService(
                OperationalScanSummary(
                    requested_limit=1,
                    scanned_count=0,
                    processed_count=0,
                    retry_triggered_count=0,
                    reentry_triggered_count=0,
                    skipped_count=0,
                    terminal_count=0,
                    rejected_count=0,
                    noop_count=0,
                    results=(),
                )
            ),
            default_scan_limit=0,
        )
    except ValueError as exc:
        assert str(exc) == "default_scan_limit must be > 0"
    else:
        raise AssertionError("Expected ValueError for invalid default scan limit")


def test_scheduler_rejects_invalid_effective_limit() -> None:
    scheduler = OperationalSchedulerService(
        scan_service=FakeScanService(
            OperationalScanSummary(
                requested_limit=1,
                scanned_count=0,
                processed_count=0,
                retry_triggered_count=0,
                reentry_triggered_count=0,
                skipped_count=0,
                terminal_count=0,
                rejected_count=0,
                noop_count=0,
                results=(),
            )
        ),
        default_scan_limit=10,
    )

    try:
        scheduler.run_tick(limit=0)
    except ValueError as exc:
        assert str(exc) == "effective scan limit must be > 0"
    else:
        raise AssertionError("Expected ValueError for invalid effective limit")


def test_scheduler_skips_overlapping_tick() -> None:
    summary = OperationalScanSummary(
        requested_limit=10,
        scanned_count=0,
        processed_count=0,
        retry_triggered_count=0,
        reentry_triggered_count=0,
        skipped_count=0,
        terminal_count=0,
        rejected_count=0,
        noop_count=0,
        results=(),
    )
    scan_service = FakeScanService(summary=summary)

    scheduler = OperationalSchedulerService(
        scan_service=scan_service,
        default_scan_limit=10,
    )

    scheduler._tick_in_progress = True

    result = scheduler.run_tick()

    assert result.triggered is False
    assert result.skipped is True
    assert result.reason == "tick_already_in_progress"
    assert result.summary is None
    assert scan_service.requests == []


def test_scheduler_resets_in_progress_flag_after_execution() -> None:
    summary = OperationalScanSummary(
        requested_limit=10,
        scanned_count=1,
        processed_count=1,
        retry_triggered_count=0,
        reentry_triggered_count=1,
        skipped_count=0,
        terminal_count=0,
        rejected_count=0,
        noop_count=0,
        results=(),
    )
    scan_service = FakeScanService(summary=summary)

    scheduler = OperationalSchedulerService(
        scan_service=scan_service,
        default_scan_limit=10,
    )

    first = scheduler.run_tick()
    second = scheduler.run_tick()

    assert first.triggered is True
    assert second.triggered is True
    assert len(scan_service.requests) == 2