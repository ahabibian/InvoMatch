from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from invomatch.api.reconciliation_runs import router


class FakeRunReport:
    def __init__(self, matched=0, unmatched=0, ambiguous=0, total=0) -> None:
        self.matched = matched
        self.unmatched = unmatched
        self.ambiguous = ambiguous
        self.total = total


class FakeRun:
    def __init__(self, run_id: str, status: str, report=None) -> None:
        self.run_id = run_id
        self.status = status
        self.created_at = datetime(2026, 4, 3, 12, 0, 0, tzinfo=UTC)
        self.updated_at = datetime(2026, 4, 3, 12, 5, 0, tzinfo=UTC)
        self.report = report


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
        content_type: str = "text/csv",
        byte_size: int = 128,
        artifact_type: str = "run_export",
    ) -> None:
        self.id = artifact_id
        self.run_id = run_id
        self.created_at = created_at
        self.file_name = file_name
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


def create_test_client(
    registry: FakeRunRegistry,
    review_store=None,
    artifact_query_service=None,
) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.state.run_registry = registry
    app.state.review_store = review_store
    app.state.artifact_query_service = artifact_query_service
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
    assert body["match_summary"]["total_items"] == 10
    assert body["match_summary"]["matched_items"] == 7
    assert body["review_summary"]["status"] == "not_started"
    assert body["export_summary"]["status"] == "not_ready"
    assert body["artifacts"] == []


def test_get_run_view_returns_review_and_sorted_artifacts():
    run = FakeRun(run_id="run_456", status="completed")
    review_store = FakeReviewStore(
        feedbacks={
            "fb_1": FakeFeedback(
                feedback_id="fb_1",
                run_id="run_456",
                raw_payload={"reason_code": "amount_mismatch", "match_id": "match_1"},
            )
        },
        review_items=[
            FakeReviewItem(
                review_item_id="review_1",
                feedback_id="fb_1",
                item_status="APPROVED",
            )
        ],
    )
    artifact_query_service = FakeArtifactQueryService(
        artifacts_by_run={
            "run_456": [
                FakeArtifact(
                    artifact_id="artifact_b",
                    run_id="run_456",
                    created_at=datetime(2026, 4, 3, 11, 32, 0, tzinfo=UTC),
                    file_name="run_456_b.csv",
                ),
                FakeArtifact(
                    artifact_id="artifact_a",
                    run_id="run_456",
                    created_at=datetime(2026, 4, 3, 11, 31, 0, tzinfo=UTC),
                    file_name="run_456_a.csv",
                ),
            ]
        }
    )
    client = create_test_client(
        FakeRunRegistry(runs={"run_456": run}),
        review_store=review_store,
        artifact_query_service=artifact_query_service,
    )

    response = client.get("/api/reconciliation/runs/run_456/view")

    assert response.status_code == 200
    body = response.json()
    assert body["review_summary"]["status"] == "completed"
    assert body["review_summary"]["total_items"] == 1
    assert body["review_summary"]["resolved_items"] == 1
    assert body["export_summary"]["status"] == "exported"
    assert body["export_summary"]["artifact_count"] == 2
    assert [artifact["artifact_id"] for artifact in body["artifacts"]] == ["artifact_a", "artifact_b"]
    assert body["artifacts"][0]["download_url"] == "/api/reconciliation/exports/artifact_a/download"
