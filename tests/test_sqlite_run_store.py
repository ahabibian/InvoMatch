import json
import sqlite3
from pathlib import Path

from invomatch.main import create_app
from invomatch.services.reconciliation import reconcile
from invomatch.services.reconciliation_runs import create_reconciliation_run, update_reconciliation_run
from invomatch.services.run_store import SqliteRunStore

ROOT_DIR = Path(__file__).resolve().parents[1]


def test_sqlite_run_store_bootstraps_schema_on_initialization(tmp_path: Path):
    database_path = tmp_path / "reconciliation_runs.sqlite3"

    SqliteRunStore(database_path)

    assert database_path.exists()
    with sqlite3.connect(database_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        schema_version = connection.execute("SELECT schema_version FROM schema_meta").fetchone()

    assert "reconciliation_runs" in table_names
    assert "schema_meta" in table_names
    assert schema_version == (3,)


def test_sqlite_run_store_persists_nullable_fields_and_report_payload(tmp_path: Path):
    run_store = SqliteRunStore(tmp_path / "reconciliation_runs.sqlite3")
    report = reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )

    run = create_reconciliation_run(
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )
    completed_run = update_reconciliation_run(
        run.run_id,
        status="processing",
        run_store=run_store,
    )
    completed_run = update_reconciliation_run(
        completed_run.run_id,
        status="completed",
        report=report,
        run_store=run_store,
    )

    with sqlite3.connect(run_store.path) as connection:
        row = connection.execute(
            "SELECT started_at, finished_at, error_message, report_json FROM reconciliation_runs WHERE run_id = ?",
            (run.run_id,),
        ).fetchone()

    assert row is not None
    assert row[0] is not None
    assert row[1] is not None
    assert row[2] is None
    persisted_report = json.loads(row[3])
    assert persisted_report["version"] == 1
    assert persisted_report["payload"]["matched"] == report.matched
    assert persisted_report["payload"]["results"][0]["invoice_id"].startswith("INV-")
    assert completed_run.report is not None


def test_sqlite_run_store_reads_legacy_report_payload_without_version_envelope(tmp_path: Path):
    run_store = SqliteRunStore(tmp_path / "reconciliation_runs.sqlite3")
    report = reconcile(
        ROOT_DIR / "sample-data" / "invoices.csv",
        ROOT_DIR / "sample-data" / "payments.csv",
    )

    with sqlite3.connect(run_store.path) as connection:
        connection.execute(
            """
            INSERT INTO reconciliation_runs (
                run_id,
                status,
                created_at,
                updated_at,
                started_at,
                finished_at,
                invoice_csv_path,
                payment_csv_path,
                error_message,
                report_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "legacy-run",
                "completed",
                "2026-03-18T10:00:00+00:00",
                "2026-03-18T10:00:00+00:00",
                "2026-03-18T10:00:00+00:00",
                "2026-03-18T10:00:00+00:00",
                "sample-data/invoices.csv",
                "sample-data/payments.csv",
                None,
                json.dumps(report.model_dump(mode="json")),
            ),
        )

    loaded_run = run_store.get_run("legacy-run")

    assert loaded_run is not None
    assert loaded_run.report is not None
    assert loaded_run.report.matched == report.matched
    assert loaded_run.report.results[0].invoice_id == report.results[0].invoice_id


def test_sqlite_run_store_list_runs_uses_deterministic_tiebreak_ordering(tmp_path: Path):
    run_store = SqliteRunStore(tmp_path / "reconciliation_runs.sqlite3")
    created_at = "2026-03-18T10:00:00+00:00"

    with sqlite3.connect(run_store.path) as connection:
        connection.executemany(
            """
            INSERT INTO reconciliation_runs (
                run_id,
                status,
                created_at,
                updated_at,
                started_at,
                finished_at,
                invoice_csv_path,
                payment_csv_path,
                error_message,
                report_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "run-b",
                    "queued",
                    created_at,
                    created_at,
                    None,
                    None,
                    "sample-data/invoices-b.csv",
                    "sample-data/payments-b.csv",
                    None,
                    None,
                ),
                (
                    "run-a",
                    "queued",
                    created_at,
                    created_at,
                    None,
                    None,
                    "sample-data/invoices-a.csv",
                    "sample-data/payments-a.csv",
                    None,
                    None,
                ),
            ],
        )

    asc_runs, _ = run_store.list_runs(sort_order="asc")
    desc_runs, _ = run_store.list_runs(sort_order="desc")

    assert [run.run_id for run in asc_runs] == ["run-a", "run-b"]
    assert [run.run_id for run in desc_runs] == ["run-b", "run-a"]


def test_create_app_can_compose_sqlite_run_store(tmp_path: Path):
    database_path = tmp_path / "app_runs.sqlite3"

    app = create_app(run_store_backend="sqlite", run_store_path=database_path)

    assert isinstance(app.state.run_store, SqliteRunStore)
    assert app.state.run_store.path == database_path
    assert database_path.exists()

def test_sqlite_run_store_round_trips_structured_error(tmp_path: Path):
    from invomatch.domain.models import RunError

    run_store = SqliteRunStore(tmp_path / "reconciliation_runs.sqlite3")

    run = create_reconciliation_run(
        invoice_csv_path=ROOT_DIR / "sample-data" / "invoices.csv",
        payment_csv_path=ROOT_DIR / "sample-data" / "payments.csv",
        run_store=run_store,
    )

    run = update_reconciliation_run(
        run.run_id,
        status="processing",
        run_store=run_store,
    )

    failed_run = update_reconciliation_run(
        run.run_id,
        status="failed",
        error=RunError(
            code="retry_exhausted",
            message="retry limit reached for operation: reconcile_and_save",
            retryable=False,
            terminal=True,
        ),
        run_store=run_store,
    )

    loaded_run = run_store.get_run(failed_run.run_id)

    assert loaded_run is not None
    assert loaded_run.status == "failed"
    assert loaded_run.error is not None
    assert loaded_run.error.code == "retry_exhausted"
    assert loaded_run.error.message == "retry limit reached for operation: reconcile_and_save"
    assert loaded_run.error.retryable is False
    assert loaded_run.error.terminal is True