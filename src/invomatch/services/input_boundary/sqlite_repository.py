from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from invomatch.domain.input_boundary.models import (
    InputError,
    InputErrorType,
    InputSession,
    InputSessionStatus,
    InputType,
)


class SqliteInputSessionRepository:
    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS input_sessions (
                    input_id TEXT PRIMARY KEY,
                    input_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source_filename TEXT NULL,
                    source_content_type TEXT NULL,
                    source_size_bytes INTEGER NULL,
                    validation_errors_json TEXT NOT NULL,
                    ingestion_batch_id TEXT NULL,
                    run_id TEXT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def create(self, session: InputSession) -> InputSession:
        stored = replace(session)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO input_sessions (
                    input_id,
                    input_type,
                    status,
                    source_filename,
                    source_content_type,
                    source_size_bytes,
                    validation_errors_json,
                    ingestion_batch_id,
                    run_id,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                ,
                self._to_row(stored),
            )
            connection.commit()
        return replace(stored)

    def save(self, session: InputSession) -> InputSession:
        stored = replace(session)
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE input_sessions
                SET input_type = ?,
                    status = ?,
                    source_filename = ?,
                    source_content_type = ?,
                    source_size_bytes = ?,
                    validation_errors_json = ?,
                    ingestion_batch_id = ?,
                    run_id = ?,
                    created_at = ?,
                    updated_at = ?
                WHERE input_id = ?
                """
                ,
                (
                    stored.input_type.value,
                    stored.status.value,
                    stored.source_filename,
                    stored.source_content_type,
                    stored.source_size_bytes,
                    self._serialize_errors(stored.validation_errors),
                    stored.ingestion_batch_id,
                    stored.run_id,
                    stored.created_at.isoformat(),
                    stored.updated_at.isoformat(),
                    stored.input_id,
                ),
            )
            connection.commit()
        return replace(stored)

    def get(self, input_id: str) -> InputSession | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM input_sessions WHERE input_id = ?",
                (input_id,),
            ).fetchone()

        if row is None:
            return None

        return self._from_row(row)

    def get_by_input_id(self, input_id: str) -> InputSession | None:
        return self.get(input_id)

    def _to_row(self, session: InputSession) -> tuple:
        return (
            session.input_id,
            session.input_type.value,
            session.status.value,
            session.source_filename,
            session.source_content_type,
            session.source_size_bytes,
            self._serialize_errors(session.validation_errors),
            session.ingestion_batch_id,
            session.run_id,
            session.created_at.isoformat(),
            session.updated_at.isoformat(),
        )

    def _from_row(self, row: sqlite3.Row) -> InputSession:
        return InputSession(
            input_id=row["input_id"],
            input_type=InputType(row["input_type"]),
            status=InputSessionStatus(row["status"]),
            source_filename=row["source_filename"],
            source_content_type=row["source_content_type"],
            source_size_bytes=row["source_size_bytes"],
            validation_errors=self._deserialize_errors(row["validation_errors_json"]),
            ingestion_batch_id=row["ingestion_batch_id"],
            run_id=row["run_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _serialize_errors(self, errors: list[InputError]) -> str:
        return json.dumps(
            [
                {
                    "type": error.type.value,
                    "code": error.code,
                    "message": error.message,
                    "field": error.field,
                    "details": error.details,
                }
                for error in errors
            ],
            sort_keys=True,
        )

    def _deserialize_errors(self, payload: str) -> list[InputError]:
        data = json.loads(payload)
        return [
            InputError(
                type=InputErrorType(item["type"]),
                code=item["code"],
                message=item["message"],
                field=item.get("field"),
                details=item.get("details", {}),
            )
            for item in data
        ]