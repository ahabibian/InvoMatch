from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from invomatch.domain.feedback.models import (
    CandidateRuleRecommendation,
    CorrectionEvent,
    LearningSignal,
)


class FeedbackRepository(ABC):
    @abstractmethod
    def save_correction_event(self, event: CorrectionEvent) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_correction_event(self, correction_id: str) -> CorrectionEvent | None:
        raise NotImplementedError

    @abstractmethod
    def list_correction_events_by_tenant(self, tenant_id: str) -> Sequence[CorrectionEvent]:
        raise NotImplementedError

    @abstractmethod
    def list_correction_events_by_run(self, run_id: str) -> Sequence[CorrectionEvent]:
        raise NotImplementedError

    @abstractmethod
    def list_correction_events_by_match(self, match_id: str) -> Sequence[CorrectionEvent]:
        raise NotImplementedError

    @abstractmethod
    def save_learning_signal(self, signal: LearningSignal) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_learning_signal(self, signal_id: str) -> LearningSignal | None:
        raise NotImplementedError

    @abstractmethod
    def list_learning_signals_by_tenant(self, tenant_id: str) -> Sequence[LearningSignal]:
        raise NotImplementedError

    @abstractmethod
    def save_candidate_rule_recommendation(
        self,
        recommendation: CandidateRuleRecommendation,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_candidate_rule_recommendation(
        self,
        recommendation_id: str,
    ) -> CandidateRuleRecommendation | None:
        raise NotImplementedError

    @abstractmethod
    def list_candidate_rule_recommendations_by_status(
        self,
        status: str,
    ) -> Sequence[CandidateRuleRecommendation]:
        raise NotImplementedError

    @abstractmethod
    def record_rule_promotion(
        self,
        recommendation_id: str,
        promoted_rule_version: str,
        approver_id: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_rule_rollback(
        self,
        recommendation_id: str,
        rolled_back_rule_version: str,
        approver_id: str,
        reason: str,
    ) -> None:
        raise NotImplementedError