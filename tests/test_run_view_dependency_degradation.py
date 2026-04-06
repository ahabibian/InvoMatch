from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from invomatch.services.run_view_query_service import RunViewQueryService


@dataclass
class FakeRun:
    run_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    report: object | None = None


class FakeRunStore:
    def __init__(self, run) -> None:
        self._run = run

    def get_run(self, run_id: str):
        if self._run.run_id != run_id:
            return None
        return self._run


class ExplodingArtifactQueryService:
    def list_artifacts_for_run(self, run_id: str):
        raise RuntimeError("artifact backend unavailable")


class FakeExportReadinessResult:
    def __init__(self, is_export_ready: bool) -> None:
        self.is_export_ready = is_export_ready


class FakeExportReadinessEvaluator:
    def __init__(self, is_export_ready: bool) -> None:
        self._is_export_ready = is_export_ready

    def evaluate(self, run_id: str):
        return FakeExportReadinessResult(self._is_export_ready)


def test_run_view_degrades_safely_when_artifact_backend_fails():
    run = FakeRun(
        run_id="run_123",
        status="completed",
        created_at=datetime(2026, 4, 3, 12, 0, 0, tzinfo=UTC),
        updated_at=datetime(2026, 4, 3, 12, 5, 0, tzinfo=UTC),
    )
    service = RunViewQueryService(
        run_store=FakeRunStore(run),
        artifact_query_service=ExplodingArtifactQueryService(),
        export_readiness_evaluator=FakeExportReadinessEvaluator(is_export_ready=True),
    )

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.run_id == "run_123"
    assert result.artifacts == []
    assert result.export_summary.status == "ready"
    assert result.export_summary.artifact_count == 0