from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from invomatch.domain.models import ReconciliationRun, RunError, RunStatus
from invomatch.services.reconciliation_errors import (
    ConcurrencyConflictError,
    RunLeaseConflictError,
    RunStorageError,
)

SortOrder = Literal["asc", "desc"]
_SCHEMA_VERSION = 3
_REPORT_PAYLOAD_VERSION = 1
_SQLITE_TIMEOUT_SECONDS = 30.0
_SQLITE_BUSY_TIMEOUT_MS = int(_SQLITE_TIMEOUT_SECONDS * 1000)
_SQLITE_JOURNAL_MODE = "WAL"
_SQLITE_SYNCHRONOUS = "NORMAL"


def _normalize_legacy_run_status(status: str | None) -> str | None:
    if status == "pending":
        return "queued"
    if status == "running":
        return "processing"
    return status


def _status_filter_values(status: RunStatus | None) -> tuple[str, ...]:
    if status is None:
        return ()
    if status == "queued":
        return ("queued", "pending")
    if status == "processing":
        return ("processing", "running")
    return (status,)


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
                        version,
                        created_at,
                        updated_at,
                        started_at,
                        finished_at,
                        claimed_by,
                        claimed_at,
                        lease_expires_at,
                        attempt_count,
                        invoice_csv_path,
                        payment_csv_path,
                        error_message,
                        error_json,
                        report_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload["run_id"],
                        payload["status"],
                        payload["version"],
                        payload["created_at"],
                        payload["updated_at"],
                        payload["started_at"],
                        payload["finished_at"],
                        payload["claimed_by"],
                        payload["claimed_at"],
                        payload["lease_expires_at"],
                        payload["attempt_count"],
                        payload["invoice_csv_path"],
                        payload["payment_csv_path"],
                        payload["error_message"],
                        payload["error_json"],
                        payload["report_json"],
                    ),
                )
        except sqlite3.Error as exc:
            raise RunStorageError(f"Failed to create reconciliation run: {exc}", run_id=run.run_id) from exc
        return run.model_copy(deep=True)

    def update_run(self, run: ReconciliationRun, *, expected_version: int) -> ReconciliationRun:
        if run.version != expected_version + 1:
            raise ValueError(
                f"Updated reconciliation run version must be expected_version + 1; "
                f"expected {expected_version + 1}, got {run.version}"
            )

        payload = self._serialize_run(run)
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    UPDATE reconciliation_runs
                    SET status = ?,
                        version = ?,
                        updated_at = ?,
                        started_at = ?,
                        finished_at = ?,
                        claimed_by = ?,
                        claimed_at = ?,
                        lease_expires_at = ?,
                        attempt_count = ?,
                        invoice_csv_path = ?,
                        payment_csv_path = ?,
                        error_message = ?,
                        error_json = ?,
                        report_json = ?
                    WHERE run_id = ?
                      AND version = ?
                    """,
                    (
                        payload["status"],
                        payload["version"],
                        payload["updated_at"],
                        payload["started_at"],
                        payload["finished_at"],
                        payload["claimed_by"],
                        payload["claimed_at"],
                        payload["lease_expires_at"],
                        payload["attempt_count"],
                        payload["invoice_csv_path"],
                        payload["payment_csv_path"],
                        payload["error_message"],
                        payload["error_json"],
                        payload["report_json"],
                        payload["run_id"],
                        expected_version,
                    ),
                )
                if cursor.rowcount == 0:
                    existing = connection.execute(
                        "SELECT version FROM reconciliation_runs WHERE run_id = ?",
                        (run.run_id,),
                    ).fetchone()
                    if existing is None:
                        raise KeyError(f"Reconciliation run not found: {run.run_id}")
                    raise ConcurrencyConflictError(
                        f"Reconciliation run version conflict: expected {expected_version}, "
                        f"found {existing['version']}",
                        run_id=run.run_id,
                    )
        except (KeyError, ConcurrencyConflictError):
            raise
        except sqlite3.Error as exc:
            raise RunStorageError(f"Failed to update reconciliation run: {exc}", run_id=run.run_id) from exc

        return run.model_copy(deep=True)

    def claim_run(
        self,
        *,
        run_id: str,
        worker_id: str,
        claimed_at: datetime,
        lease_expires_at: datetime,
        expected_version: int,
    ) -> ReconciliationRun:
        claimed_at_str = self._serialize_datetime(claimed_at)
        lease_expires_at_str = self._serialize_datetime(lease_expires_at)

        try:
            with self._connect() as connection:
                existing = connection.execute(
                    """
                    SELECT *
                    FROM reconciliation_runs
                    WHERE run_id = ?
                    """,
                    (run_id,),
                ).fetchone()
                if existing is None:
                    raise KeyError(f"Reconciliation run not found: {run_id}")

                if existing["version"] != expected_version:
                    raise ConcurrencyConflictError(
                        f"Reconciliation run version conflict: expected {expected_version}, "
                        f"found {existing['version']}",
                        run_id=run_id,
                    )

                if (
                    existing["claimed_by"] is not None
                    and existing["lease_expires_at"] is not None
                    and self._deserialize_datetime(existing["lease_expires_at"]) >= claimed_at
                ):
                    raise RunLeaseConflictError(
                        f"Reconciliation run is already leased by {existing['claimed_by']}",
                        run_id=run_id,
                    )

                cursor = connection.execute(
                    """
                    UPDATE reconciliation_runs
                    SET status = 'processing',
                        version = version + 1,
                        updated_at = ?,
                        started_at = COALESCE(started_at, ?),
                        claimed_by = ?,
                        claimed_at = ?,
                        lease_expires_at = ?,
                        attempt_count = attempt_count + 1
                    WHERE run_id = ?
                      AND version = ?
                    """,
                    (
                        claimed_at_str,
                        claimed_at_str,
                        worker_id,
                        claimed_at_str,
                        lease_expires_at_str,
                        run_id,
                        expected_version,
                    ),
                )
                if cursor.rowcount == 0:
                    refreshed = connection.execute(
                        "SELECT version FROM reconciliation_runs WHERE run_id = ?",
                        (run_id,),
                    ).fetchone()
                    if refreshed is None:
                        raise KeyError(f"Reconciliation run not found: {run_id}")
                    raise ConcurrencyConflictError(
                        f"Reconciliation run version conflict: expected {expected_version}, "
                        f"found {refreshed['version']}",
                        run_id=run_id,
                    )

                row = connection.execute(
                    """
                    SELECT
                        run_id,
                        status,
                        version,
                        created_at,
                        updated_at,
                        started_at,
                        finished_at,
                        claimed_by,
                        claimed_at,
                        lease_expires_at,
                        attempt_count,
                        invoice_csv_path,
                        payment_csv_path,
                        error_message,
                        error_json,
                        report_json
                    FROM reconciliation_runs
                    WHERE run_id = ?
                    """,
                    (run_id,),
                ).fetchone()
        except (KeyError, ConcurrencyConflictError, RunLeaseConflictError):
            raise
        except sqlite3.Error as exc:
            raise RunStorageError(f"Failed to claim reconciliation run: {exc}", run_id=run_id) from exc

        return self._deserialize_row(row)

    def heartbeat_run(
        self,
        *,
        run_id: str,
        worker_id: str,
        lease_expires_at: datetime,
        expected_version: int,
    ) -> ReconciliationRun:
        lease_expires_at_str = self._serialize_datetime(lease_expires_at)

        try:
            with self._connect() as connection:
                existing = connection.execute(
                    """
                    SELECT claimed_by, version
                    FROM reconciliation_runs
                    WHERE run_id = ?
                    """,
                    (run_id,),
                ).fetchone()
                if existing is None:
                    raise KeyError(f"Reconciliation run not found: {run_id}")
                if existing["version"] != expected_version:
                    raise ConcurrencyConflictError(
                        f"Reconciliation run version conflict: expected {expected_version}, "
                        f"found {existing['version']}",
                        run_id=run_id,
                    )
                if existing["claimed_by"] != worker_id:
                    raise RunLeaseConflictError(
                        f"Reconciliation run is not claimed by worker {worker_id}",
                        run_id=run_id,
                    )

                cursor = connection.execute(
                    """
                    UPDATE reconciliation_runs
                    SET version = version + 1,
                        updated_at = ?,
                        lease_expires_at = ?
                    WHERE run_id = ?
                      AND version = ?
                      AND claimed_by = ?
                    """,
                    (
                        lease_expires_at_str,
                        lease_expires_at_str,
                        run_id,
                        expected_version,
                        worker_id,
                    ),
                )
                if cursor.rowcount == 0:
                    refreshed = connection.execute(
                        "SELECT version FROM reconciliation_runs WHERE run_id = ?",
                        (run_id,),
                    ).fetchone()
                    if refreshed is None:
                        raise KeyError(f"Reconciliation run not found: {run_id}")
                    raise ConcurrencyConflictError(
                        f"Reconciliation run version conflict: expected {expected_version}, "
                        f"found {refreshed['version']}",
                        run_id=run_id,
                    )

                row = connection.execute(
                    """
                    SELECT
                        run_id,
                        status,
                        version,
                        created_at,
                        updated_at,
                        started_at,
                        finished_at,
                        claimed_by,
                        claimed_at,
                        lease_expires_at,
                        attempt_count,
                        invoice_csv_path,
                        payment_csv_path,
                        error_message,
                        error_json,
                        report_json
                    FROM reconciliation_runs
                    WHERE run_id = ?
                    """,
                    (run_id,),
                ).fetchone()
        except (KeyError, ConcurrencyConflictError, RunLeaseConflictError):
            raise
        except sqlite3.Error as exc:
            raise RunStorageError(f"Failed to heartbeat reconciliation run: {exc}", run_id=run_id) from exc

        return self._deserialize_row(row)

    def get_run(self, run_id: str) -> ReconciliationRun | None:
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT
                        run_id,
                        status,
                        version,
                        created_at,
                        updated_at,
                        started_at,
                        finished_at,
                        claimed_by,
                        claimed_at,
                        lease_expires_at,
                        attempt_count,
                        invoice_csv_path,
                        payment_csv_path,
                        error_message,
                        error_json,
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

        filter_values = _status_filter_values(status)
        if filter_values:
            placeholders = ", ".join("?" for _ in filter_values)
            where_clause = f"WHERE status IN ({placeholders})"
            parameters.extend(filter_values)

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
                        version,
                        created_at,
                        updated_at,
                        started_at,
                        finished_at,
                        claimed_by,
                        claimed_at,
                        lease_expires_at,
                        attempt_count,
                        invoice_csv_path,
                        payment_csv_path,
                        error_message,
                        error_json,
                        report_json
                    FROM reconciliation_runs
                    {where_clause}
                    ORDER BY created_at {order_by}, run_id {order_by}
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
                    version INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    started_at TEXT NULL,
                    finished_at TEXT NULL,
                    claimed_by TEXT NULL,
                    claimed_at TEXT NULL,
                    lease_expires_at TEXT NULL,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    invoice_csv_path TEXT NOT NULL,
                    payment_csv_path TEXT NOT NULL,
                    error_message TEXT NULL,
                    error_json TEXT NULL,
                    report_json TEXT NULL
                )
                """
            )
            self._ensure_version_and_lease_columns(connection)
            connection.execute(
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

    def _ensure_version_and_lease_columns(self, connection: sqlite3.Connection) -> None:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(reconciliation_runs)").fetchall()
        }
        if "version" not in columns:
            connection.execute(
                "ALTER TABLE reconciliation_runs ADD COLUMN version INTEGER NOT NULL DEFAULT 0"
            )
        if "claimed_by" not in columns:
            connection.execute("ALTER TABLE reconciliation_runs ADD COLUMN claimed_by TEXT NULL")
        if "claimed_at" not in columns:
            connection.execute("ALTER TABLE reconciliation_runs ADD COLUMN claimed_at TEXT NULL")
        if "lease_expires_at" not in columns:
            connection.execute("ALTER TABLE reconciliation_runs ADD COLUMN lease_expires_at TEXT NULL")
        if "attempt_count" not in columns:
            connection.execute(
                "ALTER TABLE reconciliation_runs ADD COLUMN attempt_count INTEGER NOT NULL DEFAULT 0"
            )
        if "error_json" not in columns:
            connection.execute("ALTER TABLE reconciliation_runs ADD COLUMN error_json TEXT NULL")

    def _ensure_schema_version(self, connection: sqlite3.Connection) -> None:
        row = connection.execute("SELECT schema_version FROM schema_meta LIMIT 1").fetchone()
        if row is None:
            connection.execute("INSERT INTO schema_meta (schema_version) VALUES (?)", (_SCHEMA_VERSION,))
            return

        if row[0] is None or row[0] < _SCHEMA_VERSION:
            connection.execute("UPDATE schema_meta SET schema_version = ?", (_SCHEMA_VERSION,))

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=_SQLITE_TIMEOUT_SECONDS,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute(f"PRAGMA busy_timeout={_SQLITE_BUSY_TIMEOUT_MS}")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute(f"PRAGMA journal_mode={_SQLITE_JOURNAL_MODE}")
        connection.execute(f"PRAGMA synchronous={_SQLITE_SYNCHRONOUS}")
        return connection

    def _serialize_run(self, run: ReconciliationRun) -> dict[str, str | int | None]:
        report_payload = None
        if run.report is not None:
            report_payload = json.dumps(
                {
                    "version": _REPORT_PAYLOAD_VERSION,
                    "payload": run.report.model_dump(mode="json"),
                }
            )

        error_payload = None
        if run.error is not None:
            error_payload = json.dumps(run.error.model_dump(mode="json"))

        return {
            "run_id": run.run_id,
            "status": run.status,
            "version": run.version,
            "created_at": self._serialize_datetime(run.created_at),
            "updated_at": self._serialize_datetime(run.updated_at),
            "started_at": self._serialize_optional_datetime(run.started_at),
            "finished_at": self._serialize_optional_datetime(run.finished_at),
            "claimed_by": run.claimed_by,
            "claimed_at": self._serialize_optional_datetime(run.claimed_at),
            "lease_expires_at": self._serialize_optional_datetime(run.lease_expires_at),
            "attempt_count": run.attempt_count,
            "invoice_csv_path": run.invoice_csv_path,
            "payment_csv_path": run.payment_csv_path,
            "error_message": run.error_message,
            "error_json": error_payload,
            "report_json": report_payload,
        }

    def _deserialize_row(self, row: sqlite3.Row) -> ReconciliationRun:
        report_json = row["report_json"]
        error_json = row["error_json"]
        payload = {
            "run_id": row["run_id"],
            "status": _normalize_legacy_run_status(row["status"]),
            "version": row["version"],
            "created_at": self._deserialize_datetime(row["created_at"]),
            "updated_at": self._deserialize_datetime(row["updated_at"]),
            "started_at": self._deserialize_optional_datetime(row["started_at"]),
            "finished_at": self._deserialize_optional_datetime(row["finished_at"]),
            "claimed_by": row["claimed_by"],
            "claimed_at": self._deserialize_optional_datetime(row["claimed_at"]),
            "lease_expires_at": self._deserialize_optional_datetime(row["lease_expires_at"]),
            "attempt_count": row["attempt_count"],
            "invoice_csv_path": row["invoice_csv_path"],
            "payment_csv_path": row["payment_csv_path"],
            "error": self._deserialize_error_payload(error_json),
            "error_message": row["error_message"],
            "report": self._deserialize_report_payload(report_json),
        }
        return ReconciliationRun.model_validate(payload)

    def _deserialize_error_payload(self, error_json: str | None) -> dict[str, Any] | None:
        if error_json is None:
            return None

        payload = json.loads(error_json)
        if not isinstance(payload, dict):
            raise ValueError("Error payload must be a JSON object")
        return payload

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