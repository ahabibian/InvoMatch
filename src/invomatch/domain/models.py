from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

RunStatus = Literal["pending", "running", "completed", "failed"]


class Invoice(BaseModel):
    id: str
    date: date
    amount: Decimal
    reference: str | None = None


class Payment(BaseModel):
    id: str
    date: date
    amount: Decimal
    reference: str | None = None


class MatchResult(BaseModel):
    status: Literal["matched", "duplicate_detected", "partial_match", "unmatched"]
    payment_id: str | None = None
    duplicate_payment_ids: list[str] | None = None
    payment_ids: list[str] | None = None
    confidence_score: float
    confidence_explanation: str
    mismatch_reasons: list[
        Literal[
            "amount_match",
            "date_near",
            "date_far",
            "reference_match",
            "reference_missing",
            "duplicate_candidates",
            "partial_sum_match",
            "no_viable_candidate",
        ]
    ]


class ReconciliationResult(BaseModel):
    invoice_id: str
    match_result: MatchResult


class ReconciliationReport(BaseModel):
    total_invoices: int
    matched: int
    duplicate_detected: int
    partial_match: int
    unmatched: int
    results: list[ReconciliationResult]


class ReconciliationRun(BaseModel):
    run_id: str
    status: RunStatus
    version: int = 0
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    claimed_by: str | None = None
    claimed_at: datetime | None = None
    lease_expires_at: datetime | None = None
    attempt_count: int = 0
    invoice_csv_path: str
    payment_csv_path: str
    error_message: str | None = None
    report: ReconciliationReport | None = None


def is_terminal_status(status: RunStatus) -> bool:
    return status in {"completed", "failed"}


_ALLOWED_TRANSITIONS: dict[RunStatus, set[RunStatus]] = {
    "pending": {"pending", "running", "failed"},
    "running": {"running", "completed", "failed"},
    "completed": {"completed"},
    "failed": {"failed"},
}


def can_transition(current_status: RunStatus, next_status: RunStatus) -> bool:
    return next_status in _ALLOWED_TRANSITIONS[current_status]
