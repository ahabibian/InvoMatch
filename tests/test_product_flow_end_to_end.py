from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from invomatch.api.product_models.action import ProductActionRequest
from invomatch.services.action_service import ActionService
from invomatch.services.actions.result import (
    ActionExecutionResult,
    ActionExecutionStatus,
)
from invomatch.services.review_store import InMemoryReviewStore


class StubRun:
    def __init__(self, run_id: str, status: str) -> None:
        self.run_id = run_id
        self.status = status


class StubRunStore:
    def __init__(self) -> None:
        self._runs = {
            "run-123": StubRun("run-123", "review_required"),
            "run-completed": StubRun("run-completed", "completed"),
        }

    def get_run(self, run_id: str):
        return self._runs.get(run_id)


def _resolve_payload() -> dict:
    return {
        "decision": "APPROVE",
        "reviewer_id": "reviewer-1",
        "feedback_id": "feedback-1",
        "review_session_id": "review-session-1",
        "review_item_id": "review-item-1",
        "source_type": "manual_review",
        "source_reference": "case-1",
        "feedback_type": "review_resolution",
        "raw_payload": {"matched": False},
        "submitted_by": "system",
        "feedback_status": "UNDER_REVIEW",
        "review_item_status": "IN_REVIEW",
    }


def test_product_flow_review_required_allows_resolve_review() -> None:
    service = ActionService(
        run_store=StubRunStore(),
        review_store=InMemoryReviewStore(),
    )

    result = service.execute(
        run_id="run-123",
        request=ProductActionRequest(
            action_type="resolve_review",
            target_id="case-1",
            payload=_resolve_payload(),
            note="review resolved",
        ),
    )

    assert result.accepted is True
    assert result.status == "accepted"


def test_product_flow_review_required_rejects_export_run() -> None:
    service = ActionService(
        run_store=StubRunStore(),
        review_store=InMemoryReviewStore(),
        export_base_dir=Path("output/test_exports_e2e"),
    )

    result = service.execute(
        run_id="run-123",
        request=ProductActionRequest(
            action_type="export_run",
            payload={"format": "json"},
            note="export too early",
        ),
    )

    assert result.accepted is False
    assert result.status == "conflict"


def test_product_flow_completed_allows_export_run() -> None:
    service = ActionService(
        run_store=StubRunStore(),
        review_store=InMemoryReviewStore(),
        export_base_dir=Path("output/test_exports_e2e"),
    )

    mocked_result = ActionExecutionResult(
        action_type="export_run",
        target_type="run",
        target_id="run-completed",
        status=ActionExecutionStatus.SUCCESS,
        state_changes=[],
        side_effects=[],
        audit_event_ids=[],
        response_payload={
            "run_id": "run-completed",
            "artifact_id": "artifact-123",
            "export_status": "ready",
            "export_format": "json",
            "content_type": "application/json",
            "file_name": "run-completed.json",
            "byte_size": 128,
        },
    )

    with patch(
        "invomatch.services.actions.handlers.export_run.ExportRunActionHandler.handle",
        return_value=mocked_result,
    ) as mocked_handle:
        result = service.execute(
            run_id="run-completed",
            request=ProductActionRequest(
                action_type="export_run",
                payload={"format": "json"},
                note="export ready",
            ),
        )

    assert mocked_handle.called is True
    assert result.accepted is True
    assert result.status == "accepted"


def test_product_flow_completed_rejects_resolve_review() -> None:
    service = ActionService(
        run_store=StubRunStore(),
        review_store=InMemoryReviewStore(),
    )

    result = service.execute(
        run_id="run-completed",
        request=ProductActionRequest(
            action_type="resolve_review",
            target_id="case-1",
            payload=_resolve_payload(),
            note="late review attempt",
        ),
    )

    assert result.accepted is False
    assert result.status == "conflict"