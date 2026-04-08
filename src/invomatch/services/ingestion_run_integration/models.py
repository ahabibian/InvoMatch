from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IngestionRunStatus(str, Enum):
    RUN_CREATED = "run_created"
    RUN_REUSED = "run_reused"
    RUN_REJECTED = "run_rejected"
    RUN_FAILED = "run_failed"


class IdempotencyDecisionType(str, Enum):
    CREATE_NEW = "create_new"
    REUSE_EXISTING = "reuse_existing"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class IngestionTraceabilityContext:
    ingestion_batch_id: str
    accepted_invoice_count: int
    accepted_payment_count: int
    rejected_count: int
    conflict_count: int
    partial_ingestion: bool


@dataclass(frozen=True)
class RunCreationPolicyDecision:
    creatable: bool
    reason_code: str
    partial_ingestion: bool
    blocking_conflict: bool


@dataclass(frozen=True)
class IdempotencyDecision:
    decision: IdempotencyDecisionType
    existing_run_id: str | None
    reason_code: str


@dataclass(frozen=True)
class IngestionRunResult:
    status: IngestionRunStatus
    run_id: str | None
    reason_code: str
    ingestion_batch_id: str
    accepted_invoice_count: int
    accepted_payment_count: int
    rejected_count: int
    conflict_count: int
    partial_ingestion: bool