from __future__ import annotations

from invomatch.domain.feedback.enums import PromotionStatus
from invomatch.domain.feedback.models import CandidateRuleRecommendation, LearningSignal
from invomatch.domain.feedback.repositories import FeedbackRepository


class RuleRecommendationService:
    def __init__(self, repository: FeedbackRepository) -> None:
        self._repository = repository

    def create_candidate_from_signal(
        self,
        signal: LearningSignal,
        *,
        recommendation_id: str,
        title: str,
        description: str,
        minimum_evidence_required: int,
    ) -> CandidateRuleRecommendation:
        recommendation = CandidateRuleRecommendation(
            recommendation_id=recommendation_id,
            tenant_id=signal.tenant_id,
            signal_id=signal.signal_id,
            status=PromotionStatus.CANDIDATE,
            title=title,
            description=description,
            candidate_rule_payload=signal.candidate_rule_payload,
            minimum_evidence_required=minimum_evidence_required,
            replay_test_passed=False,
        )
        self._repository.save_candidate_rule_recommendation(recommendation)
        return recommendation

    def approve_candidate(
        self,
        recommendation: CandidateRuleRecommendation,
        *,
        approver_id: str,
    ) -> CandidateRuleRecommendation:
        approved = recommendation.model_copy(
            update={
                "status": PromotionStatus.APPROVED,
                "approver_id": approver_id,
                "replay_test_passed": True,
            }
        )
        self._repository.save_candidate_rule_recommendation(approved)
        return approved

    def promote_candidate(
        self,
        recommendation: CandidateRuleRecommendation,
        *,
        promoted_rule_version: str,
        approver_id: str,
    ) -> CandidateRuleRecommendation:
        active = recommendation.model_copy(
            update={
                "status": PromotionStatus.ACTIVE,
                "approver_id": approver_id,
                "replay_test_passed": True,
            }
        )
        self._repository.save_candidate_rule_recommendation(active)
        self._repository.record_rule_promotion(
            recommendation_id=active.recommendation_id,
            promoted_rule_version=promoted_rule_version,
            approver_id=approver_id,
        )
        return active

    def rollback_candidate(
        self,
        recommendation: CandidateRuleRecommendation,
        *,
        rolled_back_rule_version: str,
        approver_id: str,
        reason: str,
    ) -> CandidateRuleRecommendation:
        rolled_back = recommendation.model_copy(
            update={
                "status": PromotionStatus.ROLLED_BACK,
                "approver_id": approver_id,
            }
        )
        self._repository.save_candidate_rule_recommendation(rolled_back)
        self._repository.record_rule_rollback(
            recommendation_id=rolled_back.recommendation_id,
            rolled_back_rule_version=rolled_back_rule_version,
            approver_id=approver_id,
            reason=reason,
        )
        return rolled_back