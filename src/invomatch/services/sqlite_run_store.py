codex/sqlite-runstore-hardening
﻿from __future__ import annotation
from __future__ import annotations
main

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from invomatch.domain.models import ReconciliationRun, RunStatus
from invomatch.services.reconciliation_errors import RunStorageError

SortOrder = Literal["asc", "desc"]
codex/sqlite-runstore-hardening
_SCHEMA_VERSION = 1
_REPORT_PAYLOAD_VERSION = 1
_SQLITE_TIMEOUT_SECONDS = 30.0
main


class SqliteRunStore:
    def __init__(self, path: Path):
        self.path = path
        self._bootstrap_schema()

    def create_run(self, run: ReconciliationRun) -> ReconciliationRun:
        payload = self._serialize_run(run)
        try:
            with self._connect() as connection:
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
                        payload["run_id"],
                        payload["status"],
                        payload["created_at"],
                        payload["updated_at"],
                        payload["started_at"],
                        payload["finished_at"],
                        payload["invoice_csv_path"],
                        payload["payment_csv_path"],
                        payload["error_message"],
                        payload["report_json"],
                    ),
                )
        except sqlite3.Error as exc:
            raise RunStorageError(f"Failed to create reconciliation run: {exc}", run_id=run.run_id) from exc
        return run.model_copy(deep=True)

    def update_run(self, run: ReconciliationRun) -> ReconciliationRun:
        payload = self._serialize_run(run)
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    UPDATE reconciliation_runs
                    SET status = ?,
                        updated_at = ?,
                        started_at = ?,
                        finished_at = ?,
                        invoice_csv_path = ?,
                        payment_csv_path = ?,
                        error_message = ?,
                        report_json = ?
                    WHERE run_id = ?
                    """,
                    (
                        payload["status"],
                        payload["updated_at"],
                        payload["started_at"],
                        payload["finished_at"],
                        payload["invoice_csv_path"],
                        payload["payment_csv_path"],
                        payload["error_message"],
                        payload["report_json"],
                        payload["run_id"],
                    ),
                )
        except sqlite3.Error as exc:
            raise RunStorageError(f"Failed to update reconciliation run: {exc}", run_id=run.run_id) from exc

        if cursor.rowcount == 0:
            raise KeyError(f"Reconciliation run not found: {run.run_id}")
        return run.model_copy(deep=True)

    def get_run(self, run_id: str) -> ReconciliationRun | None:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT
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
                    FROM reconciliation_runs
                    WHERE run_id = ?
                    """,
                    (run_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise RunStorageError(f"Failed to load reconciliation run: {exc}", run_id=run_id) from exc

        if row is None:
            return None
        return self._deserialize_row(row)

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_order: SortOrder = "desc",
    ) -> tuple[list[ReconciliationRun], int]:
        where_clause = ""
        parameters: list[Any] = []
        if status is not None:
            where_clause = "WHERE status = ?"
            parameters.append(status)

        order_by = "DESC" if sort_order == "desc" else "ASC"

        try:
            with self._connect() as connection:
                total = connection.execute(
                    f"SELECT COUNT(*) FROM reconciliation_runs {where_clause}",
                    parameters,
                ).fetchone()[0]
                rows = connection.execute(
                    f"""
                    SELECT
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
                    FROM reconciliation_runs
                    {where_clause}
codex/sqlite-runstore-hardening
                    ORDER BY created_at {order_by}, run_id {order_by}

                    ORDER BY created_at {order_by}
            main
                    LIMIT ? OFFSET ?
                    """,
                    [*parameters, limit, offset],
                ).fetchall()
        except sqlite3.Error as exc:
            raise RunStorageError(f"Failed to list reconciliation runs: {exc}") from exc

        return [self._deserialize_row(row) for row in rows], total

    def _bootstrap_schema(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reconciliation_runs (
                    run_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT NULL,
                    finished_at TEXT NULL,
                    invoice_csv_path TEXT NOT NULL,
                    payment_csv_path TEXT NOT NULL,
                    error_message TEXT NULL,
                    report_json TEXT NULL
                )
                """
            )
            connection.execute(
codex/sqlite-runstore-hardening
                """
                CREATE TABLE IF NOT EXISTS schema_meta (
                    schema_version INTEGER NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_reconciliation_runs_status_created_at ON reconciliation_runs (status, created_at, run_id)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_reconciliation_runs_created_at ON reconciliation_runs (created_at, run_id)"
            )
            self._ensure_schema_version(connection)

    def _ensure_schema_version(self, connection: sqlite3.Connection) -> None:
        row = connection.execute("SELECT schema_version FROM schema_meta LIMIT 1").fetchone()
        if row is None:
            connection.execute("INSERT INTO schema_meta (schema_version) VALUES (?)", (_SCHEMA_VERSION,))
            return

        if row[0] is None:
            connection.execute("UPDATE schema_meta SET schema_version = ?", (_SCHEMA_VERSION,))

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=_SQLITE_TIMEOUT_SECONDS,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=NORMAL")
        return connection

    def _serialize_run(self, run: ReconciliationRun) -> dict[str, str | None]:
        report_payload = None
        if run.report is not None:
            report_payload = json.dumps(
                {
                    "version": _REPORT_PAYLOAD_VERSION,
                    "payload": run.report.model_dump(mode="json"),
                }
            )

                "CREATE INDEX IF NOT EXISTS idx_reconciliation_runs_status_created_at ON reconciliation_runs (status, created_at)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_reconciliation_runs_created_at ON reconciliation_runs (created_at)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _serialize_run(self, run: ReconciliationRun) -> dict[str, str | None]:
main
        return {
            "run_id": run.run_id,
            "status": run.status,
            "created_at": self._serialize_datetime(run.created_at),
            "updated_at": self._serialize_datetime(run.updated_at),
            "started_at": self._serialize_optional_datetime(run.started_at),
            "finished_at": self._serialize_optional_datetime(run.finished_at),
            "invoice_csv_path": run.invoice_csv_path,
            "payment_csv_path": run.payment_csv_path,
            "error_message": run.error_message,
codex/sqlite-runstore-hardening
            "report_json": report_payload,
            "report_json": None if run.report is None else json.dumps(run.report.model_dump(mode="json")),
main
        }

    def _deserialize_row(self, row: sqlite3.Row) -> ReconciliationRun:
        report_json = row["report_json"]
        payload = {
            "run_id": row["run_id"],
            "status": row["status"],
            "created_at": self._deserialize_datetime(row["created_at"]),
            "updated_at": self._deserialize_datetime(row["updated_at"]),
            "started_at": self._deserialize_optional_datetime(row["started_at"]),
            "finished_at": self._deserialize_optional_datetime(row["finished_at"]),
            "invoice_csv_path": row["invoice_csv_path"],
            "payment_csv_path": row["payment_csv_path"],
            "error_message": row["error_message"],
codex/sqlite-runstore-hardening
            "report": self._deserialize_report_payload(report_json),
        }
        return ReconciliationRun.model_validate(payload)

    def _deserialize_report_payload(self, report_json: str | None) -> dict[str, Any] | None:
        if report_json is None:
            return None

        payload = json.loads(report_json)
        if isinstance(payload, dict) and payload.get("version") == _REPORT_PAYLOAD_VERSION and "payload" in payload:
            versioned_payload = payload["payload"]
            if not isinstance(versioned_payload, dict):
                raise ValueError("Versioned report payload must contain an object payload")
            return versioned_payload
        if not isinstance(payload, dict):
            raise ValueError("Report payload must be a JSON object")
        return payload

            "report": None if report_json is None else json.loads(report_json),
        }
        return ReconciliationRun.model_validate(payload)

main
    @staticmethod
    def _serialize_datetime(value: datetime) -> str:
        return value.isoformat()

    @classmethod
    def _serialize_optional_datetime(cls, value: datetime | None) -> str | None:
        if value is None:
            return None
        return cls._serialize_datetime(value)

    @staticmethod
    def _deserialize_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @classmethod
    def _deserialize_optional_datetime(cls, value: str | None) -> datetime | None:
        if value is None:
            return None
        return cls._deserialize_datetime(value)
