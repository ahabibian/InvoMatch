from invomatch.domain.operational.models import OperationalDecision
from invomatch.services.operational.operational_scan_service import (
    OperationalScanRequest,
    OperationalScanService,
)
from invomatch.services.operational.recovery_eligibility_policy import (
    RecoveryEligibilityInput,
)
from invomatch.services.operational.recovery_loop_service import (
    InMemoryRecoveryIncidentTracker,
    RecoveryCandidate,
    RecoveryLoopService,
)


class FakeCandidateSource:
    def __init__(self, candidates: list[RecoveryCandidate]) -> None:
        self._candidates = candidates
        self.requested_limits: list[int] = []

    def list_candidates(self, limit: int) -> list[RecoveryCandidate]:
        self.requested_limits.append(limit)
        return self._candidates[:limit]


def test_scan_processes_candidates_and_returns_structured_summary() -> None:
    retry_calls: list[str] = []
    reentry_calls: list[str] = []

    loop = RecoveryLoopService(
        retry_executor=lambda run_id: retry_calls.append(run_id),
        reentry_executor=lambda run_id: reentry_calls.append(run_id),
    )

    source = FakeCandidateSource(
        candidates=[
            RecoveryCandidate(
                run_id="run-1",
                incident_key="failure-1",
                eligibility=RecoveryEligibilityInput(
                    business_status="failed",
                    retry_count=0,
                    retry_limit=3,
                    failure_code="runtime_error",
                    failure_is_recoverable=True,
                ),
            ),
            RecoveryCandidate(
                run_id="run-2",
                incident_key="stuck-1",
                eligibility=RecoveryEligibilityInput(
                    business_status="processing",
                    retry_count=0,
                    retry_limit=2,
                    stuck_detected=True,
                ),
            ),
            RecoveryCandidate(
                run_id="run-3",
                incident_key="done-1",
                eligibility=RecoveryEligibilityInput(
                    business_status="completed",
                    retry_count=0,
                    retry_limit=2,
                    failure_is_recoverable=True,
                ),
            ),
        ]
    )

    service = OperationalScanService(
        candidate_source=source,
        recovery_loop_service=loop,
    )

    summary = service.scan(OperationalScanRequest(limit=10))

    assert source.requested_limits == [10]
    assert summary.requested_limit == 10
    assert summary.scanned_count == 3
    assert summary.processed_count == 3
    assert summary.retry_triggered_count == 1
    assert summary.reentry_triggered_count == 1
    assert summary.rejected_count == 1
    assert summary.skipped_count == 0
    assert summary.terminal_count == 0
    assert summary.noop_count == 0

    assert retry_calls == ["run-1"]
    assert reentry_calls == ["run-2"]

    decisions = [result.decision for result in summary.results]
    assert decisions == [
        OperationalDecision.RETRY_TRIGGERED,
        OperationalDecision.REENTRY_TRIGGERED,
        OperationalDecision.CANDIDATE_REJECTED,
    ]


def test_scan_is_noop_safe_for_repeated_incident_processing() -> None:
    retry_calls: list[str] = []
    tracker = InMemoryRecoveryIncidentTracker()

    loop = RecoveryLoopService(
        incident_tracker=tracker,
        retry_executor=lambda run_id: retry_calls.append(run_id),
    )

    candidate = RecoveryCandidate(
        run_id="run-4",
        incident_key="failure-2",
        eligibility=RecoveryEligibilityInput(
            business_status="failed",
            retry_count=0,
            retry_limit=3,
            failure_code="runtime_error",
            failure_is_recoverable=True,
        ),
    )

    source = FakeCandidateSource(candidates=[candidate])

    service = OperationalScanService(
        candidate_source=source,
        recovery_loop_service=loop,
    )

    first = service.scan(OperationalScanRequest(limit=10))
    second = service.scan(OperationalScanRequest(limit=10))

    assert first.retry_triggered_count == 1
    assert first.noop_count == 0

    assert second.retry_triggered_count == 0
    assert second.noop_count == 1
    assert second.results[0].decision == OperationalDecision.ALREADY_RECOVERED_NOOP

    assert retry_calls == ["run-4"]


def test_scan_respects_request_limit() -> None:
    retry_calls: list[str] = []

    loop = RecoveryLoopService(
        retry_executor=lambda run_id: retry_calls.append(run_id),
    )

    candidates = [
        RecoveryCandidate(
            run_id="run-5",
            incident_key="failure-3",
            eligibility=RecoveryEligibilityInput(
                business_status="failed",
                retry_count=0,
                retry_limit=3,
                failure_code="runtime_error",
                failure_is_recoverable=True,
            ),
        ),
        RecoveryCandidate(
            run_id="run-6",
            incident_key="failure-4",
            eligibility=RecoveryEligibilityInput(
                business_status="failed",
                retry_count=0,
                retry_limit=3,
                failure_code="runtime_error",
                failure_is_recoverable=True,
            ),
        ),
    ]

    source = FakeCandidateSource(candidates=candidates)

    service = OperationalScanService(
        candidate_source=source,
        recovery_loop_service=loop,
    )

    summary = service.scan(OperationalScanRequest(limit=1))

    assert summary.scanned_count == 1
    assert summary.processed_count == 1
    assert summary.retry_triggered_count == 1
    assert retry_calls == ["run-5"]


def test_invalid_scan_limit_is_rejected() -> None:
    try:
        OperationalScanRequest(limit=0)
    except ValueError as exc:
        assert str(exc) == "limit must be > 0"
    else:
        raise AssertionError("Expected ValueError for non-positive scan limit")