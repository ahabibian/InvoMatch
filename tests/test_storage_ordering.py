from datetime import datetime, timezone
from pathlib import Path

from invomatch.domain.models import ReconciliationRun
from invomatch.services.sqlite_run_store import SqliteRunStore


def _make_run(run_id: str, ts: datetime):
    return ReconciliationRun(
        run_id=run_id,
        status="queued",
        version=0,
        created_at=ts,
        updated_at=ts,
        started_at=None,
        finished_at=None,
        claimed_by=None,
        claimed_at=None,
        lease_expires_at=None,
        attempt_count=0,
        invoice_csv_path="a.csv",
        payment_csv_path="b.csv",
        error_message=None,
        report=None,
    )


def test_storage_ordering_deterministic(tmp_path: Path):
    db = tmp_path / "ordering.sqlite"
    store = SqliteRunStore(db)

    ts = datetime.now(timezone.utc)

    r1 = _make_run("run-b", ts)
    r2 = _make_run("run-a", ts)
    r3 = _make_run("run-c", ts)

    store.create_run(r1)
    store.create_run(r2)
    store.create_run(r3)

    runs, total = store.list_runs(limit=10, sort_order="asc")

    ids = [r.run_id for r in runs]

    assert total == 3
    assert ids == ["run-a", "run-b", "run-c"]