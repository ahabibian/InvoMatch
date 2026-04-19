from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from invomatch.domain.models import ReconciliationRun
from invomatch.domain.review.models import FeedbackRecord
from invomatch.main import create_app
from invomatch.services.review_service import ReviewService
from invomatch.services.run_store import JsonRunStore
from invomatch.services.sqlite_review_store import SqliteReviewStore


def _now() -> datetime:
    return datetime(2026, 4, 19, 21, 30, 0, tzinfo=timezone.utc)


def _build_run(
    *,
    run_id: str,
    status: str,
    version: int = 1,
    claimed_by: str | None = None,
    lease_expires_at: datetime | None = None,
) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        run_id=run_id,
        status=status,
        version=version,
        created_at=now - timedelta(minutes=10),
        updated_at=now - timedelta(minutes=1),
        started_at=now - timedelta(minutes=9),
        finished_at=None if status not in {"completed", "failed", "cancelled"} else now - timedelta(minutes=2),
        claimed_by=claimed_by,
        claimed_at=now - timedelta(minutes=9) if claimed_by else None,
        lease_expires_at=lease_expires_at,
        attempt_count=1,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error=None,
        error_message=None,
        report=None,
    )


def test_startup_repair_visibility_and_recovery_alignment(tmp_path: Path) -> None:
    run_store_path = tmp_path / "runs.json"
    review_store_path = tmp_path / "review.sqlite3"
    export_dir = tmp_path / "exports"

    run_store = JsonRunStore(run_store_path)
    review_store = SqliteReviewStore(review_store_path)
    review_service = ReviewService()

    repairable_run = _build_run(
        run_id="run-repairable",
        status="processing",
        claimed_by="worker-old",
        lease_expires_at=_now() - timedelta(minutes=8),
    )
    leased_run = _build_run(
        run_id="run-leased",
        status="processing",
        claimed_by="worker-active",
        lease_expires_at=_now() + timedelta(minutes=10),
    )
    terminal_run = _build_run(
        run_id="run-terminal",
        status="failed",
        version=2,
        claimed_by="worker-old",
        lease_expires_at=_now() - timedelta(minutes=12),
    )

    run_store.create_run(repairable_run)
    run_store.create_run(leased_run)
    run_store.create_run(terminal_run)

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    feedback = FeedbackRecord(
        feedback_id="fb-startup-1",
        run_id=repairable_run.run_id,
        source_type="run_orchestration",
        source_reference="INV-STARTUP-001",
        feedback_type="REVIEW_CASE",
        raw_payload={
            "invoice_id": "INV-STARTUP-001",
            "reason": "manual_review_required",
            "blocking": True,
            "source_status": "unmatched",
        },
        submitted_by="system",
    )
    review_store.save_feedback(feedback)

    review_item, audit_event = review_service.create_review_item(
        feedback=feedback,
        review_session=session,
    )
    review_store.save_review_item(review_item)
    review_store.save_audit_event(audit_event)

    app = create_app(
        run_store_backend="json",
        run_store_path=run_store_path,
        review_store_backend="sqlite",
        review_store_path=review_store_path,
        export_base_dir=export_dir,
        startup_now_provider=_now,
    )
    client = TestClient(app)

    startup_result = app.state.startup_repair_result


    assert startup_result.total_runs_scanned == 3
    assert startup_result.repairs_applied == 1
    assert startup_result.skipped_due_to_active_lease == 1
    assert startup_result.skipped_due_to_terminal_protection == 1
    assert startup_result.failed_repairs == 0
    assert startup_result.unresolved_mismatches == 0
    assert startup_result.startup_scan_failed is False
    assert startup_result.readiness_ok is True
    assert startup_result.readiness_reason == "ready_with_startup_skips"

    restarted_run_store = JsonRunStore(run_store_path)

    repaired = restarted_run_store.get_run("run-repairable")
    leased = restarted_run_store.get_run("run-leased")
    terminal = restarted_run_store.get_run("run-terminal")

    assert repaired is not None
    assert leased is not None
    assert terminal is not None

    assert repaired.status == "review_required"
    assert leased.status == "processing"
    assert terminal.status == "failed"

    health_response = client.get("/health")
    assert health_response.status_code == 200

    health_payload = health_response.json()
    assert health_payload["status"] == "ok"
    assert health_payload["startup_scan_failed"] is False
    assert health_payload["readiness_ok"] is True
    assert health_payload["readiness_reason"] == "ready_with_startup_skips"

    readiness_response = client.get("/readiness")
    assert readiness_response.status_code == 200

    readiness_payload = readiness_response.json()
    assert readiness_payload["status"] == "ready"
    assert readiness_payload["startup_scan_failed"] is False
    assert readiness_payload["readiness_reason"] == "ready_with_startup_skips"
    assert readiness_payload["repairs_applied"] == 1
    assert readiness_payload["skipped_due_to_active_lease"] == 1
    assert readiness_payload["skipped_due_to_terminal_protection"] == 1
    assert readiness_payload["unresolved_mismatches"] == 0