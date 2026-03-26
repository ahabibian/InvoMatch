from __future__ import annotations

from invomatch.domain.matching.decisioning import CandidateContext
from invomatch.domain.matching.features import MatchFeatures
from invomatch.domain.matching.models import (
    ConfidenceLevel,
    DecisionProvenance,
    DecisionStatus,
    DecisionType,
    MatchDecision,
    MatchExplanation,
)
from invomatch.domain.matching.rules import ScoreResult
from invomatch.domain.matching.taxonomy import MismatchCode, TaxonomyResult
from invomatch.services.matching.explanations import build_decision_summary


class DecisionBuilder:
    def __init__(
        self,
        *,
        match_engine_version: str = "1.0.0",
        rule_set_version: str = "1.0.0",
        confidence_policy_version: str = "1.0.0",
        taxonomy_version: str = "1.0.0",
        feature_schema_version: str = "1.0.0",
    ) -> None:
        self._provenance = DecisionProvenance(
            match_engine_version=match_engine_version,
            rule_set_version=rule_set_version,
            confidence_policy_version=confidence_policy_version,
            taxonomy_version=taxonomy_version,
            feature_schema_version=feature_schema_version,
        )

    def build(
        self,
        *,
        decision_id: str,
        run_id: str,
        features: MatchFeatures,
        score_result: ScoreResult,
        context: CandidateContext | None = None,
    ) -> MatchDecision:
        candidate_context = context or CandidateContext()

        decision_type = self._classify_decision_type(score_result, candidate_context)
        confidence = self._classify_confidence(score_result, candidate_context, decision_type)
        status = self._classify_status(score_result, decision_type)
        auto_action_eligible = self._classify_auto_action_eligibility(
            score_result,
            candidate_context,
            decision_type,
            confidence,
        )
        taxonomy = self._classify_mismatch_codes(
            score_result,
            decision_type,
            candidate_context,
        )

        explanation = MatchExplanation(
            summary=build_decision_summary(
                decision_type=decision_type,
                score_result=score_result,
                context=candidate_context,
            ),
            reasons=score_result.reason_codes,
            penalties=score_result.penalty_codes + score_result.hard_block_codes,
            key_facts={
                **score_result.extracted_facts,
                "candidate_count": candidate_context.candidate_count,
                "competing_candidate_count": candidate_context.competing_candidate_count,
            },
            competing_candidate_count=candidate_context.competing_candidate_count,
            top_score_gap=candidate_context.top_score_gap,
        )

        invoice_ids = (features.invoice_id,) if features.invoice_id else ()
        payment_ids = (features.payment_id,) if features.payment_id else ()

        return MatchDecision(
            decision_id=decision_id,
            run_id=run_id,
            invoice_ids=invoice_ids,
            payment_ids=payment_ids,
            decision_type=decision_type,
            status=status,
            score=score_result.normalized_score,
            confidence=confidence,
            explanation=explanation,
            primary_mismatch_code=taxonomy.primary_code,
            secondary_mismatch_codes=taxonomy.secondary_codes,
            auto_action_eligible=auto_action_eligible,
            provenance=self._provenance,
        )

    def _classify_decision_type(
        self,
        score_result: ScoreResult,
        context: CandidateContext,
    ) -> DecisionType:
        if score_result.is_hard_blocked:
            return DecisionType.UNMATCHED

        if (
            context.competing_candidate_count > 0
            and context.top_score_gap is not None
            and context.top_score_gap < 10.0
            and score_result.normalized_score >= 70.0
        ):
            return DecisionType.AMBIGUOUS

        if score_result.normalized_score >= 90.0:
            return DecisionType.ONE_TO_ONE

        if score_result.normalized_score >= 60.0:
            return DecisionType.REVIEW_REQUIRED

        return DecisionType.UNMATCHED

    def _classify_confidence(
        self,
        score_result: ScoreResult,
        context: CandidateContext,
        decision_type: DecisionType,
    ) -> ConfidenceLevel:
        if score_result.is_hard_blocked:
            return ConfidenceLevel.REJECTED

        if decision_type == DecisionType.AMBIGUOUS:
            return ConfidenceLevel.MEDIUM

        if score_result.normalized_score >= 90.0:
            if context.top_score_gap is None or context.top_score_gap >= 15.0:
                return ConfidenceLevel.HIGH
            return ConfidenceLevel.MEDIUM

        if score_result.normalized_score >= 60.0:
            return ConfidenceLevel.MEDIUM

        return ConfidenceLevel.LOW

    def _classify_status(
        self,
        score_result: ScoreResult,
        decision_type: DecisionType,
    ) -> DecisionStatus:
        if score_result.is_hard_blocked:
            return DecisionStatus.REJECTED

        if decision_type == DecisionType.ONE_TO_ONE and score_result.normalized_score >= 90.0:
            return DecisionStatus.AUTO_APPROVED

        return DecisionStatus.PROPOSED

    def _classify_auto_action_eligibility(
        self,
        score_result: ScoreResult,
        context: CandidateContext,
        decision_type: DecisionType,
        confidence: ConfidenceLevel,
    ) -> bool:
        if score_result.is_hard_blocked:
            return False

        if decision_type != DecisionType.ONE_TO_ONE:
            return False

        if confidence != ConfidenceLevel.HIGH:
            return False

        if context.top_score_gap is not None and context.top_score_gap < 15.0:
            return False

        return True

    def _classify_mismatch_codes(
        self,
        score_result: ScoreResult,
        decision_type: DecisionType,
        context: CandidateContext,
    ) -> TaxonomyResult:
        if score_result.is_hard_blocked:
            if "currency_mismatch" in score_result.hard_block_codes:
                return TaxonomyResult(MismatchCode.CURRENCY_POLICY_REJECTED.value)
            return TaxonomyResult(
                MismatchCode.POLICY_REJECTED.value,
                tuple(score_result.hard_block_codes),
            )

        if decision_type == DecisionType.AMBIGUOUS:
            secondary: list[str] = []
            if context.competing_candidate_count > 0:
                secondary.append(MismatchCode.LOW_TOP_SCORE_GAP.value)
            return TaxonomyResult(
                MismatchCode.AMBIGUOUS_MULTIPLE_PAYMENTS.value,
                tuple(secondary),
            )

        if decision_type == DecisionType.REVIEW_REQUIRED:
            secondary: list[str] = []
            if "high_amount_drift" in score_result.penalty_codes:
                secondary.append(MismatchCode.HIGH_AMOUNT_DRIFT.value)
            if "payment_date_far_from_invoice_date" in score_result.penalty_codes:
                secondary.append(MismatchCode.EXCESSIVE_DATE_DRIFT.value)
            if "ocr_low_confidence" in score_result.penalty_codes:
                secondary.append(MismatchCode.OCR_LOW_CONFIDENCE.value)
            return TaxonomyResult(
                MismatchCode.WEAK_MATCH_SIGNAL.value,
                tuple(secondary),
            )

        if decision_type == DecisionType.UNMATCHED:
            secondary: list[str] = []
            if "high_amount_drift" in score_result.penalty_codes:
                secondary.append(MismatchCode.NO_CANDIDATE_AMOUNT.value)
            if "payment_date_far_from_invoice_date" in score_result.penalty_codes:
                secondary.append(MismatchCode.NO_CANDIDATE_DATE.value)
            if not secondary:
                secondary.append(MismatchCode.WEAK_REFERENCE_SIGNAL.value)
            return TaxonomyResult(secondary[0], tuple(secondary[1:]))

        return TaxonomyResult(None, ())