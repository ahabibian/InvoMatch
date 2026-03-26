from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MismatchCode(StrEnum):
    CURRENCY_POLICY_REJECTED = "CURRENCY_POLICY_REJECTED"
    POLICY_REJECTED = "POLICY_REJECTED"

    AMBIGUOUS_MULTIPLE_PAYMENTS = "AMBIGUOUS_MULTIPLE_PAYMENTS"
    LOW_TOP_SCORE_GAP = "LOW_TOP_SCORE_GAP"

    WEAK_MATCH_SIGNAL = "WEAK_MATCH_SIGNAL"
    HIGH_AMOUNT_DRIFT = "HIGH_AMOUNT_DRIFT"
    EXCESSIVE_DATE_DRIFT = "EXCESSIVE_DATE_DRIFT"
    OCR_LOW_CONFIDENCE = "OCR_LOW_CONFIDENCE"

    NO_CANDIDATE_AMOUNT = "NO_CANDIDATE_AMOUNT"
    NO_CANDIDATE_DATE = "NO_CANDIDATE_DATE"
    WEAK_REFERENCE_SIGNAL = "WEAK_REFERENCE_SIGNAL"


@dataclass(frozen=True, slots=True)
class TaxonomyResult:
    primary_code: str | None
    secondary_codes: tuple[str, ...] = ()