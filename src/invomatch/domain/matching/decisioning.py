from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CandidateContext:
    candidate_count: int = 1
    competing_candidate_count: int = 0
    top_score_gap: float | None = None

    def __post_init__(self) -> None:
        if self.candidate_count < 1:
            raise ValueError("candidate_count must be >= 1.")
        if self.competing_candidate_count < 0:
            raise ValueError("competing_candidate_count must be >= 0.")
        if self.top_score_gap is not None and self.top_score_gap < 0:
            raise ValueError("top_score_gap must be >= 0 when provided.")