from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from invomatch.domain.operational.models import (
    OperationalCondition,
    OperationalDecision,
    OperationalReasonCode,
)
from invomatch.services.operational.operational_audit import OperationalAuditWrite


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


_RELEVANT_STARTUP_SCAN_STATES = {"processing", "review_required", "completed"}
_TERMINAL_PROTECTED_STATES = {"failed", "cancelled"}


@dataclass(frozen=True, slots=True)
class StartupRepairScanItem:
    run_id: str
    original_status: str
    final_status: str
    repair_attempted: bool
    repair_applied: bool
    skipped_due_to_active_lease: bool
    skipped_due_to_terminal_state: bool
    unresolved_mismatch: bool
    failed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class StartupRepairScanResult:
    total_runs_scanned: int
    repairable_mismatches_found: int
    repairs_applied: int
    no_repair_needed_count: int
    skipped_due_to_active_lease: int
    skipped_due_to_terminal_protection: int
    unresolved_mismatches: int
    failed_repairs: int
    startup_scan_failed: bool
    readiness_ok: bool
    readiness_reason: str
    scan_started_at: datetime
    scan_finished_at: datetime
    items: tuple[StartupRepairScanItem, ...] = field(default_factory=tuple)


class StartupRepairCoordinator:
    def __init__(
        self,
        *,
        run_store: Any,
        review_store: Any,
        repair_service: Any,
        metrics_service: Any | None = None,
        audit_service: Any | None = None,
        now_provider: Any | None = None,
    ) -> None:
        self._run_store = run_store
        self._review_store = review_store
        self._repair_service = repair_service
        self._metrics_service = metrics_service
        self._audit_service = audit_service
        self._now_provider = now_provider or _utcnow

    def run_startup_scan(self) -> StartupRepairScanResult:
        started_at = self._now_provider()

        try:
            runs, _total = self._run_store.list_runs(limit=100000, offset=0)
            items: list[StartupRepairScanItem] = []

            for run in runs:
                status = str(getattr(run, "status", "") or "").strip().lower()

                if status not in _RELEVANT_STARTUP_SCAN_STATES and status not in _TERMINAL_PROTECTED_STATES:
                    continue

                items.append(self._scan_run(run))

            finished_at = self._now_provider()
            return self._build_result(
                items=items,
                started_at=started_at,
                finished_at=finished_at,
            )
        except Exception:
            finished_at = self._now_provider()
            return StartupRepairScanResult(
                total_runs_scanned=0,
                repairable_mismatches_found=0,
                repairs_applied=0,
                no_repair_needed_count=0,
                skipped_due_to_active_lease=0,
                skipped_due_to_terminal_protection=0,
                unresolved_mismatches=0,
                failed_repairs=0,
                startup_scan_failed=True,
                readiness_ok=False,
                readiness_reason="startup_scan_failed",
                scan_started_at=started_at,
                scan_finished_at=finished_at,
                items=tuple(),
            )

    def _scan_run(self, run: Any) -> StartupRepairScanItem:
        run_id = str(getattr(run, "run_id"))
        original_status = str(getattr(run, "status", "") or "").strip().lower()

        if self._has_valid_active_lease(run):
            item = StartupRepairScanItem(
                run_id=run_id,
                original_status=original_status,
                final_status=original_status,
                repair_attempted=False,
                repair_applied=False,
                skipped_due_to_active_lease=True,
                skipped_due_to_terminal_state=False,
                unresolved_mismatch=False,
                failed=False,
                reason="skipped_due_to_active_lease",
            )
            self._record_item(item)
            return item

        if original_status in _TERMINAL_PROTECTED_STATES:
            item = StartupRepairScanItem(
                run_id=run_id,
                original_status=original_status,
                final_status=original_status,
                repair_attempted=False,
                repair_applied=False,
                skipped_due_to_active_lease=False,
                skipped_due_to_terminal_state=True,
                unresolved_mismatch=False,
                failed=False,
                reason="skipped_due_to_terminal_protection",
            )
            self._record_item(item)
            return item

        try:
            repair_result = self._repair_service.repair_run(run_id)
        except Exception:
            item = StartupRepairScanItem(
                run_id=run_id,
                original_status=original_status,
                final_status=original_status,
                repair_attempted=True,
                repair_applied=False,
                skipped_due_to_active_lease=False,
                skipped_due_to_terminal_state=False,
                unresolved_mismatch=True,
                failed=True,
                reason="repair_failed",
            )
            self._record_item(item)
            return item

        final_status = str(getattr(repair_result, "repaired_status", original_status) or "").strip().lower()
        reason = str(getattr(repair_result, "reason", "") or "").strip() or "unknown"

        repair_applied = final_status != original_status and reason != "no_repair_needed"

        item = StartupRepairScanItem(
            run_id=run_id,
            original_status=original_status,
            final_status=final_status,
            repair_attempted=True,
            repair_applied=repair_applied,
            skipped_due_to_active_lease=False,
            skipped_due_to_terminal_state=False,
            unresolved_mismatch=False,
            failed=False,
            reason=reason,
        )
        self._record_item(item)
        return item

    def _has_valid_active_lease(self, run: Any) -> bool:
        claimed_by = getattr(run, "claimed_by", None)
        lease_expires_at = getattr(run, "lease_expires_at", None)

        if claimed_by is None or lease_expires_at is None:
            return False

        return lease_expires_at > self._now_provider()

    def _build_result(
        self,
        *,
        items: list[StartupRepairScanItem],
        started_at: datetime,
        finished_at: datetime,
    ) -> StartupRepairScanResult:
        repairs_applied = sum(1 for item in items if item.repair_applied)
        no_repair_needed_count = sum(1 for item in items if item.reason == "no_repair_needed")
        skipped_due_to_active_lease = sum(1 for item in items if item.skipped_due_to_active_lease)
        skipped_due_to_terminal_protection = sum(1 for item in items if item.skipped_due_to_terminal_state)
        unresolved_mismatches = sum(1 for item in items if item.unresolved_mismatch)
        failed_repairs = sum(1 for item in items if item.failed)
        repairable_mismatches_found = repairs_applied + failed_repairs

        readiness_ok = failed_repairs == 0 and unresolved_mismatches == 0
        readiness_reason = "ready"

        if failed_repairs > 0 or unresolved_mismatches > 0:
            readiness_ok = False
            readiness_reason = "startup_repair_unresolved"
        elif skipped_due_to_active_lease > 0 or skipped_due_to_terminal_protection > 0:
            readiness_ok = True
            readiness_reason = "ready_with_startup_skips"

        return StartupRepairScanResult(
            total_runs_scanned=len(items),
            repairable_mismatches_found=repairable_mismatches_found,
            repairs_applied=repairs_applied,
            no_repair_needed_count=no_repair_needed_count,
            skipped_due_to_active_lease=skipped_due_to_active_lease,
            skipped_due_to_terminal_protection=skipped_due_to_terminal_protection,
            unresolved_mismatches=unresolved_mismatches,
            failed_repairs=failed_repairs,
            startup_scan_failed=False,
            readiness_ok=readiness_ok,
            readiness_reason=readiness_reason,
            scan_started_at=started_at,
            scan_finished_at=finished_at,
            items=tuple(items),
        )

    def _record_item(self, item: StartupRepairScanItem) -> None:
        if self._audit_service is not None:
            record = getattr(self._audit_service, "record", None)
            if callable(record):
                try:
                    record(
                        OperationalAuditWrite(
                            run_id=item.run_id,
                            event_type=self._audit_event_type(item),
                            decision=self._audit_decision(item),
                            reason_code=self._audit_reason_code(item),
                            new_operational_state=self._audit_target_condition(item),
                            reason_detail=item.reason,
                            correlation_id=f"startup-repair:{item.run_id}",
                            metadata={
                                "source": "startup_consistency_scan",
                                "original_status": item.original_status,
                                "final_status": item.final_status,
                                "repair_attempted": str(item.repair_attempted).lower(),
                                "repair_applied": str(item.repair_applied).lower(),
                            },
                        )
                    )
                except Exception:
                    pass

        if self._metrics_service is not None:
            record_startup_repair_item = getattr(self._metrics_service, "record_startup_repair_item", None)
            if callable(record_startup_repair_item):
                try:
                    record_startup_repair_item(item=item)
                except Exception:
                    pass

    def _audit_event_type(self, item: StartupRepairScanItem) -> str:
        if item.repair_applied:
            return "startup_repair_applied"
        if item.skipped_due_to_active_lease:
            return "startup_repair_skipped_active_lease"
        if item.skipped_due_to_terminal_state:
            return "startup_repair_skipped_terminal"
        if item.failed or item.unresolved_mismatch:
            return "startup_repair_unresolved"
        if item.reason == "no_repair_needed":
            return "startup_repair_noop"
        return "startup_repair_observed"

    def _audit_decision(self, item: StartupRepairScanItem) -> OperationalDecision:
        if item.repair_applied:
            return OperationalDecision.REENTRY_TRIGGERED
        if item.skipped_due_to_active_lease:
            return OperationalDecision.RECOVERY_SKIPPED
        if item.skipped_due_to_terminal_state:
            return OperationalDecision.CANDIDATE_REJECTED
        if item.failed or item.unresolved_mismatch:
            return OperationalDecision.CANDIDATE_REJECTED
        return OperationalDecision.ALREADY_RECOVERED_NOOP

    def _audit_reason_code(self, item: StartupRepairScanItem) -> OperationalReasonCode:
        if item.skipped_due_to_active_lease:
            return OperationalReasonCode.VALID_LEASE_PRESENT
        if item.skipped_due_to_terminal_state:
            return OperationalReasonCode.TERMINAL_BUSINESS_STATE
        if item.failed or item.unresolved_mismatch:
            return OperationalReasonCode.CANDIDATE_STATE_CHANGED
        if item.repair_applied:
            return OperationalReasonCode.STUCK_PROCESSING
        return OperationalReasonCode.ALREADY_RECOVERED_SAME_INCIDENT

    def _audit_target_condition(self, item: StartupRepairScanItem) -> OperationalCondition:
        if item.repair_applied:
            return OperationalCondition.REENTRY_PENDING
        if item.skipped_due_to_terminal_state:
            return OperationalCondition.TERMINAL_CONFIRMED
        return OperationalCondition.RECOVERY_SKIPPED