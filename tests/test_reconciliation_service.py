import json
from pathlib import Path

import pytest

from invomatch.services.reconciliation import reconcile, reconcile_and_save
from invomatch.services.reconciliation_errors import ReconciliationExecutionError, ReconciliationInputValidationError
from invomatch.services.reconciliation_runs import load_reconciliation_run
from invomatch.services.run_store import InMemoryRunStore, JsonRunStore

ROOT_DIR = Path(__file__).resolve().parents[1]


def test_reconcile_returns_typed_report_with_summary_counts():
    report = reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )

    assert report.total_invoices == 50
    assert report.matched == 20
    assert report.duplicate_detected == 10
    assert report.partial_match == 10
    assert report.unmatched == 10


def test_reconcile_results_are_bound_to_invoice_ids():
    report = reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )

    assert len(report.results) == report.total_invoices
    assert all(result.invoice_id.startswith("INV-") for result in report.results)
    assert all(result.match_result.status in {"matched", "duplicate_detected", "partial_match", "unmatched"} for result in report.results)


def test_reconcile_and_save_moves_run_through_review_required_lifecycle(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")

    run = reconcile_and_save(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )

    persisted_run = load_reconciliation_run(run.run_id, run_store=run_store)

    assert run.status == "review_required"
    assert run.started_at is not None
    assert run.finished_at is None
    assert run.updated_at >= run.created_at
    assert run.report is not None
    assert run.error_message is None
    assert persisted_run.status == "review_required"
    assert persisted_run.report is not None


def test_reconcile_and_save_supports_injected_in_memory_store():
    run_store = InMemoryRunStore()

    run = reconcile_and_save(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )

    persisted_run = load_reconciliation_run(run.run_id, run_store=run_store)

    assert run.status == "review_required"
    assert persisted_run.run_id == run.run_id
    assert persisted_run.report is not None


def test_reconcile_and_save_marks_run_failed_when_execution_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")

    def boom(invoice_csv_path: Path, payment_csv_path: Path):
        raise RuntimeError("reconciliation exploded")

    monkeypatch.setattr("invomatch.services.reconciliation.reconcile", boom)

    with pytest.raises(ReconciliationExecutionError, match="Reconciliation execution failed: reconciliation exploded"):
        reconcile_and_save(
            ROOT_DIR / "sample-data" / "invoices.csv",
            ROOT_DIR / "sample-data" / "payments.csv",
            run_store=run_store,
        )

    persisted_runs = json.loads(run_store.path.read_text(encoding="utf-8"))
    assert len(persisted_runs) == 1
    failed_run = persisted_runs[0]
    assert failed_run["status"] == "failed"
    assert failed_run["started_at"] is not None
    assert failed_run["finished_at"] is not None
    assert failed_run["error_message"] is not None
    assert "execution_failure" in failed_run["error_message"]
    assert "reconciliation exploded" in failed_run["error_message"]
    assert failed_run["report"] is None


def test_reconcile_and_save_rejects_missing_invoice_file(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")

    with pytest.raises(ReconciliationInputValidationError, match="invoice_csv_path does not exist"):
        reconcile_and_save(
            ROOT_DIR / "sample-data" / "missing.csv",
            ROOT_DIR / "sample-data" / "payments.csv",
            run_store=run_store,
        )

    runs, total = run_store.list_runs()
    assert runs == []
    assert total == 0


def test_reconcile_and_save_rejects_wrong_extension(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    invoice_path = tmp_path / "invoices.txt"
    invoice_path.write_text("id,date,amount`nINV-1,2024-01-01,10.00`n", encoding="utf-8")

    with pytest.raises(ReconciliationInputValidationError, match="invoice_csv_path must point to a .csv file"):
        reconcile_and_save(
            invoice_path,
            ROOT_DIR / "sample-data" / "payments.csv",
            run_store=run_store,
        )

    runs, total = run_store.list_runs()
    assert runs == []
    assert total == 0

from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.reconciliation_errors import ReconciliationExecutionError
from invomatch.services.run_store import InMemoryRunStore
from invomatch.runtime import RuntimeExecutor
from invomatch.runtime.runtime_policy import RuntimeRetryPolicy


class _AlwaysFailingMatchRecordStore:
    def save_many(self, records):
        raise RuntimeError("match record persistence unavailable")


def test_reconcile_and_save_completes_successfully_with_runtime_executor(tmp_path: Path):
    run_store = InMemoryRunStore()

    run = reconcile_and_save(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )

    assert run.status in {"completed", "review_required"}
    assert run.started_at is not None
    if run.status == "completed":
        assert run.finished_at is not None
    else:
        assert run.status == "review_required"
        assert run.finished_at is None
    assert run.error_message is None


def test_reconcile_and_save_marks_run_failed_when_runtime_failure_terminalizes(tmp_path: Path):
    run_store = InMemoryRunStore()
    executor = RuntimeExecutor(retry_policy=RuntimeRetryPolicy(max_attempts=2))

    with pytest.raises(ReconciliationExecutionError, match="Reconciliation execution failed"):
        reconcile_and_save(
            ROOT_DIR / "sample-data" / "invoices.csv",
            ROOT_DIR / "sample-data" / "payments.csv",
            run_store=run_store,
            match_record_store=_AlwaysFailingMatchRecordStore(),
            runtime_executor=executor,
        )

    runs, total = run_store.list_runs()
    assert total == 1

    failed_run = runs[0]
    assert failed_run.status == "failed"
    assert failed_run.finished_at is not None
    assert failed_run.error_message is not None
    assert "retry_exhausted" in failed_run.error_message
    assert "completed" not in failed_run.status


def test_reconcile_and_save_does_not_persist_false_completed_state_after_runtime_failure(tmp_path: Path):
    run_store = InMemoryRunStore()
    executor = RuntimeExecutor(retry_policy=RuntimeRetryPolicy(max_attempts=1))

    with pytest.raises(ReconciliationExecutionError):
        reconcile_and_save(
            ROOT_DIR / "sample-data" / "invoices.csv",
            ROOT_DIR / "sample-data" / "payments.csv",
            run_store=run_store,
            match_record_store=_AlwaysFailingMatchRecordStore(),
            runtime_executor=executor,
        )

    runs, total = run_store.list_runs()
    assert total == 1
    persisted_run = runs[0]

    assert persisted_run.status == "failed"
    assert persisted_run.report is None
    assert persisted_run.error_message is not None