from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class ExportArtifactStatus(StrEnum):
    READY = "READY"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    DELETED = "DELETED"


class GenerationMode(StrEnum):
    SYNC = "SYNC"
    CACHED = "CACHED"


class ExportArtifact(BaseModel):
    model_config = ConfigDict(frozen=True, use_enum_values=False)

    id: str
    run_id: str
    format: str

    content_type: str
    file_name: str

    storage_backend: str
    storage_key: str

    byte_size: int | None = None
    checksum: str | None = None

    status: ExportArtifactStatus
    created_at: datetime
    expires_at: datetime | None = None

    generation_mode: GenerationMode

    @field_validator(
        "id",
        "run_id",
        "format",
        "content_type",
        "file_name",
        "storage_backend",
        "storage_key",
    )
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("value must not be blank")
        return normalized

    @field_validator("byte_size")
    @classmethod
    def _byte_size_must_be_non_negative(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("byte_size must be >= 0")
        return value

    @field_validator("created_at", "expires_at")
    @classmethod
    def _normalize_datetime(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def _validate_expiry_window(self) -> Self:
        if self.expires_at is not None and self.expires_at < self.created_at:
            raise ValueError("expires_at must be >= created_at")
        return self