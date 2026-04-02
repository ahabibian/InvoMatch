from __future__ import annotations

import sqlite3
from datetime import UTC, datetime

from invomatch.domain.export_delivery.models import (
    ExportArtifact,
    ExportArtifactStatus,
    GenerationMode,
)
from invomatch.domain.export_delivery.repository import ExportArtifactRepository


class SqliteExportArtifactRepository(ExportArtifactRepository):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._initialize()

    def create(self, artifact: ExportArtifact) -> None:
        with self._connect() as conn:
            conn.execute(
                '''
                INSERT INTO export_artifacts (
                    id,
                    run_id,
                    format,
                    content_type,
                    file_name,
                    storage_backend,
                    storage_key,
                    byte_size,
                    checksum,
                    status,
                    created_at,
                    expires_at,
                    generation_mode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    artifact.id,
                    artifact.run_id,
                    artifact.format,
                    artifact.content_type,
                    artifact.file_name,
                    artifact.storage_backend,
                    artifact.storage_key,
                    artifact.byte_size,
                    artifact.checksum,
                    artifact.status.value,
                    self._serialize_datetime(artifact.created_at),
                    self._serialize_datetime(artifact.expires_at),
                    artifact.generation_mode.value,
                ),
            )
            conn.commit()

    def get_by_id(self, artifact_id: str) -> ExportArtifact | None:
        with self._connect() as conn:
            row = conn.execute(
                '''
                SELECT
                    id,
                    run_id,
                    format,
                    content_type,
                    file_name,
                    storage_backend,
                    storage_key,
                    byte_size,
                    checksum,
                    status,
                    created_at,
                    expires_at,
                    generation_mode
                FROM export_artifacts
                WHERE id = ?
                ''',
                (artifact_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_artifact(row)

    def get_latest_ready(
        self,
        run_id: str,
        format: str,
    ) -> ExportArtifact | None:
        with self._connect() as conn:
            row = conn.execute(
                '''
                SELECT
                    id,
                    run_id,
                    format,
                    content_type,
                    file_name,
                    storage_backend,
                    storage_key,
                    byte_size,
                    checksum,
                    status,
                    created_at,
                    expires_at,
                    generation_mode
                FROM export_artifacts
                WHERE run_id = ?
                  AND format = ?
                  AND status = ?
                ORDER BY created_at DESC, id DESC
                LIMIT 1
                ''',
                (run_id, format, ExportArtifactStatus.READY.value),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_artifact(row)

    def list_by_run(self, run_id: str) -> list[ExportArtifact]:
        with self._connect() as conn:
            rows = conn.execute(
                '''
                SELECT
                    id,
                    run_id,
                    format,
                    content_type,
                    file_name,
                    storage_backend,
                    storage_key,
                    byte_size,
                    checksum,
                    status,
                    created_at,
                    expires_at,
                    generation_mode
                FROM export_artifacts
                WHERE run_id = ?
                ORDER BY created_at DESC, id DESC
                ''',
                (run_id,),
            ).fetchall()

        return [self._row_to_artifact(row) for row in rows]

    def update_status(
        self,
        artifact_id: str,
        status: ExportArtifactStatus,
    ) -> ExportArtifact:
        existing = self.get_by_id(artifact_id)
        if existing is None:
            raise KeyError(f"export artifact not found: {artifact_id}")

        with self._connect() as conn:
            conn.execute(
                '''
                UPDATE export_artifacts
                SET status = ?
                WHERE id = ?
                ''',
                (status.value, artifact_id),
            )
            conn.commit()

        updated = self.get_by_id(artifact_id)
        if updated is None:
            raise KeyError(f"export artifact not found after update: {artifact_id}")

        return updated

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                '''
                CREATE TABLE IF NOT EXISTS export_artifacts (
                    id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    format TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    storage_backend TEXT NOT NULL,
                    storage_key TEXT NOT NULL,
                    byte_size INTEGER NULL,
                    checksum TEXT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NULL,
                    generation_mode TEXT NOT NULL
                )
                '''
            )
            conn.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_export_artifacts_run_format_status_created
                ON export_artifacts (run_id, format, status, created_at DESC)
                '''
            )
            conn.execute(
                '''
                CREATE INDEX IF NOT EXISTS idx_export_artifacts_run_created
                ON export_artifacts (run_id, created_at DESC)
                '''
            )
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_to_artifact(row: sqlite3.Row) -> ExportArtifact:
        return ExportArtifact(
            id=row["id"],
            run_id=row["run_id"],
            format=row["format"],
            content_type=row["content_type"],
            file_name=row["file_name"],
            storage_backend=row["storage_backend"],
            storage_key=row["storage_key"],
            byte_size=row["byte_size"],
            checksum=row["checksum"],
            status=ExportArtifactStatus(row["status"]),
            created_at=SqliteExportArtifactRepository._deserialize_datetime(row["created_at"]),
            expires_at=SqliteExportArtifactRepository._deserialize_datetime(row["expires_at"]),
            generation_mode=GenerationMode(row["generation_mode"]),
        )

    @staticmethod
    def _serialize_datetime(value: datetime | None) -> str | None:
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        else:
            value = value.astimezone(UTC)
        return value.isoformat()

    @staticmethod
    def _deserialize_datetime(value: str | None) -> datetime | None:
        if value is None:
            return None
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)