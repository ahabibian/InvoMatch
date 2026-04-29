from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from invomatch.api.export import export_reconciliation_run
from invomatch.domain.review.models import DecisionType, FeedbackRecord
from invomatch.main import create_app
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.export.finalized_projection_writer import FinalizedProjectionWriter
from invomatch.services.reconciliation_runs import create_reconciliation_run
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import JsonRunStore


def _request_for_app(app, authorization: str | None = "Bearer operator-token") -> SimpleNamespace:
    headers = {}
    if authorization is not None:
        headers["Authorization"] = authorization

    return SimpleNamespace(
        app=app,
        headers=headers,
        method="GET",
        url=SimpleNamespace(path="/api/reconciliation/runs/test-run/export"),
    )


def _write_source_files(tmp_path: Path) -> tuple[Path, Path]:
    invoice_path = tmp_path / "invoices.csv"
    payment_path = tmp_path / "payments.csv"

    invoice_path.write_text(
        "\n".join(
            [
                "id,date,amount,currency,reference",
                "inv-1,2024-01-10,100.00,USD,INV-1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payment_path.write_text(
        "\n".join(
            [
                "id,date,amount,currency,reference,invoice_id",
                "pay-1,2024-01-12,100.00,USD,Payment for INV-1,inv-1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return invoice_path, payment_path


def _create_completed_run(tmp_path: Path, run_store: JsonRunStore):
    invoice_path, payment_path = _write_source_files(tmp_path)
    return reconcile_and_save(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )


@pytest.fixture
def isolated_export_app(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = InMemoryReviewStore()
    app = create_app(
        run_store=run_store,
        review_store=review_store,
    )
    return SimpleNamespace(
        app=app,
        run_store=run_store,
        review_store=review_store,
    )



def _persist_projection(app, review_store, run) -> None:
    writer = FinalizedProjectionWriter(
        projection_store=app.state.finalized_projection_store,
        review_store=review_store,
    )
    writer.persist_for_completed_run(run)

def _seed_approved_review(review_store, run) -> None:
    review_service = ReviewService()

    session = review_service.create_review_session(created_by="system")
    review_store.save_review_session(session)

    for result in run.report.results:
        feedback = FeedbackRecord(
            feedback_id=f"fb_{result.invoice_id}",
            run_id=run.run_id,
            source_type="reconciliation_result",
            source_reference=result.invoice_id,
            feedback_type="manual_review",
            raw_payload={
                "invoice_id": result.invoice_id,
                "payment_ids": result.match_result.payment_ids or (
                    [result.match_result.payment_id] if result.match_result.payment_id else []
                ),
                "reason_code": "export_test",
            },
            submitted_by="system",
        )
        review_store.save_feedback(feedback)

        review_item, audit_event = review_service.create_review_item(
            feedback=feedback,
            review_session=session,
        )
        review_store.save_review_item(review_item)
        review_store.save_audit_event(audit_event)

        start_audit = review_service.start_review(
            feedback=feedback,
            review_item=review_item,
            reviewer_id="reviewer-1",
        )
        review_store.save_review_item(review_item)
        review_store.save_audit_event(start_audit)

        decision_result = review_service.apply_decision(
            feedback=feedback,
            review_item=review_item,
            reviewer_id="reviewer-1",
            decision=DecisionType.APPROVE,
            reason="approved for export",
        )
        review_store.save_review_item(decision_result.review_item)
        review_store.save_decision_event(decision_result.decision_event)
        review_store.save_audit_event(decision_result.audit_event)
        if decision_result.eligibility_record is not None:
            review_store.save_eligibility_record(decision_result.eligibility_record)


def test_export_route_returns_401_without_auth(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    app = create_app(run_store=run_store)

    with pytest.raises(HTTPException) as exc_info:
        export_reconciliation_run(
            "missing-run",
            format="json",
            request=_request_for_app(app, authorization=None),
        )

    assert exc_info.value.status_code == 401


def test_export_route_returns_404_for_missing_run(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    app = create_app(run_store=run_store)

    with pytest.raises(HTTPException) as exc_info:
        export_reconciliation_run(
            "missing-run",
            format="json",
            request=_request_for_app(app),
        )

    assert exc_info.value.status_code == 404


def test_export_route_returns_409_for_pending_run(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    invoice_path, payment_path = _write_source_files(tmp_path)
    pending_run = create_reconciliation_run(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )
    app = create_app(run_store=run_store)

    with pytest.raises(HTTPException) as exc_info:
        export_reconciliation_run(
            pending_run.run_id,
            format="json",
            request=_request_for_app(app),
        )

    assert exc_info.value.status_code == 409


def test_export_route_allows_export_for_completed_matched_run_without_review(
    tmp_path: Path,
    isolated_export_app,
):
    app = isolated_export_app.app
    run_store = isolated_export_app.run_store

    run = _create_completed_run(tmp_path, run_store)
    _persist_projection(app, isolated_export_app.review_store, run)

    response = export_reconciliation_run(
        run.run_id,
        format="json",
        request=_request_for_app(app),
    )

    assert response.status_code == 200
    assert response.media_type == "application/json"

    payload = json.loads(response.body.decode("utf-8"))
    assert payload["run_id"] == run.run_id
    assert len(payload["results"]) == 1
    assert payload["results"][0]["invoice"]["invoice_id"] == "inv-1"
    assert payload["results"][0]["review"]["status"] == "NOT_REQUIRED"


def test_export_route_returns_json_export_for_completed_reviewed_run(
    tmp_path: Path,
    isolated_export_app,
):
    app = isolated_export_app.app
    run_store = isolated_export_app.run_store
    review_store = isolated_export_app.review_store

    run = _create_completed_run(tmp_path, run_store)
    _seed_approved_review(review_store, run)
    _persist_projection(app, review_store, run)

    response = export_reconciliation_run(
        run.run_id,
        format="json",
        request=_request_for_app(app),
    )

    assert response.status_code == 200
    assert response.media_type == "application/json"
    assert "attachment; filename=" in response.headers["Content-Disposition"]

    payload = json.loads(response.body.decode("utf-8"))
    assert payload["run_id"] == run.run_id
    assert payload["schema_version"] == "1.0"
    assert payload["currency"] == "USD"
    assert len(payload["results"]) == 1
    assert payload["results"][0]["invoice"]["invoice_id"] == "inv-1"


def test_export_route_returns_csv_export_for_completed_reviewed_run(
    tmp_path: Path,
    isolated_export_app,
):
    app = isolated_export_app.app
    run_store = isolated_export_app.run_store
    review_store = isolated_export_app.review_store

    run = _create_completed_run(tmp_path, run_store)
    _seed_approved_review(review_store, run)
    _persist_projection(app, review_store, run)

    response = export_reconciliation_run(
        run.run_id,
        format="csv",
        request=_request_for_app(app),
    )

    assert response.status_code == 200
    assert response.media_type == "text/csv"
    assert "attachment; filename=" in response.headers["Content-Disposition"]

    body = response.body.decode("utf-8")
    assert "result_id,decision_type,invoice_id" in body
    assert "inv-1" in body