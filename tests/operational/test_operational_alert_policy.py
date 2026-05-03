from datetime import datetime, timezone

from invomatch.services.operational.alert_policy import OperationalAlertPolicy


def test_alert_policy_reports_clear_without_alert_signals() -> None:
    policy = OperationalAlertPolicy()

    result = policy.evaluate(signals={})

    assert result.status == "clear"
    assert result.alerts == []


def test_alert_policy_reports_critical_startup_repair_failed_alert() -> None:
    policy = OperationalAlertPolicy()

    result = policy.evaluate(
        signals={
            "startup_repair_failed_total": 1,
        }
    )

    assert result.status == "active"
    assert len(result.alerts) == 1

    alert = result.alerts[0]
    assert alert.code == "startup_repair_failed"
    assert alert.severity == "critical"
    assert alert.recommended_action == "inspect_startup_repair"
    assert alert.signal == "startup_repair_failed_total"
    assert alert.value == 1


def test_alert_policy_reports_critical_unresolved_startup_alert() -> None:
    policy = OperationalAlertPolicy()

    result = policy.evaluate(
        signals={
            "startup_repair_unresolved_total": 2,
        }
    )

    assert result.status == "active"
    assert result.alerts[0].code == "startup_repair_unresolved"
    assert result.alerts[0].severity == "critical"
    assert result.alerts[0].value == 2


def test_alert_policy_reports_terminal_failure_warning() -> None:
    policy = OperationalAlertPolicy()

    result = policy.evaluate(
        signals={
            "terminal_failures_confirmed_total": 3,
        }
    )

    assert result.status == "active"
    assert result.alerts[0].code == "terminal_failures_confirmed"
    assert result.alerts[0].severity == "warning"
    assert result.alerts[0].recommended_action == "inspect_terminal_failures"


def test_alert_policy_reports_recovery_action_info() -> None:
    policy = OperationalAlertPolicy()

    result = policy.evaluate(
        signals={
            "recovery_action_taken_total": 4,
        }
    )

    assert result.status == "active"
    assert result.alerts[0].code == "recovery_automation_active"
    assert result.alerts[0].severity == "info"
    assert result.alerts[0].recommended_action == "inspect_recovery_activity"


def test_alert_policy_returns_alerts_in_stable_priority_order() -> None:
    policy = OperationalAlertPolicy()

    result = policy.evaluate(
        signals={
            "recovery_action_taken_total": 4,
            "terminal_failures_confirmed_total": 3,
            "startup_repair_unresolved_total": 2,
            "startup_repair_failed_total": 1,
        }
    )

    assert [alert.code for alert in result.alerts] == [
        "startup_repair_failed",
        "startup_repair_unresolved",
        "terminal_failures_confirmed",
        "recovery_automation_active",
    ]


def test_alert_policy_handles_non_integer_signal_values_safely() -> None:
    policy = OperationalAlertPolicy()

    result = policy.evaluate(
        signals={
            "startup_repair_failed_total": "not-a-number",
            "terminal_failures_confirmed_total": None,
        }
    )

    assert result.status == "clear"
    assert result.alerts == []


def test_alert_policy_uses_injected_clock() -> None:
    fixed_now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    policy = OperationalAlertPolicy(now_provider=lambda: fixed_now)

    result = policy.evaluate(signals={})

    assert result.generated_at == "2026-01-02T03:04:05+00:00"
