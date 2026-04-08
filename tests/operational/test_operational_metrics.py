from invomatch.domain.operational.models import OperationalDecision, OperationalReasonCode
from invomatch.services.operational.operational_metrics import (
    InMemoryOperationalMetricsStore,
    OperationalMetricsService,
)


def test_operational_metrics_service_tracks_recovery_results() -> None:
    store = InMemoryOperationalMetricsStore()
    service = OperationalMetricsService(store)

    service.record_recovery_result(
        decision=OperationalDecision.RETRY_TRIGGERED,
        reason_code=OperationalReasonCode.RECOVERABLE_FAILURE,
        action_taken=True,
    )
    service.record_recovery_result(
        decision=OperationalDecision.ALREADY_RECOVERED_NOOP,
        reason_code=OperationalReasonCode.ALREADY_RECOVERED_SAME_INCIDENT,
        action_taken=False,
    )
    service.record_recovery_result(
        decision=OperationalDecision.TERMINAL_CONFIRMED,
        reason_code=OperationalReasonCode.RETRY_BUDGET_EXHAUSTED,
        action_taken=False,
    )

    snapshot = service.snapshot()

    assert snapshot.counters["recovery_attempts_total"] == 3
    assert snapshot.counters["recovery_action_taken_total"] == 1
    assert snapshot.counters["retries_triggered_total"] == 1
    assert snapshot.counters["recovery_noop_total"] == 1
    assert snapshot.counters["terminal_failures_confirmed_total"] == 1

    assert snapshot.decision_counts["retry_triggered"] == 1
    assert snapshot.decision_counts["already_recovered_noop"] == 1
    assert snapshot.decision_counts["terminal_confirmed"] == 1

    assert snapshot.reason_counts["recoverable_failure"] == 1
    assert snapshot.reason_counts["already_recovered_same_incident"] == 1
    assert snapshot.reason_counts["retry_budget_exhausted"] == 1