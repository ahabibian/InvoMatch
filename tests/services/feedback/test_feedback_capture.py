from collections.abc import Sequence

from invomatch.domain.feedback.models import (
    CandidateRuleRecommendation,
    CorrectionEvent,
    FeatureSnapshotRef,
    LearningSignal,
)
from invomatch.domain.feedback.repositories import FeedbackRepository
from invomatch.services.feedback.feedback_capture import FeedbackCaptureService
from invomatch.domain.feedback.enums import (
    CorrectionType,
    ReasonCode,
    ReviewerAction,
)


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


def build_snapshot() -> FeatureSnapshotRef:
    return FeatureSnapshotRef(
        snapshot_id="snap-001",
        run_id="run-001",
        match_id="match-001",
        engine_version="engine-v1",
        rule_version="rules-v1",
    )


def build_event() -> CorrectionEvent:
    return CorrectionEvent(
        correction_id="corr-001",
        tenant_id="tenant-001",
        run_id="run-001",
        match_id="match-001",
        invoice_id="inv-001",
        correction_type=CorrectionType.ACCEPT_MATCH,
        reviewer_action=ReviewerAction.ACCEPT,
        reason_code=ReasonCode.EXACT_MATCH_CONFIRMED,
        reviewer_id="rev-001",
        reviewer_role="finance-reviewer",
        original_decision="matched",
        original_confidence=0.95,
        corrected_confidence=0.98,
        feature_snapshot_ref=build_snapshot(),
        ui_version="ui-v1",
        engine_version="engine-v1",
        rule_version="rules-v1",
    )


def test_feedback_capture_service_persists_event() -> None:
    repository = InMemoryFeedbackRepository()
    service = FeedbackCaptureService(repository)

    event = build_event()
    captured = service.capture(event)

    assert captured == event
    assert repository.get_correction_event("corr-001") == event