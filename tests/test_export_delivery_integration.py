from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from invomatch.api.export import export_reconciliation_run
from invomatch.domain.review.models import DecisionType, FeedbackRecord
from invomatch.main import create_app
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import JsonRunStore


def _request(app):
    return SimpleNamespace(app=app)


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


def _make_isolated_app(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "runs.json")
    review_store = InMemoryReviewStore()
    app = create_app(
        run_store=run_store,
        review_store=review_store,
        export_base_dir=tmp_path / "exports",
    )
    return SimpleNamespace(
        app=app,
        run_store=run_store,
        review_store=review_store,
    )


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


def _create_exportable_run(
    tmp_path: Path,
    run_store: JsonRunStore,
    review_store,
):
    invoice, payment = _write_files(tmp_path)

    run = reconcile_and_save(
        invoice_csv_path=invoice,
        payment_csv_path=payment,
        run_store=run_store,
    )
    _seed_approved_review(review_store, run)
    return run


def test_export_creates_and_reuses_artifact(tmp_path: Path):
    deps = _make_isolated_app(tmp_path)
    app = deps.app
    run_store = deps.run_store
    review_store = deps.review_store
    run = _create_exportable_run(tmp_path, run_store, review_store)

    response1 = export_reconciliation_run(
        run.run_id,
        format="json",
        request=_request(app),
    )
    response2 = export_reconciliation_run(
        run.run_id,
        format="json",
        request=_request(app),
    )

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.body == response2.body


def test_export_creates_file_on_disk(tmp_path: Path):
    deps = _make_isolated_app(tmp_path)
    app = deps.app
    run_store = deps.run_store
    review_store = deps.review_store
    export_root = tmp_path / "exports"
    run = _create_exportable_run(tmp_path, run_store, review_store)

    export_reconciliation_run(
        run.run_id,
        format="json",
        request=_request(app),
    )

    files = list(export_root.rglob("*"))
    assert any(f.suffix == ".json" for f in files)


def test_export_supports_multiple_formats(tmp_path: Path):
    deps = _make_isolated_app(tmp_path)
    app = deps.app
    run_store = deps.run_store
    review_store = deps.review_store
    run = _create_exportable_run(tmp_path, run_store, review_store)

    json_response = export_reconciliation_run(
        run.run_id,
        format="json",
        request=_request(app),
    )
    csv_response = export_reconciliation_run(
        run.run_id,
        format="csv",
        request=_request(app),
    )

    assert json_response.media_type == "application/json"
    assert csv_response.media_type == "text/csv"
    assert json_response.body != csv_response.body


def test_export_payload_is_valid_json(tmp_path: Path):
    deps = _make_isolated_app(tmp_path)
    app = deps.app
    run_store = deps.run_store
    review_store = deps.review_store
    run = _create_exportable_run(tmp_path, run_store, review_store)

    response = export_reconciliation_run(
        run.run_id,
        format="json",
        request=_request(app),
    )

    payload = json.loads(response.body.decode("utf-8"))

    assert payload["run_id"] == run.run_id
    assert "results" in payload
    assert len(payload["results"]) == 1