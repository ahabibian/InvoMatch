from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from invomatch.domain.feedback.models import (
    CandidateRuleRecommendation,
    CorrectionEvent,
    FeatureSnapshotRef,
    LearningSignal,
)
from invomatch.domain.feedback.repositories import FeedbackRepository

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS feedback_correction_events (
    correction_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    run_id TEXT NOT NULL,
    match_id TEXT NOT NULL,
    invoice_id TEXT NOT NULL,
    correction_type TEXT NOT NULL,
    reviewer_action TEXT NOT NULL,
    reason_code TEXT NOT NULL,
    reviewer_id TEXT NOT NULL,
    reviewer_role TEXT NOT NULL,
    occurred_at_utc TEXT NOT NULL,
    original_decision TEXT NOT NULL,
    original_confidence REAL NOT NULL,
    corrected_confidence REAL NULL,
    previous_payment_id TEXT NULL,
    corrected_payment_id TEXT NULL,
    feature_snapshot_id TEXT NOT NULL,
    feature_snapshot_run_id TEXT NOT NULL,
    feature_snapshot_match_id TEXT NOT NULL,
    ui_version TEXT NOT NULL,
    engine_version TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    notes TEXT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_correction_events_tenant
    ON feedback_correction_events (tenant_id, occurred_at_utc, correction_id);

CREATE INDEX IF NOT EXISTS idx_feedback_correction_events_run
    ON feedback_correction_events (run_id, occurred_at_utc, correction_id);

CREATE INDEX IF NOT EXISTS idx_feedback_correction_events_match
    ON feedback_correction_events (match_id, occurred_at_utc, correction_id);

CREATE TABLE IF NOT EXISTS feedback_learning_signals (
    signal_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    source_correction_ids_json TEXT NOT NULL,
    source_match_ids_json TEXT NOT NULL,
    source_feature_snapshot_ids_json TEXT NOT NULL,
    evidence_count INTEGER NOT NULL,
    consistency_score REAL NOT NULL,
    reviewer_weight_score REAL NOT NULL,
    extraction_version TEXT NOT NULL,
    candidate_rule_payload_json TEXT NOT NULL,
    extracted_at_utc TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_learning_signals_tenant
    ON feedback_learning_signals (tenant_id, extracted_at_utc, signal_id);

CREATE TABLE IF NOT EXISTS feedback_candidate_rule_recommendations (
    recommendation_id TEXT NOT NULL,
    version_no INTEGER NOT NULL,
    tenant_id TEXT NOT NULL,
    signal_id TEXT NOT NULL,
    status TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    candidate_rule_payload_json TEXT NOT NULL,
    minimum_evidence_required INTEGER NOT NULL,
    replay_test_passed INTEGER NOT NULL,
    approver_id TEXT NULL,
    created_at_utc TEXT NOT NULL,
    approved_at_utc TEXT NULL,
    PRIMARY KEY (recommendation_id, version_no)
);

CREATE INDEX IF NOT EXISTS idx_feedback_candidate_rule_recommendations_latest
    ON feedback_candidate_rule_recommendations (recommendation_id, version_no DESC);

CREATE INDEX IF NOT EXISTS idx_feedback_candidate_rule_recommendations_status
    ON feedback_candidate_rule_recommendations (status, created_at_utc, recommendation_id, version_no);

CREATE TABLE IF NOT EXISTS feedback_rule_promotions (
    promotion_id TEXT PRIMARY KEY,
    recommendation_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    promoted_rule_version TEXT NOT NULL,
    approver_id TEXT NOT NULL,
    promoted_at_utc TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_rule_promotions_recommendation
    ON feedback_rule_promotions (recommendation_id, promoted_at_utc, promotion_id);

CREATE TABLE IF NOT EXISTS feedback_rule_rollbacks (
    rollback_id TEXT PRIMARY KEY,
    recommendation_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    rolled_back_rule_version TEXT NOT NULL,
    approver_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    rolled_back_at_utc TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_rule_rollbacks_recommendation
    ON feedback_rule_rollbacks (recommendation_id, rolled_back_at_utc, rollback_id);
"""


class SqliteFeedbackRepository(FeedbackRepository):
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._bootstrap_schema()

    def save_correction_event(self, event: CorrectionEvent) -> None:
        sql = """
        INSERT INTO feedback_correction_events (
            correction_id,
            tenant_id,
            run_id,
            match_id,
            invoice_id,
            correction_type,
            reviewer_action,
            reason_code,
            reviewer_id,
            reviewer_role,
            occurred_at_utc,
            original_decision,
            original_confidence,
            corrected_confidence,
            previous_payment_id,
            corrected_payment_id,
            feature_snapshot_id,
            feature_snapshot_run_id,
            feature_snapshot_match_id,
            ui_version,
            engine_version,
            rule_version,
            notes,
            created_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        payload = (
            event.correction_id,
            event.tenant_id,
            event.run_id,
            event.match_id,
            event.invoice_id,
            event.correction_type.value,
            event.reviewer_action.value,
            event.reason_code.value,
            event.reviewer_id,
            event.reviewer_role,
            event.occurred_at_utc.isoformat(),
            event.original_decision,
            event.original_confidence,
            event.corrected_confidence,
            event.previous_payment_id,
            event.corrected_payment_id,
            event.feature_snapshot_ref.snapshot_id,
            event.feature_snapshot_ref.run_id,
            event.feature_snapshot_ref.match_id,
            event.ui_version,
            event.engine_version,
            event.rule_version,
            event.notes,
            event.occurred_at_utc.isoformat(),
        )
        self._execute_insert(sql, payload, "correction event")

    def get_correction_event(self, correction_id: str) -> CorrectionEvent | None:
        row = self._fetch_one(
            """
            SELECT *
            FROM feedback_correction_events
            WHERE correction_id = ?
            """,
            (correction_id,),
        )
        if row is None:
            return None
        return self._row_to_correction_event(row)

    def list_correction_events_by_tenant(self, tenant_id: str) -> tuple[CorrectionEvent, ...]:
        rows = self._fetch_all(
            """
            SELECT *
            FROM feedback_correction_events
            WHERE tenant_id = ?
            ORDER BY occurred_at_utc, correction_id
            """,
            (tenant_id,),
        )
        return tuple(self._row_to_correction_event(row) for row in rows)

    def list_correction_events_by_run(self, run_id: str) -> tuple[CorrectionEvent, ...]:
        rows = self._fetch_all(
            """
            SELECT *
            FROM feedback_correction_events
            WHERE run_id = ?
            ORDER BY occurred_at_utc, correction_id
            """,
            (run_id,),
        )
        return tuple(self._row_to_correction_event(row) for row in rows)

    def list_correction_events_by_match(self, match_id: str) -> tuple[CorrectionEvent, ...]:
        rows = self._fetch_all(
            """
            SELECT *
            FROM feedback_correction_events
            WHERE match_id = ?
            ORDER BY occurred_at_utc, correction_id
            """,
            (match_id,),
        )
        return tuple(self._row_to_correction_event(row) for row in rows)

    def save_learning_signal(self, signal: LearningSignal) -> None:
        sql = """
        INSERT INTO feedback_learning_signals (
            signal_id,
            tenant_id,
            signal_type,
            source_correction_ids_json,
            source_match_ids_json,
            source_feature_snapshot_ids_json,
            evidence_count,
            consistency_score,
            reviewer_weight_score,
            extraction_version,
            candidate_rule_payload_json,
            extracted_at_utc,
            created_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        payload = (
            signal.signal_id,
            signal.tenant_id,
            signal.signal_type.value,
            json.dumps(list(signal.source_correction_ids), separators=(",", ":")),
            json.dumps(list(signal.source_match_ids), separators=(",", ":")),
            json.dumps(list(signal.source_feature_snapshot_ids), separators=(",", ":")),
            signal.evidence_count,
            signal.consistency_score,
            signal.reviewer_weight_score,
            signal.extraction_version,
            json.dumps(signal.candidate_rule_payload, separators=(",", ":"), sort_keys=True),
            signal.extracted_at_utc.isoformat(),
            signal.extracted_at_utc.isoformat(),
        )
        self._execute_insert(sql, payload, "learning signal")

    def get_learning_signal(self, signal_id: str) -> LearningSignal | None:
        row = self._fetch_one(
            """
            SELECT *
            FROM feedback_learning_signals
            WHERE signal_id = ?
            """,
            (signal_id,),
        )
        if row is None:
            return None
        return self._row_to_learning_signal(row)

    def list_learning_signals_by_tenant(self, tenant_id: str) -> tuple[LearningSignal, ...]:
        rows = self._fetch_all(
            """
            SELECT *
            FROM feedback_learning_signals
            WHERE tenant_id = ?
            ORDER BY extracted_at_utc, signal_id
            """,
            (tenant_id,),
        )
        return tuple(self._row_to_learning_signal(row) for row in rows)

    def save_candidate_rule_recommendation(
        self,
        recommendation: CandidateRuleRecommendation,
    ) -> None:
        version_no = self._next_recommendation_version(recommendation.recommendation_id)
        sql = """
        INSERT INTO feedback_candidate_rule_recommendations (
            recommendation_id,
            version_no,
            tenant_id,
            signal_id,
            status,
            title,
            description,
            candidate_rule_payload_json,
            minimum_evidence_required,
            replay_test_passed,
            approver_id,
            created_at_utc,
            approved_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        payload = (
            recommendation.recommendation_id,
            version_no,
            recommendation.tenant_id,
            recommendation.signal_id,
            recommendation.status.value,
            recommendation.title,
            recommendation.description,
            json.dumps(recommendation.candidate_rule_payload, separators=(",", ":"), sort_keys=True),
            recommendation.minimum_evidence_required,
            1 if recommendation.replay_test_passed else 0,
            recommendation.approver_id,
            recommendation.created_at_utc.isoformat(),
            recommendation.approved_at_utc.isoformat() if recommendation.approved_at_utc else None,
        )
        self._execute_insert(sql, payload, "candidate rule recommendation")

    def get_candidate_rule_recommendation(
        self,
        recommendation_id: str,
    ) -> CandidateRuleRecommendation | None:
        row = self._fetch_one(
            """
            SELECT *
            FROM feedback_candidate_rule_recommendations
            WHERE recommendation_id = ?
            ORDER BY version_no DESC
            LIMIT 1
            """,
            (recommendation_id,),
        )
        if row is None:
            return None
        return self._row_to_candidate_rule_recommendation(row)

    def list_candidate_rule_recommendations_by_status(
        self,
        status: str,
    ) -> tuple[CandidateRuleRecommendation, ...]:
        rows = self._fetch_all(
            """
            SELECT current.*
            FROM feedback_candidate_rule_recommendations AS current
            INNER JOIN (
                SELECT recommendation_id, MAX(version_no) AS max_version_no
                FROM feedback_candidate_rule_recommendations
                GROUP BY recommendation_id
            ) AS latest
                ON latest.recommendation_id = current.recommendation_id
               AND latest.max_version_no = current.version_no
            WHERE current.status = ?
            ORDER BY current.created_at_utc, current.recommendation_id
            """,
            (status,),
        )
        return tuple(self._row_to_candidate_rule_recommendation(row) for row in rows)

    def record_rule_promotion(
        self,
        recommendation_id: str,
        promoted_rule_version: str,
        approver_id: str,
    ) -> None:
        tenant_id = self._get_recommendation_tenant_id(recommendation_id)
        sql = """
        INSERT INTO feedback_rule_promotions (
            promotion_id,
            recommendation_id,
            tenant_id,
            promoted_rule_version,
            approver_id,
            promoted_at_utc,
            created_at_utc
        ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        self._execute_insert(
            sql,
            (
                f"prom-{uuid4().hex}",
                recommendation_id,
                tenant_id,
                promoted_rule_version,
                approver_id,
            ),
            "rule promotion",
        )

    def record_rule_rollback(
        self,
        recommendation_id: str,
        rolled_back_rule_version: str,
        approver_id: str,
        reason: str,
    ) -> None:
        tenant_id = self._get_recommendation_tenant_id(recommendation_id)
        sql = """
        INSERT INTO feedback_rule_rollbacks (
            rollback_id,
            recommendation_id,
            tenant_id,
            rolled_back_rule_version,
            approver_id,
            reason,
            rolled_back_at_utc,
            created_at_utc
        ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        self._execute_insert(
            sql,
            (
                f"rb-{uuid4().hex}",
                recommendation_id,
                tenant_id,
                rolled_back_rule_version,
                approver_id,
                reason,
            ),
            "rule rollback",
        )

    def _bootstrap_schema(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(SCHEMA_SQL)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        return connection

    def _fetch_one(self, sql: str, params: tuple[object, ...]) -> sqlite3.Row | None:
        with self._connect() as connection:
            cursor = connection.execute(sql, params)
            return cursor.fetchone()

    def _fetch_all(self, sql: str, params: tuple[object, ...]) -> list[sqlite3.Row]:
        with self._connect() as connection:
            cursor = connection.execute(sql, params)
            return list(cursor.fetchall())

    def _execute_insert(
        self,
        sql: str,
        params: tuple[object, ...],
        entity_name: str,
    ) -> None:
        try:
            with self._connect() as connection:
                connection.execute(sql, params)
                connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"failed to persist {entity_name}: {exc}") from exc

    def _next_recommendation_version(self, recommendation_id: str) -> int:
        row = self._fetch_one(
            """
            SELECT COALESCE(MAX(version_no), 0) AS max_version_no
            FROM feedback_candidate_rule_recommendations
            WHERE recommendation_id = ?
            """,
            (recommendation_id,),
        )
        if row is None:
            return 1
        return int(row["max_version_no"]) + 1

    def _get_recommendation_tenant_id(self, recommendation_id: str) -> str:
        row = self._fetch_one(
            """
            SELECT tenant_id
            FROM feedback_candidate_rule_recommendations
            WHERE recommendation_id = ?
            ORDER BY version_no DESC
            LIMIT 1
            """,
            (recommendation_id,),
        )
        if row is None:
            raise ValueError(
                f"cannot record audit event for unknown recommendation_id={recommendation_id}"
            )
        return str(row["tenant_id"])

    @staticmethod
    def _row_to_correction_event(row: sqlite3.Row) -> CorrectionEvent:
        snapshot = FeatureSnapshotRef(
            snapshot_id=str(row["feature_snapshot_id"]),
            run_id=str(row["feature_snapshot_run_id"]),
            match_id=str(row["feature_snapshot_match_id"]),
            engine_version=str(row["engine_version"]),
            rule_version=str(row["rule_version"]),
        )
        return CorrectionEvent(
            correction_id=str(row["correction_id"]),
            tenant_id=str(row["tenant_id"]),
            run_id=str(row["run_id"]),
            match_id=str(row["match_id"]),
            invoice_id=str(row["invoice_id"]),
            correction_type=str(row["correction_type"]),
            reviewer_action=str(row["reviewer_action"]),
            reason_code=str(row["reason_code"]),
            reviewer_id=str(row["reviewer_id"]),
            reviewer_role=str(row["reviewer_role"]),
            occurred_at_utc=str(row["occurred_at_utc"]),
            original_decision=str(row["original_decision"]),
            original_confidence=float(row["original_confidence"]),
            corrected_confidence=(
                None if row["corrected_confidence"] is None else float(row["corrected_confidence"])
            ),
            previous_payment_id=row["previous_payment_id"],
            corrected_payment_id=row["corrected_payment_id"],
            feature_snapshot_ref=snapshot,
            notes=row["notes"],
            ui_version=str(row["ui_version"]),
            engine_version=str(row["engine_version"]),
            rule_version=str(row["rule_version"]),
        )

    @staticmethod
    def _row_to_learning_signal(row: sqlite3.Row) -> LearningSignal:
        return LearningSignal(
            signal_id=str(row["signal_id"]),
            tenant_id=str(row["tenant_id"]),
            signal_type=str(row["signal_type"]),
            source_correction_ids=tuple(json.loads(str(row["source_correction_ids_json"]))),
            source_match_ids=tuple(json.loads(str(row["source_match_ids_json"]))),
            source_feature_snapshot_ids=tuple(json.loads(str(row["source_feature_snapshot_ids_json"]))),
            evidence_count=int(row["evidence_count"]),
            consistency_score=float(row["consistency_score"]),
            reviewer_weight_score=float(row["reviewer_weight_score"]),
            extracted_at_utc=str(row["extracted_at_utc"]),
            extraction_version=str(row["extraction_version"]),
            candidate_rule_payload=json.loads(str(row["candidate_rule_payload_json"])),
        )

    @staticmethod
    def _row_to_candidate_rule_recommendation(
        row: sqlite3.Row,
    ) -> CandidateRuleRecommendation:
        return CandidateRuleRecommendation(
            recommendation_id=str(row["recommendation_id"]),
            tenant_id=str(row["tenant_id"]),
            signal_id=str(row["signal_id"]),
            status=str(row["status"]),
            title=str(row["title"]),
            description=str(row["description"]),
            candidate_rule_payload=json.loads(str(row["candidate_rule_payload_json"])),
            minimum_evidence_required=int(row["minimum_evidence_required"]),
            replay_test_passed=bool(row["replay_test_passed"]),
            approver_id=row["approver_id"],
            created_at_utc=str(row["created_at_utc"]),
            approved_at_utc=row["approved_at_utc"],
        )