from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Sequence

from invomatch.domain.operational.models import OperationalDecision
from invomatch.services.operational.recovery_loop_service import (
    RecoveryCandidate,
    RecoveryLoopResult,
    RecoveryLoopService,
)


class ScanCandidateSource(Protocol):
    def list_candidates(self, limit: int) -> Sequence[RecoveryCandidate]:
        ...


@dataclass(frozen=True, slots=True)
class OperationalScanRequest:
    limit: int = 100

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise ValueError("limit must be > 0")


@dataclass(frozen=True, slots=True)
class OperationalScanSummary:
    requested_limit: int
    scanned_count: int
    processed_count: int
    retry_triggered_count: int
    reentry_triggered_count: int
    skipped_count: int
    terminal_count: int
    rejected_count: int
    noop_count: int
    results: tuple[RecoveryLoopResult, ...] = field(default_factory=tuple)


class OperationalScanService:
    def __init__(
        self,
        *,
        candidate_source: ScanCandidateSource,
        recovery_loop_service: RecoveryLoopService,
    ) -> None:
        self._candidate_source = candidate_source
        self._recovery_loop_service = recovery_loop_service

    def scan(self, request: OperationalScanRequest) -> OperationalScanSummary:
        candidates = tuple(self._candidate_source.list_candidates(limit=request.limit))
        results = tuple(self._recovery_loop_service.process(candidate) for candidate in candidates)

        return OperationalScanSummary(
            requested_limit=request.limit,
            scanned_count=len(candidates),
            processed_count=len(results),
            retry_triggered_count=self._count(results, OperationalDecision.RETRY_TRIGGERED),
            reentry_triggered_count=self._count(results, OperationalDecision.REENTRY_TRIGGERED),
            skipped_count=self._count(results, OperationalDecision.RECOVERY_SKIPPED),
            terminal_count=self._count(results, OperationalDecision.TERMINAL_CONFIRMED),
            rejected_count=self._count(results, OperationalDecision.CANDIDATE_REJECTED),
            noop_count=self._count(results, OperationalDecision.ALREADY_RECOVERED_NOOP),
            results=results,
        )

    def _count(
        self,
        results: tuple[RecoveryLoopResult, ...],
        decision: OperationalDecision,
    ) -> int:
        return sum(1 for item in results if item.decision == decision)