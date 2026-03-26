from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class RuleEffect(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    HARD_BLOCK = "hard_block"


@dataclass(frozen=True, slots=True)
class RuleResult:
    rule_id: str
    effect: RuleEffect
    score_delta: float
    reason_code: str
    triggered: bool

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("rule_id must not be empty.")
        if not self.reason_code.strip():
            raise ValueError("reason_code must not be empty.")
        if self.score_delta < 0:
            raise ValueError("score_delta must be >= 0.")


@dataclass(frozen=True, slots=True)
class ScoreResult:
    raw_score: float
    normalized_score: float
    rule_results: tuple[RuleResult, ...] = ()
    reason_codes: tuple[str, ...] = ()
    penalty_codes: tuple[str, ...] = ()
    hard_block_codes: tuple[str, ...] = ()
    is_hard_blocked: bool = False
    extracted_facts: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.raw_score < 0:
            raise ValueError("raw_score must be >= 0.")
        if not (0.0 <= self.normalized_score <= 100.0):
            raise ValueError("normalized_score must be between 0.0 and 100.0.")
        if self.is_hard_blocked and not self.hard_block_codes:
            raise ValueError("hard_block_codes must be present when is_hard_blocked is True.")