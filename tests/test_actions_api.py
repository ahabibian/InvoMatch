from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from invomatch.api.actions import post_reconciliation_run_action
from invomatch.api.product_models.action import ProductActionRequest
from invomatch.domain.models import ReconciliationReport
from invomatch.services.action_service import ActionService
from invomatch.services.reconciliation_runs import (
    create_reconciliation_run,
    update_reconciliation_run,
)
from invomatch.services.run_store import JsonRunStore


def _request_with_action_service(action_service: ActionService) -> SimpleNamespace:
    app = SimpleNamespace(state=SimpleNamespace(action_service=action_service))
    return SimpleNamespace(app=app)


def test_post_reconciliation_run_action_accepts_resolve_review():
    request = _request_with_action_service(ActionService())

    response = post_reconciliation_run_action(
        "run-123",
        ProductActionRequest(
            action_type="resolve_review",
            target_id="case-1",
            payload={
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
            },
            note="resolved by reviewer",
        ),
        request=request,
    )

    assert response.run_id == "run-123"
    assert response.action_type == "resolve_review"
    assert response.accepted is True
    assert response.status == "accepted"


def test_post_reconciliation_run_action_accepts_export_run():
    run_store = JsonRunStore(Path("output") / "test_actions_api_runs.json")

    invoice_path = Path("output") / "test_actions_api_invoices.csv"
    payment_path = Path("output") / "test_actions_api_payments.csv"
    export_dir = Path("output") / "test_actions_api_exports"

    invoice_path.parent.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)

    invoice_path.write_text("invoice_id,amount\ninv-1,100\n", encoding="utf-8")
    payment_path.write_text("payment_id,amount\npay-1,100\n", encoding="utf-8")

    run = create_reconciliation_run(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )
    update_reconciliation_run(run.run_id, status="running", run_store=run_store)

    report = ReconciliationReport(
        total_invoices=1,
        matched=1,
        unmatched=0,
        duplicate_detected=0,
        partial_match=0,
        results=[],
    )
    completed = update_reconciliation_run(
        run.run_id,
        status="completed",
        report=report,
        run_store=run_store,
    )

    action_service = ActionService(
        run_store=run_store,
        export_base_dir=export_dir,
    )
    request = _request_with_action_service(action_service)

    response = post_reconciliation_run_action(
        completed.run_id,
        ProductActionRequest(
            action_type="export_run",
            target_id=None,
            payload={"format": "json"},
            note="export requested",
        ),
        request=request,
    )

    assert response.run_id == completed.run_id
    assert response.action_type == "export_run"
    assert response.accepted is True
    assert response.status == "accepted"


def test_post_reconciliation_run_action_rejects_invalid_resolve_review_payload():
    request = _request_with_action_service(ActionService())

    response = post_reconciliation_run_action(
        "run-123",
        ProductActionRequest(
            action_type="resolve_review",
            target_id="case-1",
            payload={},
            note="invalid request",
        ),
        request=request,
    )

    assert response.run_id == "run-123"
    assert response.action_type == "resolve_review"
    assert response.accepted is False
    assert response.status == "invalid_request"