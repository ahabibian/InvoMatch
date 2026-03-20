import json
from pathlib import Path

import pytest

from invomatch.domain.models import ReconciliationReport, can_transition, is_terminal_status
from invomatch.services.reconciliation import reconcile
from invomatch.services.reconciliation_runs import (
    create_reconciliation_run,
    load_reconciliation_run,
    save_reconciliation_run,
    update_reconciliation_run,
)
from invomatch.services.run_store import InMemoryRunStore, JsonRunStore

ROOT_DIR = Path(__file__).resolve().parents[1]


def _report() -> ReconciliationReport:
    return reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )


def test_lifecycle_helpers_enforce_terminal_status_and_valid_transitions():
    assert is_terminal_status("completed") is True
    assert is_terminal_status("failed") is True
    assert is_terminal_status("pending") is False
    assert can_transition("pending", "running") is True
    assert can_transition("running", "completed") is True
    assert can_transition("completed", "running") is False


@pytest.mark.parametrize("store_factory", [JsonRunStore, lambda path: InMemoryRunStore()])
def test_run_store_create_get_update_and_list_operations(tmp_path: Path, store_factory):
    run_store = store_factory(tmp_path / "reconciliation_runs.json")
    created_run = create_reconciliation_run(
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )

    fetched_run = run_store.get_run(created_run.run_id)
    assert fetched_run is not None
    assert fetched_run.run_id == created_run.run_id
    assert fetched_run.status == "pending"

    updated_run = created_run.model_copy(update={"status": "failed", "error_message": "boom"})
    persisted_run = run_store.update_run(updated_run)

    runs, total = run_store.list_runs()
    assert total == 1
    assert runs[0].run_id == created_run.run_id
    assert runs[0].status == "failed"
    assert runs[0].error_message == "boom"
    assert persisted_run.status == "failed"


@pytest.mark.parametrize("store_factory", [JsonRunStore, lambda path: InMemoryRunStore()])
def test_run_store_list_operations_support_status_filter_pagination_and_sort(tmp_path: Path, store_factory):
    run_store = store_factory(tmp_path / "reconciliation_runs.json")
    pending = create_reconciliation_run(
        Path("sample-data/invoices-pending.csv"),
        Path("sample-data/payments-pending.csv"),
        run_store=run_store,
    )
    failed = create_reconciliation_run(
        Path("sample-data/invoices-failed.csv"),
        Path("sample-data/payments-failed.csv"),
        run_store=run_store,
    )
    completed = create_reconciliation_run(
        Path("sample-data/invoices-completed.csv"),
        Path("sample-data/payments-completed.csv"),
        run_store=run_store,
    )

    run_store.update_run(failed.model_copy(update={"status": "failed", "error_message": "import failed"}))
    run_store.update_run(completed.model_copy(update={"status": "completed"}))

    failed_runs, failed_total = run_store.list_runs(status="failed")
    assert failed_total == 1
    assert [run.run_id for run in failed_runs] == [failed.run_id]

    paged_runs, total = run_store.list_runs(limit=1, offset=1, sort_order="asc")
    assert total == 3
    assert len(paged_runs) == 1
    assert paged_runs[0].run_id == failed.run_id
    assert pending.run_id != completed.run_id


@pytest.mark.parametrize("store_factory", [JsonRunStore, lambda path: InMemoryRunStore()])
def test_run_store_returns_copies_from_queries(tmp_path: Path, store_factory):
    run_store = store_factory(tmp_path / "reconciliation_runs.json")
    created_run = create_reconciliation_run(
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )

    fetched_run = run_store.get_run(created_run.run_id)
    assert fetched_run is not None
    fetched_run.status = "failed"

    persisted_run = run_store.get_run(created_run.run_id)
    assert persisted_run is not None
    assert persisted_run.status == "pending"


def test_create_reconciliation_run_persists_pending_lifecycle(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")

    run = create_reconciliation_run(
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )

    assert run.status == "pending"
    assert run.created_at == run.updated_at
    assert run.started_at is None
    assert run.finished_at is None
    assert run.error_message is None
    assert run.report is None
    assert run_store.path.exists()


def test_update_reconciliation_run_persists_all_lifecycle_fields(tmp_path: Path):
    report = _report()
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")

    run = create_reconciliation_run(
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )
    running_run = update_reconciliation_run(run.run_id, status="running", run_store=run_store)
    completed_run = update_reconciliation_run(
        run.run_id,
        status="completed",
        report=report,
        run_store=run_store,
    )
    loaded_run = load_reconciliation_run(run.run_id, run_store=run_store)

    assert running_run.status == "running"
    assert running_run.started_at is not None
    assert running_run.finished_at is None
    assert completed_run.status == "completed"
    assert completed_run.started_at is not None
    assert completed_run.finished_at is not None
    assert completed_run.error_message is None
    assert isinstance(loaded_run.report, ReconciliationReport)
    assert loaded_run.report.total_invoices == report.total_invoices
    assert loaded_run.report.matched == report.matched
    assert loaded_run.report.duplicate_detected == report.duplicate_detected
    assert loaded_run.report.partial_match == report.partial_match
    assert loaded_run.report.unmatched == report.unmatched
    assert len(loaded_run.report.results) == len(report.results)


def test_update_reconciliation_run_rejects_invalid_transition(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    run = create_reconciliation_run(
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )
    update_reconciliation_run(run.run_id, status="running", run_store=run_store)
    update_reconciliation_run(run.run_id, status="completed", report=None, run_store=run_store)

    with pytest.raises(ValueError, match="Invalid reconciliation run transition"):
        update_reconciliation_run(run.run_id, status="running", run_store=run_store)


def test_load_reconciliation_run_backfills_legacy_completed_payload(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    report = _report()
    legacy_payload = [
        {
            "run_id": "legacy-run",
            "created_at": "2026-03-18T10:00:00Z",
            "invoice_csv_path": "sample-data/invoices.csv",
            "payment_csv_path": "sample-data/payments.csv",
            "report": report.model_dump(mode="json"),
        }
    ]
    run_store.path.write_text(json.dumps(legacy_payload), encoding="utf-8")

    loaded_run = load_reconciliation_run("legacy-run", run_store=run_store)

    assert loaded_run.status == "completed"
    assert loaded_run.updated_at == loaded_run.created_at
    assert loaded_run.started_at == loaded_run.created_at
    assert loaded_run.finished_at == loaded_run.created_at
    assert loaded_run.error_message is None
    assert loaded_run.report is not None


def test_save_reconciliation_run_preserves_summary_and_result_structure(tmp_path: Path):
    report = _report()
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")

    saved_run = save_reconciliation_run(
        report=report,
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )
    loaded_run = load_reconciliation_run(saved_run.run_id, run_store=run_store)

    assert loaded_run.status == "completed"
    assert loaded_run.report is not None
    first_result = loaded_run.report.results[0]
    assert first_result.invoice_id.startswith("INV-")
    assert first_result.match_result.status in {
        "matched",
        "duplicate_detected",
        "partial_match",
        "unmatched",
    }
