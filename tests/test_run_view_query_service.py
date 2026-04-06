from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from invomatch.services.run_view_query_service import RunViewQueryService


@dataclass
class FakeRunReport:
    matched: int = 0
    unmatched: int = 0
    ambiguous: int = 0
    total: int = 0


@dataclass
class FakeRun:
    run_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    report: FakeRunReport | None = None


@dataclass
class FakeFeedback:
    feedback_id: str
    run_id: str


@dataclass
class FakeReviewItem:
    review_item_id: str
    feedback_id: str
    item_status: str


@dataclass
class FakeArtifact:
    id: str
    run_id: str
    created_at: datetime
    file_name: str
    status: str = "READY"
    content_type: str = "text/csv"
    byte_size: int = 128
    artifact_type: str = "run_export"


class FakeRunStore:
    def __init__(self, run=None) -> None:
        self._run = run

    def get_run(self, run_id: str):
        if self._run is None:
            return None
        if self._run.run_id != run_id:
            return None
        return self._run


class FakeReviewStore:
    def __init__(self, feedbacks=None, review_items=None) -> None:
        self._feedbacks = feedbacks or {}
        self._review_items = review_items or []

    def get_feedback(self, feedback_id: str):
        return self._feedbacks.get(feedback_id)

    def list_review_items(self):
        return list(self._review_items)


class FakeArtifactQueryService:
    def __init__(self, artifacts_by_run=None) -> None:
        self._artifacts_by_run = artifacts_by_run or {}

    def list_artifacts_for_run(self, run_id: str):
        return list(self._artifacts_by_run.get(run_id, []))


class FakeExportReadinessResult:
    def __init__(self, is_export_ready: bool) -> None:
        self.is_export_ready = is_export_ready


class FakeExportReadinessEvaluator:
    def __init__(self, is_export_ready: bool) -> None:
        self._is_export_ready = is_export_ready

    def evaluate(self, run_id: str):
        return FakeExportReadinessResult(is_export_ready=self._is_export_ready)


def _run(status: str = "processing", report: FakeRunReport | None = None) -> FakeRun:
    return FakeRun(
        run_id="run_123",
        status=status,
        created_at=datetime(2026, 4, 3, 12, 0, 0, tzinfo=UTC),
        updated_at=datetime(2026, 4, 3, 12, 5, 0, tzinfo=UTC),
        report=report,
    )


def test_get_run_view_returns_none_when_run_missing():
    service = RunViewQueryService(run_store=FakeRunStore(run=None))

    result = service.get_run_view("missing-run")

    assert result is None


def test_get_run_view_returns_projection_with_explicit_defaults():
    service = RunViewQueryService(run_store=FakeRunStore(run=_run(status="processing")))

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.run_id == "run_123"
    assert result.status == "processing"
    assert result.review_summary.status == "not_started"
    assert result.review_summary.total_items == 0
    assert result.export_summary.status == "not_ready"
    assert result.artifacts == []


def test_review_summary_treats_unknown_status_as_open():
    run = _run(status="review_required")
    review_store = FakeReviewStore(
        feedbacks={"fb_1": FakeFeedback(feedback_id="fb_1", run_id="run_123")},
        review_items=[
            FakeReviewItem(
                review_item_id="review_1",
                feedback_id="fb_1",
                item_status="WAITING_FOR_SOMETHING_UNKNOWN",
            )
        ],
    )
    service = RunViewQueryService(
        run_store=FakeRunStore(run=run),
        review_store=review_store,
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.review_summary.status == "in_review"
    assert result.review_summary.total_items == 1
    assert result.review_summary.open_items == 1
    assert result.review_summary.resolved_items == 0
    assert result.review_summary.open_items + result.review_summary.resolved_items == result.review_summary.total_items


def test_match_summary_uses_computed_total_when_report_total_is_too_small():
    run = _run(
        status="processing",
        report=FakeRunReport(matched=4, unmatched=3, ambiguous=2, total=5),
    )
    service = RunViewQueryService(run_store=FakeRunStore(run=run))

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.match_summary.matched_items == 4
    assert result.match_summary.unmatched_items == 3
    assert result.match_summary.ambiguous_items == 2
    assert result.match_summary.total_items == 9


def test_export_summary_is_not_ready_when_completed_but_evaluator_returns_false():
    run = _run(status="completed")
    service = RunViewQueryService(
        run_store=FakeRunStore(run=run),
        export_readiness_evaluator=FakeExportReadinessEvaluator(is_export_ready=False),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.export_summary.status == "not_ready"
    assert result.export_summary.artifact_count == 0


def test_export_summary_is_ready_when_completed_and_evaluator_returns_true():
    run = _run(status="completed")
    service = RunViewQueryService(
        run_store=FakeRunStore(run=run),
        export_readiness_evaluator=FakeExportReadinessEvaluator(is_export_ready=True),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.export_summary.status == "ready"
    assert result.export_summary.artifact_count == 0


def test_export_summary_is_exported_when_ready_artifact_exists():
    run = _run(status="completed")
    artifact_service = FakeArtifactQueryService(
        artifacts_by_run={
            "run_123": [
                FakeArtifact(
                    id="artifact_ready",
                    run_id="run_123",
                    created_at=datetime(2026, 4, 3, 12, 1, 0, tzinfo=UTC),
                    file_name="ready.csv",
                    status="READY",
                )
            ]
        }
    )
    service = RunViewQueryService(
        run_store=FakeRunStore(run=run),
        artifact_query_service=artifact_service,
        export_readiness_evaluator=FakeExportReadinessEvaluator(is_export_ready=False),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.export_summary.status == "exported"
    assert result.export_summary.artifact_count == 1
    assert result.artifacts[0].download_url == "/api/reconciliation/exports/artifact_ready/download"


def test_export_summary_is_failed_when_only_failed_artifacts_exist():
    run = _run(status="completed")
    artifact_service = FakeArtifactQueryService(
        artifacts_by_run={
            "run_123": [
                FakeArtifact(
                    id="artifact_failed",
                    run_id="run_123",
                    created_at=datetime(2026, 4, 3, 12, 1, 0, tzinfo=UTC),
                    file_name="failed.csv",
                    status="FAILED",
                )
            ]
        }
    )
    service = RunViewQueryService(
        run_store=FakeRunStore(run=run),
        artifact_query_service=artifact_service,
        export_readiness_evaluator=FakeExportReadinessEvaluator(is_export_ready=False),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.export_summary.status == "failed"
    assert result.export_summary.artifact_count == 1
    assert result.artifacts[0].download_url is None


def test_artifacts_are_sorted_newest_first():
    run = _run(status="completed")
    artifact_service = FakeArtifactQueryService(
        artifacts_by_run={
            "run_123": [
                FakeArtifact(
                    id="artifact_old",
                    run_id="run_123",
                    created_at=datetime(2026, 4, 3, 12, 1, 0, tzinfo=UTC),
                    file_name="old.csv",
                    status="READY",
                ),
                FakeArtifact(
                    id="artifact_new",
                    run_id="run_123",
                    created_at=datetime(2026, 4, 3, 12, 2, 0, tzinfo=UTC),
                    file_name="new.csv",
                    status="READY",
                ),
            ]
        }
    )
    service = RunViewQueryService(
        run_store=FakeRunStore(run=run),
        artifact_query_service=artifact_service,
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert [artifact.artifact_id for artifact in result.artifacts] == [
        "artifact_new",
        "artifact_old",
    ]