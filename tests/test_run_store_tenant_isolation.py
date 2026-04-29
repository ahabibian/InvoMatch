from datetime import UTC, datetime
from pathlib import Path

from invomatch.domain.models import ReconciliationRun
from invomatch.services.run_store import InMemoryRunStore, JsonRunStore
from invomatch.services.sqlite_run_store import SqliteRunStore


def _run(run_id: str, tenant_id: str) -> ReconciliationRun:
    now = datetime(2026, 4, 25, 12, 0, tzinfo=UTC)
    return ReconciliationRun(
        run_id=run_id,
        tenant_id=tenant_id,
        status="queued",
        version=0,
        created_at=now,
        updated_at=now,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
    )


def _assert_tenant_filtering(store) -> None:
    store.create_run(_run("run-a", "tenant-a"))
    store.create_run(_run("run-b", "tenant-b"))

    assert store.get_run("run-a", tenant_id="tenant-a") is not None
    assert store.get_run("run-a", tenant_id="tenant-b") is None

    tenant_a_runs, tenant_a_total = store.list_runs(tenant_id="tenant-a")
    tenant_b_runs, tenant_b_total = store.list_runs(tenant_id="tenant-b")

    assert tenant_a_total == 1
    assert tenant_a_runs[0].run_id == "run-a"

    assert tenant_b_total == 1
    assert tenant_b_runs[0].run_id == "run-b"


def test_in_memory_run_store_filters_by_tenant() -> None:
    _assert_tenant_filtering(InMemoryRunStore())


def test_json_run_store_filters_by_tenant(tmp_path: Path) -> None:
    _assert_tenant_filtering(JsonRunStore(tmp_path / "runs.json"))

def test_sqlite_run_store_filters_by_tenant(tmp_path: Path) -> None:
    _assert_tenant_filtering(SqliteRunStore(tmp_path / "runs.sqlite3"))