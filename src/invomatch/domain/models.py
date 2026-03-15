from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class Invoice(BaseModel):
    id: str
    date: date
    amount: Decimal


class Payment(BaseModel):
    id: str
    date: date
    amount: Decimal


class MatchResult(BaseModel):
    status: Literal["matched", "duplicate_detected", "partial_match", "unmatched"]
    payment_id: str | None = None
    duplicate_payment_ids: list[str] | None = None
    payment_ids: list[str] | None = None
    confidence_score: float
    confidence_explanation: str
