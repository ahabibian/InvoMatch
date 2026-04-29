from __future__ import annotations

from datetime import datetime, timezone

from invomatch.domain.models import ReconciliationRun


def build_run(**overrides) -> ReconciliationRun:
    now = datetime.now(timezone.utc)

    base = {
        "run_id": "run-test",
        "tenant_id": "tenant-test",
        "status": "queued",
        "version": 0,
        "created_at": now,
        "updated_at": now,
        "started_at": None,
        "finished_at": None,
        "claimed_by": None,
        "claimed_at": None,
        "lease_expires_at": None,
        "attempt_count": 0,
        "invoice_csv_path": "input/invoices.csv",
        "payment_csv_path": "input/payments.csv",
        "error": None,
        "error_message": None,
        "report": None,
    }

    base.update(overrides)
    return ReconciliationRun(**base)