from pydantic import ValidationError
import pytest

from invomatch.domain.feedback.enums import PromotionStatus
from invomatch.services.feedback.records import (
    CandidateRuleRecommendationRecord,
    CorrectionEventRecord,
    LearningSignalRecord,
    RulePromotionRecord,
    RuleRollbackRecord,
)


def test_correction_event_record_accepts_valid_shape() -> None:
    record = CorrectionEventRecord(
        correction_id="corr-001",
        tenant_id="tenant-001",
        run_id="run-001",
        match_id="match-001",
        invoice_id="inv-001",
        correction_type="accept_match",
        reviewer_action="accept",
        reason_code="exact_match_confirmed",
        reviewer_id="rev-001",
        reviewer_role="finance-reviewer",
        original_decision="matched",
        original_confidence=0.91,
        corrected_confidence=0.95,
        feature_snapshot_id="snap-001",
        feature_snapshot_run_id="run-001",
        feature_snapshot_match_id="match-001",
        ui_version="ui-v1",
        engine_version="engine-v1",
        rule_version="rules-v1",
    )

    assert record.correction_id == "corr-001"


def test_correction_event_record_replacement_requires_both_payment_ids() -> None:
    with pytest.raises(ValidationError):
        CorrectionEventRecord(
            correction_id="corr-002",
            tenant_id="tenant-001",
            run_id="run-001",
            match_id="match-001",
            invoice_id="inv-001",
            correction_type="replace_match_target",
            reviewer_action="override",
            reason_code="wrong_payment_target",
            reviewer_id="rev-001",
            reviewer_role="finance-reviewer",
            original_decision="matched",
            original_confidence=0.91,
            feature_snapshot_id="snap-001",
            feature_snapshot_run_id="run-001",
            feature_snapshot_match_id="match-001",
            ui_version="ui-v1",
            engine_version="engine-v1",
            rule_version="rules-v1",
        )


def test_learning_signal_record_rejects_small_evidence_count() -> None:
    with pytest.raises(ValidationError):
        LearningSignalRecord(
            signal_id="sig-001",
            tenant_id="tenant-001",
            signal_type="vendor_alias_discovered",
            source_correction_ids=("corr-001", "corr-002"),
            source_match_ids=("match-001",),
            source_feature_snapshot_ids=("snap-001",),
            evidence_count=1,
            consistency_score=0.90,
            reviewer_weight_score=0.80,
            extraction_version="extract-v1",
        )


def test_candidate_rule_recommendation_record_requires_approver_when_active() -> None:
    with pytest.raises(ValidationError):
        CandidateRuleRecommendationRecord(
            recommendation_id="rec-001",
            tenant_id="tenant-001",
            signal_id="sig-001",
            status=PromotionStatus.ACTIVE,
            title="Promote alias rule",
            description="Activate vendor alias normalization rule.",
            minimum_evidence_required=5,
            replay_test_passed=True,
        )


def test_rule_promotion_record_accepts_valid_shape() -> None:
    record = RulePromotionRecord(
        promotion_id="prom-001",
        recommendation_id="rec-001",
        tenant_id="tenant-001",
        promoted_rule_version="rules-v2",
        approver_id="approver-001",
    )

    assert record.promoted_rule_version == "rules-v2"


def test_rule_rollback_record_requires_reason() -> None:
    with pytest.raises(ValidationError):
        RuleRollbackRecord(
            rollback_id="rb-001",
            recommendation_id="rec-001",
            tenant_id="tenant-001",
            rolled_back_rule_version="rules-v2",
            approver_id="approver-001",
            reason="",
        )