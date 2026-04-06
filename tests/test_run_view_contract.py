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
        self.storage_key = "internal/should_not_leak.csv"
        self.expires_at = datetime(2026, 5, 1, 0, 0, 0, tzinfo=UTC)


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
        self.source_reference = "internal-match-ref"


class FakeReviewItem:
    def __init__(self, review_item_id: str, feedback_id: str, item_status: str) -> None:
        self.review_item_id = review_item_id
        self.feedback_id = feedback_id
        self.item_status = item_status
        self.current_decision = None
        self.reviewed_payload = {"internal": "hidden"}


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


def _create_client() -> TestClient:
    run = FakeRun(
        run_id="run_contract",
        status="completed",
        report=FakeRunReport(matched=8, unmatched=1, ambiguous=1, total=10),
    )
    review_store = FakeReviewStore(
        feedbacks={
            "fb_1": FakeFeedback(
                feedback_id="fb_1",
                run_id="run_contract",
                raw_payload={"reason_code": "amount_mismatch", "internal_flag": "secret"},
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
            "run_contract": [
                FakeArtifact(
                    artifact_id="artifact_1",
                    run_id="run_contract",
                    created_at=datetime(2026, 4, 3, 11, 31, 0, tzinfo=UTC),
                    file_name="run_contract.csv",
                    status="READY",
                )
            ]
        }
    )

    app = FastAPI()
    app.include_router(router)
    app.state.run_registry = FakeRunRegistry(runs={"run_contract": run})
    app.state.review_store = review_store
    app.state.artifact_query_service = artifact_query_service
    app.state.export_readiness_evaluator = FakeExportReadinessEvaluator(is_export_ready=True)
    return TestClient(app)


def test_run_view_contract_has_expected_top_level_fields_only():
    client = _create_client()

    response = client.get("/api/reconciliation/runs/run_contract/view")

    assert response.status_code == 200
    body = response.json()

    assert set(body.keys()) == {
        "run_id",
        "status",
        "created_at",
        "updated_at",
        "match_summary",
        "review_summary",
        "export_summary",
        "artifacts",
    }


def test_run_view_contract_does_not_leak_internal_fields():
    client = _create_client()

    response = client.get("/api/reconciliation/runs/run_contract/view")

    assert response.status_code == 200
    body = response.json()
    serialized = str(body)

    assert "storage_key" not in serialized
    assert "expires_at" not in serialized
    assert "source_reference" not in serialized
    assert "reviewed_payload" not in serialized
    assert "internal_flag" not in serialized


def test_run_view_contract_artifact_shape_is_lightweight_and_product_safe():
    client = _create_client()

    response = client.get("/api/reconciliation/runs/run_contract/view")

    assert response.status_code == 200
    artifact = response.json()["artifacts"][0]

    assert set(artifact.keys()) == {
        "artifact_id",
        "kind",
        "file_name",
        "media_type",
        "size_bytes",
        "created_at",
        "download_url",
    }


def test_run_view_contract_exposes_only_allowed_export_summary_statuses():
    client = _create_client()

    response = client.get("/api/reconciliation/runs/run_contract/view")

    assert response.status_code == 200
    export_status = response.json()["export_summary"]["status"]

    assert export_status in {"not_ready", "ready", "exported", "failed"}