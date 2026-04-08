from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from invomatch.services.operational.operational_scan_service import (
    OperationalScanRequest,
    OperationalScanService,
    OperationalScanSummary,
)


@dataclass(frozen=True, slots=True)
class SchedulerTickResult:
    triggered: bool
    skipped: bool
    reason: str
    summary: Optional[OperationalScanSummary] = None


class OperationalSchedulerService:
    def __init__(
        self,
        *,
        scan_service: OperationalScanService,
        default_scan_limit: int = 100,
    ) -> None:
        if default_scan_limit <= 0:
            raise ValueError("default_scan_limit must be > 0")

        self._scan_service = scan_service
        self._default_scan_limit = default_scan_limit
        self._tick_in_progress = False

    def run_tick(self, *, limit: int | None = None) -> SchedulerTickResult:
        if self._tick_in_progress:
            return SchedulerTickResult(
                triggered=False,
                skipped=True,
                reason="tick_already_in_progress",
            )

        effective_limit = limit if limit is not None else self._default_scan_limit
        if effective_limit <= 0:
            raise ValueError("effective scan limit must be > 0")

        self._tick_in_progress = True
        try:
            summary = self._scan_service.scan(
                OperationalScanRequest(limit=effective_limit)
            )
            return SchedulerTickResult(
                triggered=True,
                skipped=False,
                reason="tick_executed",
                summary=summary,
            )
        finally:
            self._tick_in_progress = False