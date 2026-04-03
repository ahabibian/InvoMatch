from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC

from invomatch.services.run_view_query_service import RunViewQueryService


@dataclass
class FakeRun:
    run_id: str
    status: str
    created_at: datetime
    updated_at: datetime


class FakeRunStore:
    def __init__(self, run=None) -> None:
        self._run = run

    def get_run(self, run_id: str):
        if self._run is None:
            return None
        if self._run.run_id != run_id:
            return None
        return self._run


def test_get_run_view_returns_none_when_run_missing():
    service = RunViewQueryService(run_store=FakeRunStore(run=None))

    result = service.get_run_view("missing-run")

    assert result is None


def test_get_run_view_returns_projection_with_explicit_defaults():
    run = FakeRun(
        run_id="run_123",
        status="processing",
        created_at=datetime(2026, 4, 3, 12, 0, 0, tzinfo=UTC),
        updated_at=datetime(2026, 4, 3, 12, 5, 0, tzinfo=UTC),
    )
    service = RunViewQueryService(run_store=FakeRunStore(run=run))

    result = service.get_run_view("run_123")

    assert result is not None
    assert result.run_id == "run_123"
    assert result.status == "processing"
    assert result.review_summary.status == "not_started"
    assert result.export_summary.status == "not_ready"
    assert result.artifacts == []
