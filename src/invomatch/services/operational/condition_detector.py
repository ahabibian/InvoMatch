from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Literal


OperationalHealthStatus = Literal["healthy", "attention_required", "degraded"]
OperationalRecommendedAction = Literal[
    "none",
    "inspect_startup_repair",
    "inspect_terminal_failures",
]


@dataclass(frozen=True, slots=True)
class OperationalConditionSnapshot:
    status: OperationalHealthStatus
    generated_at: str
    signals: dict[str, int]
    summary: dict[str, str]
    recommended_action: OperationalRecommendedAction


class OperationalConditionDetector:
    """
    Converts low-level operational counters into operator-facing health signals.

    This is intentionally policy-only:
    - no FastAPI dependency
    - no persistence dependency
    - no authorization dependency
    - deterministic input/output behavior when now_provider is injected
    """

    def __init__(
        self,
        *,
        now_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    def evaluate(self, *, counters: dict[str, Any]) -> OperationalConditionSnapshot:
        normalized_counters = dict(counters or {})
        signals = self.build_signals(counters=normalized_counters)

        return OperationalConditionSnapshot(
            status=self.build_health_state(counters=normalized_counters),
            generated_at=self._now_provider().isoformat(),
            signals=signals,
            summary=self.build_summary(counters=normalized_counters),
            recommended_action=self.build_recommended_action(
                counters=normalized_counters
            ),
        )

    def build_health_state(
        self,
        *,
        counters: dict[str, Any],
    ) -> OperationalHealthStatus:
        startup_failures = self._safe_int(counters.get("startup_repair_failed_total"))
        unresolved_startup = self._safe_int(
            counters.get("startup_repair_unresolved_total")
        )
        terminal_failures = self._safe_int(
            counters.get("terminal_failures_confirmed_total")
        )

        if startup_failures > 0 or unresolved_startup > 0:
            return "degraded"

        if terminal_failures > 0:
            return "attention_required"

        return "healthy"

    def build_signals(self, *, counters: dict[str, Any]) -> dict[str, int]:
        return {
            "recovery_attempts_total": self._safe_int(
                counters.get("recovery_attempts_total")
            ),
            "recovery_action_taken_total": self._safe_int(
                counters.get("recovery_action_taken_total")
            ),
            "retries_triggered_total": self._safe_int(
                counters.get("retries_triggered_total")
            ),
            "reentries_triggered_total": self._safe_int(
                counters.get("reentries_triggered_total")
            ),
            "terminal_failures_confirmed_total": self._safe_int(
                counters.get("terminal_failures_confirmed_total")
            ),
            "startup_repair_items_total": self._safe_int(
                counters.get("startup_repair_items_total")
            ),
            "startup_repairs_applied_total": self._safe_int(
                counters.get("startup_repairs_applied_total")
            ),
            "startup_repair_failed_total": self._safe_int(
                counters.get("startup_repair_failed_total")
            ),
            "startup_repair_unresolved_total": self._safe_int(
                counters.get("startup_repair_unresolved_total")
            ),
            "startup_repair_skipped_total": self._sum_prefixed(
                counters,
                "startup_repair_skipped_",
            ),
        }

    def build_recommended_action(
        self,
        *,
        counters: dict[str, Any],
    ) -> OperationalRecommendedAction:
        startup_failures = self._safe_int(counters.get("startup_repair_failed_total"))
        unresolved_startup = self._safe_int(
            counters.get("startup_repair_unresolved_total")
        )
        terminal_failures = self._safe_int(
            counters.get("terminal_failures_confirmed_total")
        )

        if startup_failures > 0 or unresolved_startup > 0:
            return "inspect_startup_repair"

        if terminal_failures > 0:
            return "inspect_terminal_failures"

        return "none"

    def build_summary(self, *, counters: dict[str, Any]) -> dict[str, str]:
        startup_failures = self._safe_int(counters.get("startup_repair_failed_total"))
        unresolved_startup = self._safe_int(
            counters.get("startup_repair_unresolved_total")
        )
        startup_repairs = self._safe_int(counters.get("startup_repairs_applied_total"))
        recovery_attempts = self._safe_int(counters.get("recovery_attempts_total"))
        recovery_actions = self._safe_int(counters.get("recovery_action_taken_total"))
        terminal_failures = self._safe_int(
            counters.get("terminal_failures_confirmed_total")
        )

        if startup_failures > 0 or unresolved_startup > 0:
            startup_repair = "startup repair has unresolved or failed repair outcomes"
        elif startup_repairs > 0:
            startup_repair = "startup repair applied corrections successfully"
        else:
            startup_repair = "no startup repair issues detected"

        if recovery_actions > 0:
            recovery = "recovery automation has taken action"
        elif recovery_attempts > 0:
            recovery = "recovery automation evaluated candidates without action"
        else:
            recovery = "no recovery activity detected"

        if terminal_failures > 0:
            terminal = "terminal failures were confirmed and require operator attention"
        else:
            terminal = "no terminal failure confirmations detected"

        return {
            "startup_repair": startup_repair,
            "recovery": recovery,
            "terminal_failures": terminal,
        }

    def _safe_int(self, value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _sum_prefixed(self, counters: dict[str, Any], prefix: str) -> int:
        return sum(
            self._safe_int(value)
            for key, value in counters.items()
            if str(key).startswith(prefix)
        )
