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


class FakeReviewStoreMissingMethods:
    pass


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


def test_review_summary_degrades_to_not_started_when_review_store_interface_is_incomplete():
    service = RunViewQueryService(
        run_store=FakeRunStore(run=_run(status="processing")),
        review_store=FakeReviewStoreMissingMethods(),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.review_summary.status == "not_started"
    assert result.review_summary.total_items == 0
    assert result.review_summary.open_items == 0
    assert result.review_summary.resolved_items == 0


def test_review_summary_ignores_review_items_without_feedback():
    service = RunViewQueryService(
        run_store=FakeRunStore(run=_run(status="review_required")),
        review_store=FakeReviewStore(
            feedbacks={},
            review_items=[
                FakeReviewItem(
                    review_item_id="review_1",
                    feedback_id="missing_feedback",
                    item_status="IN_REVIEW",
                )
            ],
        ),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.review_summary.status == "not_started"
    assert result.review_summary.total_items == 0


def test_review_summary_ignores_review_items_for_other_runs():
    service = RunViewQueryService(
        run_store=FakeRunStore(run=_run(status="review_required")),
        review_store=FakeReviewStore(
            feedbacks={
                "fb_1": FakeFeedback(feedback_id="fb_1", run_id="other_run"),
            },
            review_items=[
                FakeReviewItem(
                    review_item_id="review_1",
                    feedback_id="fb_1",
                    item_status="IN_REVIEW",
                )
            ],
        ),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.review_summary.status == "not_started"
    assert result.review_summary.total_items == 0


def test_export_status_stays_not_ready_for_non_completed_run_even_with_failed_artifact():
    service = RunViewQueryService(
        run_store=FakeRunStore(run=_run(status="processing")),
        artifact_query_service=FakeArtifactQueryService(
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
        ),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.export_summary.status == "not_ready"
    assert result.export_summary.artifact_count == 1


def test_failed_export_is_only_reported_for_completed_export_eligible_run():
    service = RunViewQueryService(
        run_store=FakeRunStore(run=_run(status="completed")),
        review_store=FakeReviewStore(),
        artifact_query_service=FakeArtifactQueryService(
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
        ),
        export_readiness_evaluator=FakeExportReadinessEvaluator(is_export_ready=False),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.export_summary.status == "failed"
    assert result.export_summary.artifact_count == 1


def test_ready_artifact_still_wins_over_failed_artifact():
    service = RunViewQueryService(
        run_store=FakeRunStore(run=_run(status="completed")),
        artifact_query_service=FakeArtifactQueryService(
            artifacts_by_run={
                "run_123": [
                    FakeArtifact(
                        id="artifact_failed",
                        run_id="run_123",
                        created_at=datetime(2026, 4, 3, 12, 1, 0, tzinfo=UTC),
                        file_name="failed.csv",
                        status="FAILED",
                    ),
                    FakeArtifact(
                        id="artifact_ready",
                        run_id="run_123",
                        created_at=datetime(2026, 4, 3, 12, 2, 0, tzinfo=UTC),
                        file_name="ready.csv",
                        status="READY",
                    ),
                ]
            }
        ),
        export_readiness_evaluator=FakeExportReadinessEvaluator(is_export_ready=False),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.export_summary.status == "exported"
    assert result.export_summary.artifact_count == 2