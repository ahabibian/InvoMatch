from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from invomatch.domain.models import ReconciliationRun
from invomatch.runtime import RuntimeFailure, assess_stuck_run
from invomatch.services.reconciliation_runs import (
    DEFAULT_LEASE_SECONDS,
    claim_reconciliation_run,
    update_reconciliation_run,
)
from invomatch.services.run_store import RunStore


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class RecoveryScanItem:
    run_id: str
    assessment_reason: str
    recovery_decision: str


@dataclass(frozen=True, slots=True)
class RecoveryScanResult:
    scanned_processing_runs: int
    failed_run_ids: list[str]
    reenter_candidate_run_ids: list[str]
    untouched_run_ids: list[str]


@dataclass(frozen=True, slots=True)
class RecoveryClaimResult:
    run_id: str
    claimed_by: str
    recovery_decision: str
    assessment_reason: str
    run: ReconciliationRun


class RuntimeRecoveryService:
    def scan_and_apply_recovery(
        self,
        *,
        run_store: RunStore,
        failure_lookup: dict[str, RuntimeFailure] | None = None,
        now: datetime | None = None,
    ) -> RecoveryScanResult:
        effective_now = now or _utcnow()
        failures = failure_lookup or {}

        processing_runs, _ = run_store.list_runs(status="processing")

        failed_run_ids: list[str] = []
        reenter_candidate_run_ids: list[str] = []
        untouched_run_ids: list[str] = []

        for run in processing_runs:
            assessment = assess_stuck_run(
                run,
                last_failure=failures.get(run.run_id),
                now=effective_now,
            )

            if not assessment.is_stuck:
                untouched_run_ids.append(run.run_id)
                continue

            if assessment.recovery_decision == "reenter":
                reenter_candidate_run_ids.append(run.run_id)
                continue

            if assessment.recovery_decision == "fail":
                update_reconciliation_run(
                    run.run_id,
                    status="failed",
                    error_message=(
                        f"[stuck_run] {assessment.reason}: "
                        "runtime recovery terminalized processing run"
                    ),
                    run_store=run_store,
                )
                failed_run_ids.append(run.run_id)
                continue

            untouched_run_ids.append(run.run_id)

        return RecoveryScanResult(
            scanned_processing_runs=len(processing_runs),
            failed_run_ids=failed_run_ids,
            reenter_candidate_run_ids=reenter_candidate_run_ids,
            untouched_run_ids=untouched_run_ids,
        )

    def claim_reentry_candidate(
        self,
        *,
        run_id: str,
        worker_id: str,
        run_store: RunStore,
        failure_lookup: dict[str, RuntimeFailure] | None = None,
        lease_seconds: int = DEFAULT_LEASE_SECONDS,
        now: datetime | None = None,
    ) -> RecoveryClaimResult:
        effective_now = now or _utcnow()
        failures = failure_lookup or {}

        run = run_store.get_run(run_id)
        if run is None:
            raise KeyError(f"Reconciliation run not found: {run_id}")

        assessment = assess_stuck_run(
            run,
            last_failure=failures.get(run.run_id),
            now=effective_now,
        )

        if not assessment.is_stuck:
            raise ValueError(
                f"Run is not eligible for recovery claim: {run_id} ({assessment.reason})"
            )

        if assessment.recovery_decision != "reenter":
            raise ValueError(
                f"Run is not reenterable: {run_id} ({assessment.reason})"
            )

        claimed_run = claim_reconciliation_run(
            run_id,
            worker_id=worker_id,
            lease_seconds=lease_seconds,
            run_store=run_store,
            now=effective_now,
        )

        return RecoveryClaimResult(
            run_id=claimed_run.run_id,
            claimed_by=worker_id,
            recovery_decision=assessment.recovery_decision,
            assessment_reason=assessment.reason,
            run=claimed_run,
        )