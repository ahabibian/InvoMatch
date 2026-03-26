from __future__ import annotations

from invomatch.domain.matching.decisioning import CandidateContext
from invomatch.domain.matching.models import DecisionType
from invomatch.domain.matching.rules import ScoreResult


def build_decision_summary(
    *,
    decision_type: DecisionType,
    score_result: ScoreResult,
    context: CandidateContext,
) -> str:
    if score_result.is_hard_blocked:
        return "Candidate rejected by policy due to a hard-block rule."

    if decision_type == DecisionType.ONE_TO_ONE:
        return "Candidate auto-approved due to strong score, strong evidence, and sufficient candidate separation."

    if decision_type == DecisionType.AMBIGUOUS:
        return "Multiple plausible candidates exist and the score separation is too small for automatic selection."

    if decision_type == DecisionType.REVIEW_REQUIRED:
        return "Candidate has meaningful evidence but not enough certainty for automatic approval."

    return "No reliable match candidate met the required confidence threshold."