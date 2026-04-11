from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InputType(StrEnum):
    JSON = "json"
    FILE = "file"


class InputSessionStatus(StrEnum):
    RECEIVED = "received"
    VALIDATED = "validated"
    REJECTED = "rejected"
    INGESTED = "ingested"
    RUN_CREATED = "run_created"
    FAILED = "failed"


class InputErrorType(StrEnum):
    VALIDATION = "validation_error"
    FILE = "file_error"
    PARSING = "parsing_error"
    MAPPING = "mapping_error"
    INGESTION = "ingestion_error"
    RUNTIME = "runtime_error"


@dataclass(slots=True)
class InputError:
    type: InputErrorType
    code: str
    message: str
    field: str | None = None
    details: dict[str, Any] = dc_field(default_factory=dict)


@dataclass(slots=True)
class InputSession:
    input_type: InputType
    status: InputSessionStatus = InputSessionStatus.RECEIVED
    input_id: str = dc_field(default_factory=lambda: str(uuid4()))
    source_filename: str | None = None
    source_content_type: str | None = None
    source_size_bytes: int | None = None
    validation_errors: list[InputError] = dc_field(default_factory=list)
    ingestion_batch_id: str | None = None
    run_id: str | None = None
    created_at: datetime = dc_field(default_factory=utc_now)
    updated_at: datetime = dc_field(default_factory=utc_now)

    def touch(self) -> None:
        self.updated_at = utc_now()

    def mark_validated(self) -> None:
        self.status = InputSessionStatus.VALIDATED
        self.touch()

    def mark_rejected(self, errors: list[InputError]) -> None:
        self.status = InputSessionStatus.REJECTED
        self.validation_errors = list(errors)
        self.touch()

    def mark_ingested(self, ingestion_batch_id: str) -> None:
        self.status = InputSessionStatus.INGESTED
        self.ingestion_batch_id = ingestion_batch_id
        self.touch()

    def mark_run_created(self, run_id: str) -> None:
        self.status = InputSessionStatus.RUN_CREATED
        self.run_id = run_id
        self.touch()

    def mark_failed(self, errors: list[InputError]) -> None:
        self.status = InputSessionStatus.FAILED
        self.validation_errors = list(errors)
        self.touch()