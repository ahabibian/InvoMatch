from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from invomatch.api.reconciliation_runs import router


class FakeRunError:
    def __init__(self, code: str, message: str, retryable: bool, terminal: bool) -> None:
        self.code = code
        self.message = message
        self.retryable = retryable
        self.terminal = terminal


class FakeRunReport:
    def __init__(self, matched=0, unmatched=0, ambiguous=0, total=0) -> None:
        self.matched = matched
        self.unmatched = unmatched
        self.ambiguous = ambiguous
        self.total = total


class FakeRun:
    def __init__(self, run_id: str, status: str, report=None, error=None, error_message=None) -> None:
        self.run_id = run_id
        self.status = status
        self.created_at = datetime(2026, 4, 3, 12, 0, 0, tzinfo=UTC)
        self.updated_at = datetime(2026, 4, 3, 12, 5, 0, tzinfo=UTC)
        self.report = report
        self.error = error
        self.error_message = error_message


class FakeRunRegistry:
    def __init__(self, runs: dict[str, FakeRun]) -> None:
        self._runs = runs

    def get_run(self, run_id: str):
        return self._runs.get(run_id)

    def list_runs(self, status=None, limit=50, offset=0, sort_order="desc"):
        runs = list(self._runs.values())
        return runs, len(runs)


class FakeArtifact:
    def __init__(
        self,
        artifact_id: str,
        run_id: str,
        created_at: datetime,
        file_name: str,
        status: str = "READY",
        content_type: str = "text/csv",
        byte_size: int = 128,
        artifact_type: str = "run_export",
    ) -> None:
        self.id = artifact_id
        self.run_id = run_id
        self.created_at = created_at
        self.file_name = file_name
        self.status = status
        self.content_type = content_type
        self.byte_size = byte_size
        self.artifact_type = artifact_type


class FakeArtifactQueryService:
    def __init__(self, artifacts_by_run: dict[str, list[FakeArtifact]]) -> None:
        self._artifacts_by_run = artifacts_by_run

    def list_artifacts_for_run(self, run_id: str):
        return list(self._artifacts_by_run.get(run_id, []))


class FakeFeedback:
    def __init__(self, feedback_id: str, run_id: str, raw_payload: dict | None = None) -> None:
        self.feedback_id = feedback_id
        self.run_id = run_id
        self.raw_payload = raw_payload or {}


class FakeReviewItem:
    def __init__(self, review_item_id: str, feedback_id: str, item_status: str, current_decision=None) -> None:
        self.review_item_id = review_item_id
        self.feedback_id = feedback_id
        self.item_status = item_status
        self.current_decision = current_decision


class FakeReviewStore:
    def __init__(self, feedbacks=None, review_items=None) -> None:
        self._feedbacks = feedbacks or {}
        self._review_items = review_items or []

    def get_feedback(self, feedback_id: str):
        return self._feedbacks.get(feedback_id)

    def list_review_items(self):
        return list(self._review_items)


class FakeExportReadinessResult:
    def __init__(self, is_export_ready: bool) -> None:
        self.is_export_ready = is_export_ready


class FakeExportReadinessEvaluator:
    def __init__(self, is_export_ready: bool) -> None:
        self._is_export_ready = is_export_ready

    def evaluate(self, run_id: str):
        return FakeExportReadinessResult(is_export_ready=self._is_export_ready)


def create_test_client(
    registry: FakeRunRegistry,
    review_store=None,
    artifact_query_service=None,
    export_readiness_evaluator=None,
) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.state.run_registry = registry
    app.state.review_store = review_store
    app.state.artifact_query_service = artifact_query_service
    app.state.export_readiness_evaluator = export_readiness_evaluator
    return TestClient(app)


def test_get_run_view_returns_404_when_run_missing():
    client = create_test_client(FakeRunRegistry(runs={}))

    response = client.get("/api/reconciliation/runs/missing/view")

    assert response.status_code == 404
    assert response.json()["detail"] == "Reconciliation run not found"


def test_get_run_view_returns_default_projection_shape():
    run = FakeRun(
        run_id="run_123",
        status="processing",
        report=FakeRunReport(matched=7, unmatched=2, ambiguous=1, total=10),
        error=None,
        error_message=None,
    )
    client = create_test_client(
        FakeRunRegistry(runs={"run_123": run}),
        review_store=FakeReviewStore(),
        artifact_query_service=FakeArtifactQueryService(artifacts_by_run={}),
    )

    response = client.get("/api/reconciliation/runs/run_123/view")

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == "run_123"
    assert body["status"] == "processing"
    assert body["error"] is None
    assert body["match_summary"]["total_items"] == 10
    assert body["match_summary"]["matched_items"] == 7
    assert body["review_summary"]["status"] == "not_started"
    assert body["review_summary"]["total_items"] == 0
    assert body["export_summary"]["status"] == "not_ready"
    assert body["artifacts"] == []


