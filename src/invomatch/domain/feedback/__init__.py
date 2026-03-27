"""Feedback domain package."""

from invomatch.domain.feedback.enums import (
    CorrectionType,
    PromotionStatus,
    ReasonCode,
    ReviewerAction,
    SignalType,
)
from invomatch.domain.feedback.models import (
    CandidateRuleRecommendation,
    CorrectionEvent,
    FeatureSnapshotRef,
    FeedbackRecord,
    LearningSignal,
)

__all__ = [
    "CorrectionType",
    "ReviewerAction",
    "ReasonCode",
    "SignalType",
    "PromotionStatus",
    "FeatureSnapshotRef",
    "CorrectionEvent",
    "LearningSignal",
    "CandidateRuleRecommendation",
    "FeedbackRecord",
]