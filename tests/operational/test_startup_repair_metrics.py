from invomatch.services.operational.operational_metrics import (
    InMemoryOperationalMetricsStore,
    OperationalMetricsService,
)
from invomatch.services.startup_repair_coordinator import StartupRepairScanItem


def test_operational_metrics_service_tracks_startup_repair_items() -> None:
    store = InMemoryOperationalMetricsStore()
    service = OperationalMetricsService(store)

    service.record_startup_repair_item(
        item=StartupRepairScanItem(
            run_id="run-1",
            original_status="processing",
            final_status="review_required",
            repair_attempted=True,
            repair_applied=True,
            skipped_due_to_active_lease=False,
            skipped_due_to_terminal_state=False,
            unresolved_mismatch=False,
            failed=False,
            reason="active_review_cases_present",
        )
    )

    service.record_startup_repair_item(
        item=StartupRepairScanItem(
            run_id="run-2",
            original_status="processing",
            final_status="processing",
            repair_attempted=False,
            repair_applied=False,
            skipped_due_to_active_lease=True,
            skipped_due_to_terminal_state=False,
            unresolved_mismatch=False,
            failed=False,
            reason="skipped_due_to_active_lease",
        )
    )

    service.record_startup_repair_item(
        item=StartupRepairScanItem(
            run_id="run-3",
            original_status="review_required",
            final_status="review_required",
            repair_attempted=True,
            repair_applied=False,
            skipped_due_to_active_lease=False,
            skipped_due_to_terminal_state=False,
            unresolved_mismatch=False,
            failed=False,
            reason="no_repair_needed",
        )
    )

    service.record_startup_repair_item(
        item=StartupRepairScanItem(
            run_id="run-4",
            original_status="completed",
            final_status="completed",
            repair_attempted=True,
            repair_applied=False,
            skipped_due_to_active_lease=False,
            skipped_due_to_terminal_state=False,
            unresolved_mismatch=True,
            failed=True,
            reason="repair_failed",
        )
    )

    snapshot = service.snapshot()

    assert snapshot.counters["startup_repair_items_total"] == 4
    assert snapshot.counters["startup_repairs_applied_total"] == 1
    assert snapshot.counters["startup_repair_skipped_active_lease_total"] == 1
    assert snapshot.counters["startup_repair_noop_total"] == 1
    assert snapshot.counters["startup_repair_unresolved_total"] == 1
    assert snapshot.counters["startup_repair_failed_total"] == 1