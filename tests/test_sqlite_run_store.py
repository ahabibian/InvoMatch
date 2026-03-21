codex/sqlite-runstore-hardening
﻿import json

import json
main
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
codex/sqlite-runstore-hardening
        schema_version = connection.execute("SELECT schema_version FROM schema_meta").fetchone()

    assert "reconciliation_runs" in table_names
    assert "schema_meta" in table_names
    assert schema_version == (1,)

    assert "reconciliation_runs" in table_names
 main


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
        status="running",
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
codex/sqlite-runstore-hardening
    assert persisted_report["version"] == 1
    assert persisted_report["payload"]["matched"] == report.matched
    assert persisted_report["payload"]["results"][0]["invoice_id"].startswith("INV-")
    assert completed_run.report is not None
    assert persisted_report["matched"] == report.matched
    assert persisted_report["results"][0]["invoice_id"].startswith("INV-")
    assert completed_run.report is not None


def test_create_app_can_compose_sqlite_run_store(tmp_path: Path):
    database_path = tmp_path / "app_runs.sqlite3"

    app = create_app(run_store_backend="sqlite", run_store_path=database_path)

    assert isinstance(app.state.run_store, SqliteRunStore)
    assert app.state.run_store.path == database_path
    assert database_path.exists()
main
