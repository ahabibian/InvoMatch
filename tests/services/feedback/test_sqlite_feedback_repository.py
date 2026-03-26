from __future__ import annotations

import sqlite3

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
from invomatch.services.feedback.sqlite_feedback_repository import (
    SCHEMA_SQL,
    SqliteFeedbackRepository,
)


def build_snapshot(snapshot_id: str, match_id: str) -> FeatureSnapshotRef:
    return FeatureSnapshotRef(
        snapshot_id=snapshot_id,
        run_id="run-001",
        match_id=match_id,
        engine_version="engine-v1",
        rule_version="rules-v1",
    )


def build_correction_event(
    correction_id: str,
    match_id: str,
    reason_code: ReasonCode = ReasonCode.EXACT_MATCH_CONFIRMED,
) -> CorrectionEvent:
    return CorrectionEvent(
        correction_id=correction_id,
        tenant_id="tenant-001",
        run_id="run-001",
        match_id=match_id,
        invoice_id=f"inv-{correction_id}",
        correction_type=CorrectionType.ACCEPT_MATCH,
        reviewer_action=ReviewerAction.ACCEPT,
        reason_code=reason_code,
        reviewer_id="rev-001",
        reviewer_role="finance-reviewer",
        original_decision="matched",
        original_confidence=0.94,
        corrected_confidence=0.97,
        feature_snapshot_ref=build_snapshot(f"snap-{correction_id}", match_id),
        ui_version="ui-v1",
        engine_version="engine-v1",
        rule_version="rules-v1",
    )


def build_learning_signal(signal_id: str) -> LearningSignal:
    return LearningSignal(
        signal_id=signal_id,
        tenant_id="tenant-001",
        signal_type=SignalType.VENDOR_ALIAS_DISCOVERED,
        source_correction_ids=("corr-001", "corr-002"),
        source_match_ids=("match-001", "match-002"),
        source_feature_snapshot_ids=("snap-001", "snap-002"),
        evidence_count=2,
        consistency_score=1.0,
        reviewer_weight_score=0.9,
        extraction_version="extract-v1",
        candidate_rule_payload={"alias": "AB Industriservice"},
    )


def build_recommendation(
    recommendation_id: str,
    status: PromotionStatus = PromotionStatus.CANDIDATE,
    replay_test_passed: bool = False,
    approver_id: str | None = None,
) -> CandidateRuleRecommendation:
    approved_at_utc = (
        "2026-03-26T12:00:00+00:00"
        if status in {PromotionStatus.APPROVED, PromotionStatus.ACTIVE}
        else None
    )

    return CandidateRuleRecommendation(
        recommendation_id=recommendation_id,
        tenant_id="tenant-001",
        signal_id="sig-001",
        status=status,
        title="Vendor alias recommendation",
        description="Create candidate alias normalization rule.",
        candidate_rule_payload={"alias": "AB Industriservice"},
        minimum_evidence_required=2,
        replay_test_passed=replay_test_passed,
        approver_id=approver_id,
        approved_at_utc=approved_at_utc,
    )


def test_correction_event_roundtrip_and_ordering(tmp_path) -> None:
    db_path = tmp_path / "feedback.sqlite3"
    repository = SqliteFeedbackRepository(str(db_path))

    event_a = build_correction_event("corr-001", "match-001")
    event_b = build_correction_event("corr-002", "match-001")

    repository.save_correction_event(event_a)
    repository.save_correction_event(event_b)

    loaded = repository.get_correction_event("corr-001")
    listed = repository.list_correction_events_by_match("match-001")

    assert loaded is not None
    assert loaded.correction_id == "corr-001"
    assert [item.correction_id for item in listed] == ["corr-001", "corr-002"]


def test_learning_signal_roundtrip(tmp_path) -> None:
    db_path = tmp_path / "feedback.sqlite3"
    repository = SqliteFeedbackRepository(str(db_path))

    signal = build_learning_signal("sig-001")
    repository.save_learning_signal(signal)

    loaded = repository.get_learning_signal("sig-001")
    listed = repository.list_learning_signals_by_tenant("tenant-001")

    assert loaded is not None
    assert loaded.signal_type == SignalType.VENDOR_ALIAS_DISCOVERED
    assert len(listed) == 1
    assert listed[0].signal_id == "sig-001"


def test_candidate_recommendation_is_versioned_append_only(tmp_path) -> None:
    db_path = tmp_path / "feedback.sqlite3"
    repository = SqliteFeedbackRepository(str(db_path))

    candidate = build_recommendation("rec-001")
    approved = build_recommendation(
        "rec-001",
        status=PromotionStatus.APPROVED,
        replay_test_passed=True,
        approver_id="approver-001",
    )

    repository.save_candidate_rule_recommendation(candidate)
    repository.save_candidate_rule_recommendation(approved)

    latest = repository.get_candidate_rule_recommendation("rec-001")
    approved_items = repository.list_candidate_rule_recommendations_by_status("approved")

    assert latest is not None
    assert latest.status == PromotionStatus.APPROVED
    assert len(approved_items) == 1
    assert approved_items[0].recommendation_id == "rec-001"

    connection = sqlite3.connect(str(db_path))
    try:
        version_count = connection.execute(
            "SELECT COUNT(*) FROM feedback_candidate_rule_recommendations WHERE recommendation_id = ?",
            ("rec-001",),
        ).fetchone()[0]
    finally:
        connection.close()

    assert version_count == 2


def test_promotion_and_rollback_are_persisted(tmp_path) -> None:
    db_path = tmp_path / "feedback.sqlite3"
    repository = SqliteFeedbackRepository(str(db_path))

    approved = build_recommendation(
        "rec-002",
        status=PromotionStatus.APPROVED,
        replay_test_passed=True,
        approver_id="approver-001",
    )
    repository.save_candidate_rule_recommendation(approved)

    repository.record_rule_promotion(
        recommendation_id="rec-002",
        promoted_rule_version="rules-v2",
        approver_id="approver-001",
    )
    repository.record_rule_rollback(
        recommendation_id="rec-002",
        rolled_back_rule_version="rules-v2",
        approver_id="approver-001",
        reason="false learning pattern",
    )

    connection = sqlite3.connect(str(db_path))
    try:
        promotion_count = connection.execute(
            "SELECT COUNT(*) FROM feedback_rule_promotions WHERE recommendation_id = ?",
            ("rec-002",),
        ).fetchone()[0]
        rollback_count = connection.execute(
            "SELECT COUNT(*) FROM feedback_rule_rollbacks WHERE recommendation_id = ?",
            ("rec-002",),
        ).fetchone()[0]
    finally:
        connection.close()

    assert promotion_count == 1
    assert rollback_count == 1


def test_schema_sql_contains_required_feedback_tables() -> None:
    assert "feedback_correction_events" in SCHEMA_SQL
    assert "feedback_learning_signals" in SCHEMA_SQL
    assert "feedback_candidate_rule_recommendations" in SCHEMA_SQL