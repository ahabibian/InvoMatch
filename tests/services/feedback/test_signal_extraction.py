from collections.abc import Sequence

from invomatch.domain.feedback.enums import (
    CorrectionType,
    ReasonCode,
    ReviewerAction,
    SignalType,
)
from invomatch.domain.feedback.models import (
    CandidateRuleRecommendation,
    CorrectionEvent,
    FeatureSnapshotRef,
    LearningSignal,
)
from invomatch.domain.feedback.repositories import FeedbackRepository
from invomatch.services.feedback.signal_extraction import SignalExtractionService


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


def build_event(
    correction_id: str,
    match_id: str,
    reason_code: ReasonCode,
) -> CorrectionEvent:
    snapshot = FeatureSnapshotRef(
        snapshot_id=f"snap-{correction_id}",
        run_id="run-001",
        match_id=match_id,
        engine_version="engine-v1",
        rule_version="rules-v1",
    )
    return CorrectionEvent(
        correction_id=correction_id,
        tenant_id="tenant-001",
        run_id="run-001",
        match_id=match_id,
        invoice_id=f"inv-{correction_id}",
        correction_type=CorrectionType.REJECT_MATCH,
        reviewer_action=ReviewerAction.REJECT,
        reason_code=reason_code,
        reviewer_id="rev-001",
        reviewer_role="finance-reviewer",
        original_decision="matched",
        original_confidence=0.72,
        corrected_confidence=0.95,
        feature_snapshot_ref=snapshot,
        ui_version="ui-v1",
        engine_version="engine-v1",
        rule_version="rules-v1",
    )


def test_signal_extraction_groups_events_into_signal() -> None:
    repository = InMemoryFeedbackRepository()
    service = SignalExtractionService(repository, extraction_version="extract-v1")

    events = [
        build_event("corr-001", "match-001", ReasonCode.VENDOR_ALIAS_DISCOVERED),
        build_event("corr-002", "match-002", ReasonCode.VENDOR_ALIAS_DISCOVERED),
    ]

    signals = service.extract_from_events(events)

    assert len(signals) == 1
    assert signals[0].signal_type == SignalType.VENDOR_ALIAS_DISCOVERED
    assert signals[0].evidence_count == 2
    assert repository.get_learning_signal(signals[0].signal_id) == signals[0]


def test_signal_extraction_skips_unmapped_reason_codes() -> None:
    repository = InMemoryFeedbackRepository()
    service = SignalExtractionService(repository, extraction_version="extract-v1")

    events = [
        build_event("corr-003", "match-003", ReasonCode.FALSE_POSITIVE_MATCH),
    ]

    signals = service.extract_from_events(events)

    assert signals == []
    assert repository.signals == {}