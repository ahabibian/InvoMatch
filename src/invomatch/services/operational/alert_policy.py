from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Literal


OperationalAlertSeverity = Literal["info", "warning", "critical"]
OperationalAlertStatus = Literal["clear", "active"]
OperationalAlertAction = Literal[
    "none",
    "inspect_startup_repair",
    "inspect_terminal_failures",
    "inspect_recovery_activity",
]


@dataclass(frozen=True, slots=True)
class OperationalAlert:
    code: str
    severity: OperationalAlertSeverity
    message: str
    recommended_action: OperationalAlertAction
    signal: str
    value: int


@dataclass(frozen=True, slots=True)
class OperationalAlertSnapshot:
    status: OperationalAlertStatus
    generated_at: str
    alerts: list[OperationalAlert]


class OperationalAlertPolicy:
    """
    Converts operational signals into machine-readable operator alerts.

    This is intentionally policy-only:
    - no FastAPI dependency
    - no persistence dependency
    - no authorization dependency
    - deterministic output when now_provider is injected
    """

    def __init__(
        self,
        *,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    def evaluate(self, *, signals: dict[str, Any]) -> OperationalAlertSnapshot:
        normalized_signals = dict(signals or {})
        alerts = self.build_alerts(signals=normalized_signals)

        return OperationalAlertSnapshot(
            status="active" if alerts else "clear",
            generated_at=self._now_provider().isoformat(),
            alerts=alerts,
        )

    def build_alerts(self, *, signals: dict[str, Any]) -> list[OperationalAlert]:
        alerts: list[OperationalAlert] = []

        startup_repair_failed = self._safe_int(
            signals.get("startup_repair_failed_total")
        )
        startup_repair_unresolved = self._safe_int(
            signals.get("startup_repair_unresolved_total")
        )
        terminal_failures = self._safe_int(
            signals.get("terminal_failures_confirmed_total")
        )
        recovery_actions = self._safe_int(
            signals.get("recovery_action_taken_total")
        )

        if startup_repair_failed > 0:
            alerts.append(
                OperationalAlert(
                    code="startup_repair_failed",
                    severity="critical",
                    message="startup repair has failed outcomes",
                    recommended_action="inspect_startup_repair",
                    signal="startup_repair_failed_total",
                    value=startup_repair_failed,
                )
            )

        if startup_repair_unresolved > 0:
            alerts.append(
                OperationalAlert(
                    code="startup_repair_unresolved",
                    severity="critical",
                    message="startup repair has unresolved mismatches",
                    recommended_action="inspect_startup_repair",
                    signal="startup_repair_unresolved_total",
                    value=startup_repair_unresolved,
                )
            )

        if terminal_failures > 0:
            alerts.append(
                OperationalAlert(
                    code="terminal_failures_confirmed",
                    severity="warning",
                    message="terminal failures were confirmed",
                    recommended_action="inspect_terminal_failures",
                    signal="terminal_failures_confirmed_total",
                    value=terminal_failures,
                )
            )

        if recovery_actions > 0:
            alerts.append(
                OperationalAlert(
                    code="recovery_automation_active",
                    severity="info",
                    message="recovery automation has taken action",
                    recommended_action="inspect_recovery_activity",
                    signal="recovery_action_taken_total",
                    value=recovery_actions,
                )
            )

        return alerts

    def _safe_int(self, value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
