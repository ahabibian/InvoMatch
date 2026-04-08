from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from invomatch.domain.models import ReconciliationRun
from invomatch.runtime import RuntimeFailure, assess_stuck_run
from invomatch.services.reconciliation_runs import update_reconciliation_run
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