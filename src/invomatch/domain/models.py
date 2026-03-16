from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


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
