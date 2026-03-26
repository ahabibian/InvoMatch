from collections.abc import Sequence

from invomatch.domain.feedback.enums import PromotionStatus, SignalType
from invomatch.domain.feedback.models import (
    CandidateRuleRecommendation,
    CorrectionEvent,
    LearningSignal,
)
from invomatch.domain.feedback.repositories import FeedbackRepository
from invomatch.services.feedback.rule_recommendation import RuleRecommendationService


class InMemoryFeedbackRepository(FeedbackRepository):
    def __init__(self) -> None:
        self.corrections: dict[str, CorrectionEvent] = {}
        self.signals: dict[str, LearningSignal] = {}
        self.recommendations: dict[str, CandidateRuleRecommendation] = {}
        self.promotions: list[dict[str, str]] = []
        self.rollbacks: list[dict[str, str]] = []

    def save_correction_event(self, event: CorrectionEvent) -> None:
        self.corrections[event.correction_id] = event

    def get_correction_event(self, correction_id: str) -> CorrectionEvent | None:
        return self.corrections.get(correction_id)

    def list_correction_events_by_tenant(self, tenant_id: str) -> Sequence[CorrectionEvent]:
        return [event for event in self.corrections.values() if event.tenant_id == tenant_id]

    def list_correction_events_by_run(self, run_id: str) -> Sequence[CorrectionEvent]:
        return [event for event in self.corrections.values() if event.run_id == run_id]

    def list_correction_events_by_match(self, match_id: str) -> Sequence[CorrectionEvent]:
        return [event for event in self.corrections.values() if event.match_id == match_id]

    def save_learning_signal(self, signal: LearningSignal) -> None:
        self.signals[signal.signal_id] = signal

    def get_learning_signal(self, signal_id: str) -> LearningSignal | None:
        return self.signals.get(signal_id)

    def list_learning_signals_by_tenant(self, tenant_id: str) -> Sequence[LearningSignal]:
        return [signal for signal in self.signals.values() if signal.tenant_id == tenant_id]

    def save_candidate_rule_recommendation(
        self,
        recommendation: CandidateRuleRecommendation,
    ) -> None:
        self.recommendations[recommendation.recommendation_id] = recommendation

    def get_candidate_rule_recommendation(
        self,
        recommendation_id: str,
    ) -> CandidateRuleRecommendation | None:
        return self.recommendations.get(recommendation_id)

    def list_candidate_rule_recommendations_by_status(
        self,
        status: str,
    ) -> Sequence[CandidateRuleRecommendation]:
        return [
            recommendation
            for recommendation in self.recommendations.values()
            if recommendation.status == status
        ]

    def record_rule_promotion(
        self,
        recommendation_id: str,
        promoted_rule_version: str,
        approver_id: str,
    ) -> None:
        self.promotions.append(
            {
                "recommendation_id": recommendation_id,
                "promoted_rule_version": promoted_rule_version,
                "approver_id": approver_id,
            }
        )

    def record_rule_rollback(
        self,
        recommendation_id: str,
        rolled_back_rule_version: str,
        approver_id: str,
        reason: str,
    ) -> None:
        self.rollbacks.append(
            {
                "recommendation_id": recommendation_id,
                "rolled_back_rule_version": rolled_back_rule_version,
                "approver_id": approver_id,
                "reason": reason,
            }
        )


def build_signal() -> LearningSignal:
    return LearningSignal(
        signal_id="sig-001",
        tenant_id="tenant-001",
        signal_type=SignalType.VENDOR_ALIAS_DISCOVERED,
        source_correction_ids=("corr-001", "corr-002"),
        source_match_ids=("match-001", "match-002"),
        source_feature_snapshot_ids=("snap-001", "snap-002"),
        evidence_count=2,
        consistency_score=1.0,
        reviewer_weight_score=1.0,
        extraction_version="extract-v1",
        candidate_rule_payload={"alias": "AB Industriservice"},
    )


def test_create_candidate_from_signal_persists_candidate() -> None:
    repository = InMemoryFeedbackRepository()
    service = RuleRecommendationService(repository)

    signal = build_signal()
    recommendation = service.create_candidate_from_signal(
        signal,
        recommendation_id="rec-001",
        title="Vendor alias recommendation",
        description="Create candidate alias normalization rule.",
        minimum_evidence_required=2,
    )

    assert recommendation.status == PromotionStatus.CANDIDATE
    assert repository.get_candidate_rule_recommendation("rec-001") == recommendation


def test_promote_candidate_records_promotion() -> None:
    repository = InMemoryFeedbackRepository()
    service = RuleRecommendationService(repository)

    signal = build_signal()
    recommendation = service.create_candidate_from_signal(
        signal,
        recommendation_id="rec-002",
        title="Vendor alias recommendation",
        description="Create candidate alias normalization rule.",
        minimum_evidence_required=2,
    )

    active = service.promote_candidate(
        recommendation,
        promoted_rule_version="rules-v2",
        approver_id="approver-001",
    )

    assert active.status == PromotionStatus.ACTIVE
    assert repository.promotions[0]["promoted_rule_version"] == "rules-v2"


def test_rollback_candidate_records_rollback() -> None:
    repository = InMemoryFeedbackRepository()
    service = RuleRecommendationService(repository)

    signal = build_signal()
    recommendation = service.create_candidate_from_signal(
        signal,
        recommendation_id="rec-003",
        title="Vendor alias recommendation",
        description="Create candidate alias normalization rule.",
        minimum_evidence_required=2,
    )

    rolled_back = service.rollback_candidate(
        recommendation,
        rolled_back_rule_version="rules-v2",
        approver_id="approver-001",
        reason="false learning pattern",
    )

    assert rolled_back.status == PromotionStatus.ROLLED_BACK
    assert repository.rollbacks[0]["reason"] == "false learning pattern"