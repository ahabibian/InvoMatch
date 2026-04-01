from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"


class FinalDecisionType(str, Enum):
    MATCH = "MATCH"
    PARTIAL = "PARTIAL"
    UNMATCHED = "UNMATCHED"


class FinalizedReviewStatus(str, Enum):
    APPROVED = "APPROVED"
    MODIFIED = "MODIFIED"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class FinalizedInvoiceRef:
    invoice_id: str
    invoice_number: str
    invoice_date: date | None
    amount: Decimal
    currency: str
    vendor_name: str | None = None

    def __post_init__(self) -> None:
        if not self.invoice_id:
            raise ValueError("invoice_id is required")
        if not self.invoice_number:
            raise ValueError("invoice_number is required")
        if not self.currency:
            raise ValueError("currency is required")


@dataclass(frozen=True, slots=True)
class FinalizedPaymentRef:
    payment_id: str
    payment_date: date | None
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not self.payment_id:
            raise ValueError("payment_id is required")
        if not self.currency:
            raise ValueError("currency is required")


@dataclass(frozen=True, slots=True)
class FinalizedMatchMeta:
    confidence: Decimal | None
    method: str
    matched_amount: Decimal
    difference_amount: Decimal

    def __post_init__(self) -> None:
        if not self.method:
            raise ValueError("method is required")


@dataclass(frozen=True, slots=True)
class FinalizedReviewMeta:
    status: FinalizedReviewStatus
    reviewed_by: str | None
    reviewed_at: datetime | None


@dataclass(frozen=True, slots=True)
class FinalizedResult:
    result_id: str
    run_id: str
    decision_type: FinalDecisionType
    invoice: FinalizedInvoiceRef
    payments: tuple[FinalizedPaymentRef, ...]
    match: FinalizedMatchMeta
    review: FinalizedReviewMeta

    def __post_init__(self) -> None:
        if not self.result_id:
            raise ValueError("result_id is required")
        if not self.run_id:
            raise ValueError("run_id is required")
        if self.invoice is None:
            raise ValueError("invoice is required")
        if self.match is None:
            raise ValueError("match is required")
        if self.review is None:
            raise ValueError("review is required")

        if self.decision_type in {FinalDecisionType.MATCH, FinalDecisionType.PARTIAL} and not self.payments:
            raise ValueError("payments are required for MATCH and PARTIAL results")

        if self.decision_type is FinalDecisionType.UNMATCHED and self.match.matched_amount != Decimal("0"):
            raise ValueError("UNMATCHED results must have matched_amount == 0")

        if self.decision_type is FinalDecisionType.UNMATCHED and self.match.difference_amount != self.invoice.amount:
            raise ValueError("UNMATCHED results must have difference_amount equal to invoice.amount")

        if self.decision_type is FinalDecisionType.PARTIAL and self.match.matched_amount >= self.invoice.amount:
            raise ValueError("PARTIAL results must have matched_amount < invoice.amount")

        if self.decision_type is FinalDecisionType.MATCH and self.match.matched_amount != self.invoice.amount:
            raise ValueError("MATCH results must have matched_amount equal to invoice.amount")

        for payment in self.payments:
            if payment.currency != self.invoice.currency:
                raise ValueError("payment currency must match invoice currency")


@dataclass(frozen=True, slots=True)
class ExportSummary:
    total_invoices: int
    total_payments: int
    matched: int
    unmatched: int
    partial: int

    def __post_init__(self) -> None:
        for field_name in ("total_invoices", "total_payments", "matched", "unmatched", "partial"):
            if getattr(self, field_name) < 0:
                raise ValueError(f"{field_name} must be >= 0")


@dataclass(frozen=True, slots=True)
class ExportBundle:
    schema_version: str
    run_id: str
    status: str
    exported_at: datetime
    currency: str
    summary: ExportSummary
    results: tuple[FinalizedResult, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.schema_version:
            raise ValueError("schema_version is required")
        if not self.run_id:
            raise ValueError("run_id is required")
        if not self.status:
            raise ValueError("status is required")
        if not self.currency:
            raise ValueError("currency is required")
        if self.summary is None:
            raise ValueError("summary is required")


@dataclass(frozen=True, slots=True)
class ExportOutput:
    format: ExportFormat
    content_type: str
    filename: str | None
    body: bytes

    def __post_init__(self) -> None:
        if not self.content_type:
            raise ValueError("content_type is required")
        if self.body is None:
            raise ValueError("body is required")