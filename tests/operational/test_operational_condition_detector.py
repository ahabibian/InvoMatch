from invomatch.services.operational.condition_detector import (
    OperationalConditionDetector,
)


def test_condition_detector_reports_healthy_without_problem_counters() -> None:
    detector = OperationalConditionDetector()

    result = detector.evaluate(counters={})

    assert result.status == "healthy"
    assert result.recommended_action == "none"
    assert result.signals["recovery_attempts_total"] == 0
    assert result.summary["startup_repair"] == "no startup repair issues detected"


def test_condition_detector_reports_degraded_for_startup_repair_failure() -> None:
    detector = OperationalConditionDetector()

    result = detector.evaluate(
        counters={
            "startup_repair_failed_total": 1,
        }
    )

    assert result.status == "degraded"
    assert result.recommended_action == "inspect_startup_repair"
    assert result.signals["startup_repair_failed_total"] == 1
    assert (
        result.summary["startup_repair"]
        == "startup repair has unresolved or failed repair outcomes"
    )


def test_condition_detector_reports_degraded_for_unresolved_startup_mismatch() -> None:
    detector = OperationalConditionDetector()

    result = detector.evaluate(
        counters={
            "startup_repair_unresolved_total": 1,
        }
    )

    assert result.status == "degraded"
    assert result.recommended_action == "inspect_startup_repair"
    assert result.signals["startup_repair_unresolved_total"] == 1


def test_condition_detector_reports_attention_required_for_terminal_failures() -> None:
    detector = OperationalConditionDetector()

    result = detector.evaluate(
        counters={
            "terminal_failures_confirmed_total": 1,
        }
    )

    assert result.status == "attention_required"
    assert result.recommended_action == "inspect_terminal_failures"
    assert result.signals["terminal_failures_confirmed_total"] == 1
    assert (
        result.summary["terminal_failures"]
        == "terminal failures were confirmed and require operator attention"
    )


def test_condition_detector_prioritizes_degraded_over_terminal_attention() -> None:
    detector = OperationalConditionDetector()

    result = detector.evaluate(
        counters={
            "startup_repair_failed_total": 1,
            "terminal_failures_confirmed_total": 1,
        }
    )

    assert result.status == "degraded"
    assert result.recommended_action == "inspect_startup_repair"


def test_condition_detector_sums_startup_repair_skipped_counters() -> None:
    detector = OperationalConditionDetector()

    result = detector.evaluate(
        counters={
            "startup_repair_skipped_active_lease_total": 2,
            "startup_repair_skipped_terminal_total": 3,
        }
    )

    assert result.signals["startup_repair_skipped_total"] == 5


def test_condition_detector_handles_non_integer_counter_values_safely() -> None:
    detector = OperationalConditionDetector()

    result = detector.evaluate(
        counters={
            "recovery_attempts_total": "not-a-number",
            "startup_repair_failed_total": None,
        }
    )

    assert result.status == "healthy"
    assert result.signals["recovery_attempts_total"] == 0
    assert result.signals["startup_repair_failed_total"] == 0


def test_condition_detector_reports_recovery_action_summary() -> None:
    detector = OperationalConditionDetector()

    result = detector.evaluate(
        counters={
            "recovery_attempts_total": 3,
            "recovery_action_taken_total": 1,
        }
    )

    assert result.status == "healthy"
    assert result.summary["recovery"] == "recovery automation has taken action"
    assert result.signals["recovery_attempts_total"] == 3
    assert result.signals["recovery_action_taken_total"] == 1
def test_condition_detector_uses_injected_clock() -> None:
    from datetime import datetime, timezone

    fixed_now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    detector = OperationalConditionDetector(now_provider=lambda: fixed_now)

    result = detector.evaluate(counters={})

    assert result.generated_at == "2026-01-02T03:04:05+00:00"
