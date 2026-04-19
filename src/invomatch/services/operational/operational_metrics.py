from __future__ import annotations

from dataclasses import dataclass, field

from invomatch.domain.operational.models import OperationalDecision, OperationalReasonCode


@dataclass(frozen=True, slots=True)
class OperationalMetricsSnapshot:
    counters: dict[str, int]
    decision_counts: dict[str, int]
    reason_counts: dict[str, int]


class InMemoryOperationalMetricsStore:
    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._decision_counts: dict[str, int] = {}
        self._reason_counts: dict[str, int] = {}

    def increment_counter(self, name: str, value: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + value

    def increment_decision(self, decision: OperationalDecision) -> None:
        key = decision.value
        self._decision_counts[key] = self._decision_counts.get(key, 0) + 1

    def increment_reason(self, reason_code: OperationalReasonCode) -> None:
        key = reason_code.value
        self._reason_counts[key] = self._reason_counts.get(key, 0) + 1

    def snapshot(self) -> OperationalMetricsSnapshot:
        return OperationalMetricsSnapshot(
            counters=dict(self._counters),
            decision_counts=dict(self._decision_counts),
            reason_counts=dict(self._reason_counts),
        )


class OperationalMetricsService:
    def __init__(self, store: InMemoryOperationalMetricsStore) -> None:
        self._store = store

    def record_recovery_result(
        self,
        *,
        decision: OperationalDecision,
        reason_code: OperationalReasonCode,
        action_taken: bool,
    ) -> None:
        self._store.increment_counter("recovery_attempts_total")
        self._store.increment_decision(decision)
        self._store.increment_reason(reason_code)

        if action_taken:
            self._store.increment_counter("recovery_action_taken_total")

        if decision == OperationalDecision.RETRY_TRIGGERED:
            self._store.increment_counter("retries_triggered_total")
        elif decision == OperationalDecision.REENTRY_TRIGGERED:
            self._store.increment_counter("reentries_triggered_total")
        elif decision == OperationalDecision.RECOVERY_SKIPPED:
            self._store.increment_counter("recovery_skipped_total")
        elif decision == OperationalDecision.TERMINAL_CONFIRMED:
            self._store.increment_counter("terminal_failures_confirmed_total")
        elif decision == OperationalDecision.CANDIDATE_REJECTED:
            self._store.increment_counter("recovery_candidates_rejected_total")
        elif decision == OperationalDecision.ALREADY_RECOVERED_NOOP:
            self._store.increment_counter("recovery_noop_total")

    def record_startup_repair_item(self, *, item) -> None:
        self._store.increment_counter("startup_repair_items_total")

        if getattr(item, "repair_applied", False):
            self._store.increment_counter("startup_repairs_applied_total")

        if getattr(item, "skipped_due_to_active_lease", False):
            self._store.increment_counter("startup_repair_skipped_active_lease_total")

        if getattr(item, "skipped_due_to_terminal_state", False):
            self._store.increment_counter("startup_repair_skipped_terminal_total")

        if getattr(item, "unresolved_mismatch", False):
            self._store.increment_counter("startup_repair_unresolved_total")

        if getattr(item, "failed", False):
            self._store.increment_counter("startup_repair_failed_total")

        if str(getattr(item, "reason", "") or "").strip() == "no_repair_needed":
            self._store.increment_counter("startup_repair_noop_total")

    def snapshot(self) -> OperationalMetricsSnapshot:
        return self._store.snapshot()