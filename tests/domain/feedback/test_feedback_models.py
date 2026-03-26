from pydantic import ValidationError
import pytest

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
    LearningSignal,
)


def build_snapshot() -> FeatureSnapshotRef:
    return FeatureSnapshotRef(
        snapshot_id="snap-001",
        run_id="run-001",
        match_id="match-001",
        engine_version="engine-v1",
        rule_version="rules-v1",
    )


def test_correction_event_accept_match_is_valid() -> None:
    event = CorrectionEvent(
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
        original_confidence=0.93,
        corrected_confidence=0.97,
        feature_snapshot_ref=build_snapshot(),
        ui_version="ui-v1",
        engine_version="engine-v1",
        rule_version="rules-v1",
    )

    assert event.correction_id == "corr-001"


def test_replace_match_target_requires_both_payment_ids() -> None:
    with pytest.raises(ValidationError):
        CorrectionEvent(
            correction_id="corr-002",
            tenant_id="tenant-001",
            run_id="run-001",
            match_id="match-001",
            invoice_id="inv-001",
            correction_type=CorrectionType.REPLACE_MATCH_TARGET,
            reviewer_action=ReviewerAction.OVERRIDE,
            reason_code=ReasonCode.WRONG_PAYMENT_TARGET,
            reviewer_id="rev-001",
            reviewer_role="finance-reviewer",
            original_decision="matched",
            original_confidence=0.91,
            corrected_confidence=0.96,
            feature_snapshot_ref=build_snapshot(),
            ui_version="ui-v1",
            engine_version="engine-v1",
            rule_version="rules-v1",
        )


def test_accept_match_requires_accept_action() -> None:
    with pytest.raises(ValidationError):
        CorrectionEvent(
            correction_id="corr-003",
            tenant_id="tenant-001",
            run_id="run-001",
            match_id="match-001",
            invoice_id="inv-001",
            correction_type=CorrectionType.ACCEPT_MATCH,
            reviewer_action=ReviewerAction.REJECT,
            reason_code=ReasonCode.EXACT_MATCH_CONFIRMED,
            reviewer_id="rev-001",
            reviewer_role="finance-reviewer",
            original_decision="matched",
            original_confidence=0.88,
            feature_snapshot_ref=build_snapshot(),
            ui_version="ui-v1",
            engine_version="engine-v1",
            rule_version="rules-v1",
        )


def test_learning_signal_requires_valid_evidence_alignment() -> None:
    signal = LearningSignal(
        signal_id="sig-001",
        tenant_id="tenant-001",
        signal_type=SignalType.VENDOR_ALIAS_DISCOVERED,
        source_correction_ids=("corr-001", "corr-002"),
        source_match_ids=("match-001",),
        source_feature_snapshot_ids=("snap-001",),
        evidence_count=2,
        consistency_score=0.95,
        reviewer_weight_score=0.80,
        extraction_version="extract-v1",
        candidate_rule_payload={"alias": "AB Industriservice"},
    )

    assert signal.signal_id == "sig-001"


def test_learning_signal_rejects_small_evidence_count() -> None:
    with pytest.raises(ValidationError):
        LearningSignal(
            signal_id="sig-002",
            tenant_id="tenant-001",
            signal_type=SignalType.VENDOR_ALIAS_DISCOVERED,
            source_correction_ids=("corr-001", "corr-002"),
            source_match_ids=("match-001",),
            source_feature_snapshot_ids=("snap-001",),
            evidence_count=1,
            consistency_score=0.95,
            reviewer_weight_score=0.80,
            extraction_version="extract-v1",
        )


def test_candidate_rule_recommendation_requires_approver_when_approved() -> None:
    with pytest.raises(ValidationError):
        CandidateRuleRecommendation(
            recommendation_id="rec-001",
            tenant_id="tenant-001",
            signal_id="sig-001",
            status=PromotionStatus.APPROVED,
            title="Vendor alias recommendation",
            description="Promote alias mapping for recurring supplier normalization.",
            minimum_evidence_required=5,
            replay_test_passed=True,
        )


def test_candidate_rule_recommendation_allows_active_with_approver_and_replay() -> None:
    recommendation = CandidateRuleRecommendation(
        recommendation_id="rec-002",
        tenant_id="tenant-001",
        signal_id="sig-001",
        status=PromotionStatus.ACTIVE,
        title="Vendor alias recommendation",
        description="Promote alias mapping for recurring supplier normalization.",
        minimum_evidence_required=5,
        replay_test_passed=True,
        approver_id="approver-001",
    )

    assert recommendation.status == PromotionStatus.ACTIVE