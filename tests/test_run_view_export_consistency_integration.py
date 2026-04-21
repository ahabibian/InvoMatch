from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from invomatch.domain.review.models import DecisionType, FeedbackRecord
from invomatch.main import create_app
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import JsonRunStore


def _write_files(tmp_path: Path):
    invoice = tmp_path / "invoices.csv"
    payment = tmp_path / "payments.csv"

    invoice.write_text(
        "id,date,amount,currency,reference\n"
        "inv-1,2024-01-10,100.00,USD,INV-1\n",
        encoding="utf-8",
    )

    payment.write_text(
        "id,date,amount,currency,reference,invoice_id\n"
        "pay-1,2024-01-12,100.00,USD,INV-1,inv-1\n",
        encoding="utf-8",
    )

    return invoice, payment


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


def test_run_view_reflects_exported_state_after_export_route_execution(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = InMemoryReviewStore()
    app = create_app(
        run_store=run_store,
        review_store=review_store,
        export_base_dir=tmp_path / "exports",
    )
    client = TestClient(app)

    invoice, payment = _write_files(tmp_path)
    run = reconcile_and_save(
        invoice_csv_path=invoice,
        payment_csv_path=payment,
        run_store=run_store,
    )
    _seed_approved_review(review_store, run)

    pre_export_view = client.get(f"/api/reconciliation/runs/{run.run_id}/view")
    assert pre_export_view.status_code == 200
    pre_body = pre_export_view.json()
    assert pre_body["export_summary"]["status"] in {"ready", "not_ready"}

    export_response = client.get(f"/api/reconciliation/runs/{run.run_id}/export?format=json")
    assert export_response.status_code == 200

    post_export_view = client.get(f"/api/reconciliation/runs/{run.run_id}/view")
    assert post_export_view.status_code == 200
    post_body = post_export_view.json()

    assert post_body["run_id"] == run.run_id
    assert post_body["export_summary"]["status"] == "exported"
    assert post_body["export_summary"]["artifact_count"] >= 1
    assert len(post_body["artifacts"]) >= 1
    assert post_body["artifacts"][0]["download_url"] is not None