def test_get_run_view_returns_review_aggregate_and_newest_ready_artifact_first():
    run = FakeRun(run_id="run_456", status="completed", error=None, error_message=None)
    review_store = FakeReviewStore(
        feedbacks={
            "fb_1": FakeFeedback(feedback_id="fb_1", run_id="run_456", raw_payload={"reason_code": "amount_mismatch"}),
            "fb_2": FakeFeedback(feedback_id="fb_2", run_id="run_456", raw_payload={"reason_code": "date_mismatch"}),
            "fb_other": FakeFeedback(feedback_id="fb_other", run_id="other_run"),
        },
        review_items=[
            FakeReviewItem(review_item_id="review_1", feedback_id="fb_1", item_status="APPROVED"),
            FakeReviewItem(review_item_id="review_2", feedback_id="fb_2", item_status="DEFERRED"),
            FakeReviewItem(review_item_id="review_other", feedback_id="fb_other", item_status="IN_REVIEW"),
        ],
    )
    artifact_query_service = FakeArtifactQueryService(
        artifacts_by_run={
            "run_456": [
                FakeArtifact(
                    artifact_id="artifact_old_failed",
                    run_id="run_456",
                    created_at=datetime(2026, 4, 3, 11, 31, 0, tzinfo=UTC),
                    file_name="run_456_old.csv",
                    status="FAILED",
                ),
                FakeArtifact(
                    artifact_id="artifact_new_ready",
                    run_id="run_456",
                    created_at=datetime(2026, 4, 3, 11, 32, 0, tzinfo=UTC),
                    file_name="run_456_new.csv",
                    status="READY",
                ),
            ]
        }
    )
    client = create_test_client(
        FakeRunRegistry(runs={"run_456": run}),
        review_store=review_store,
        artifact_query_service=artifact_query_service,
        export_readiness_evaluator=FakeExportReadinessEvaluator(is_export_ready=False),
    )

    response = client.get("/api/reconciliation/runs/run_456/view")

    assert response.status_code == 200
    body = response.json()
    assert body["review_summary"]["status"] == "in_review"
    assert body["review_summary"]["total_items"] == 2
    assert body["review_summary"]["open_items"] == 1
    assert body["review_summary"]["resolved_items"] == 1
    assert body["review_summary"]["open_items"] + body["review_summary"]["resolved_items"] == body["review_summary"]["total_items"]
    assert body["export_summary"]["status"] == "exported"
    assert body["export_summary"]["artifact_count"] == 2
    assert [artifact["artifact_id"] for artifact in body["artifacts"]] == ["artifact_new_ready", "artifact_old_failed"]
    assert body["artifacts"][0]["download_url"] == "/api/reconciliation/exports/artifact_new_ready/download"
    assert body["artifacts"][1]["download_url"] is None


def test_get_run_view_returns_ready_when_export_evaluator_allows_but_no_ready_artifact_exists():
    run = FakeRun(run_id="run_ready", status="completed", error=None, error_message=None)
    client = create_test_client(
        FakeRunRegistry(runs={"run_ready": run}),
        review_store=FakeReviewStore(),
        artifact_query_service=FakeArtifactQueryService(artifacts_by_run={"run_ready": []}),
        export_readiness_evaluator=FakeExportReadinessEvaluator(is_export_ready=True),
    )

    response = client.get("/api/reconciliation/runs/run_ready/view")

    assert response.status_code == 200
    body = response.json()
    assert body["export_summary"]["status"] == "ready"
    assert body["export_summary"]["artifact_count"] == 0


def test_get_run_view_exposes_structured_error_for_failed_run():
    run = FakeRun(
        run_id="run_failed",
        status="failed",
        report=None,
        error=FakeRunError(
            code="retry_exhausted",
            message="retry limit reached",
            retryable=False,
            terminal=True,
        ),
        error_message="[retry_exhausted] retry limit reached",
    )
    client = create_test_client(
        FakeRunRegistry(runs={"run_failed": run}),
        review_store=FakeReviewStore(),
        artifact_query_service=FakeArtifactQueryService(artifacts_by_run={}),
    )

    response = client.get("/api/reconciliation/runs/run_failed/view")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["error"] == {
        "code": "retry_exhausted",
        "message": "retry limit reached",
        "retryable": False,
        "terminal": True,
    }