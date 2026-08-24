import csv
from functools import partial
from pathlib import Path

from fastapi.testclient import TestClient
from tests.helpers.security import TEST_AUTH_HEADER

from invomatch.domain.models import ReconciliationRun
from invomatch.main import create_app
from invomatch.services.ingestion_run_integration.runtime_adapter import (
    IngestionRunRuntimeAdapter,
)
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.sqlite_match_record_store import SqliteMatchRecordStore
from invomatch.services.sqlite_review_store import SqliteReviewStore
from invomatch.services.sqlite_run_store import SqliteRunStore


def _fake_run(run_id: str, batch_id: str) -> ReconciliationRun:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        run_id=run_id,
        tenant_id="tenant-test",
        status="completed",
        version=1,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=now,
        claimed_by=None,
        claimed_at=None,
        lease_expires_at=None,
        attempt_count=1,
        invoice_csv_path=f"output/ingestion_batches/{batch_id}/invoices.csv",
        payment_csv_path=f"output/ingestion_batches/{batch_id}/payments.csv",
        error_message=None,
        report=None,
    )


def test_post_ingest_creates_run(tmp_path: Path):
    app = create_app()

    def _reconcile_and_save(invoice_path: Path, payment_path: Path, **kwargs):
        assert invoice_path.exists()
        assert payment_path.exists()
        with payment_path.open(newline="", encoding="utf-8") as payment_file:
            payment_rows = list(csv.DictReader(payment_file))
        assert payment_rows[0]["invoice_id"] == "inv-1"
        assert kwargs["tenant_context"].tenant_id == "tenant-demo"
        return _fake_run("run-123", "batch-1")

    app.state.ingestion_run_runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=_reconcile_and_save,
        batch_root=tmp_path,
    )

    client = TestClient(app)

    response = client.post(
        "/api/reconciliation/runs/ingest",
        headers=TEST_AUTH_HEADER,
        json={
            "ingestion_batch_id": "batch-1",
            "invoices": [
                {
                    "id": "inv-1",
                    "date": "2026-04-08",
                    "amount": "100.00",
                    "currency": "SEK",
                    "reference": "REF-1",
                }
            ],
            "payments": [
                {
                    "id": "pay-1",
                    "invoice_id": "inv-1",
                    "date": "2026-04-08",
                    "amount": "100.00",
                    "currency": "SEK",
                    "reference": "REF-1",
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "run_created"
    assert body["run_id"] == "run-123"
    assert body["ingestion_batch_id"] == "batch-1"
    assert body["accepted_invoice_count"] == 1
    assert body["accepted_payment_count"] == 1


def test_post_ingest_preserves_invoice_binding_for_review_required_run(tmp_path: Path):
    run_store = SqliteRunStore(tmp_path / "runs.sqlite3")
    review_store = SqliteReviewStore(tmp_path / "reviews.sqlite3")
    app = create_app(run_store=run_store, review_store=review_store)
    app.state.ingestion_run_runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=partial(
            reconcile_and_save,
            run_store=run_store,
            match_record_store=SqliteMatchRecordStore(tmp_path / "matches.sqlite3"),
            review_store=review_store,
        ),
        batch_root=tmp_path / "batches",
    )
    client = TestClient(app)

    response = client.post(
        "/api/reconciliation/runs/ingest",
        headers=TEST_AUTH_HEADER,
        json={
            "ingestion_batch_id": "scenario-15-api",
            "invoices": [
                {
                    "id": "scenario-15-invoice",
                    "date": "2026-08-24",
                    "amount": "125.50",
                    "currency": "EUR",
                    "reference": "SCENARIO-15",
                }
            ],
            "payments": [
                {
                    "id": payment_id,
                    "invoice_id": "scenario-15-invoice",
                    "date": "2026-08-24",
                    "amount": "125.50",
                    "currency": "EUR",
                    "reference": "SCENARIO-15",
                }
                for payment_id in ("scenario-15-payment-a", "scenario-15-payment-b")
            ],
        },
    )

    assert response.status_code == 200
    run_id = response.json()["run_id"]
    detail_response = client.get(
        f"/api/reconciliation/runs/{run_id}", headers=TEST_AUTH_HEADER
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["status"] == "review_required"


def test_post_ingest_reuses_existing_run_for_same_batch(tmp_path: Path):
    app = create_app()

    def _reconcile_and_save(invoice_path: Path, payment_path: Path, **kwargs):
        assert kwargs["tenant_context"].tenant_id == "tenant-demo"
        return _fake_run("run-123", "batch-1")

    app.state.ingestion_run_runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=_reconcile_and_save,
        batch_root=tmp_path,
    )

    client = TestClient(app)

    payload = {
        "ingestion_batch_id": "batch-1",
        "invoices": [
            {
                "id": "inv-1",
                "date": "2026-04-08",
                "amount": "100.00",
                "currency": "SEK",
                "reference": "REF-1",
            }
        ],
        "payments": [
            {
                "id": "pay-1",
                "date": "2026-04-08",
                "amount": "100.00",
                "currency": "SEK",
                "reference": "REF-1",
            }
        ],
    }

    first = client.post("/api/reconciliation/runs/ingest", json=payload, headers=TEST_AUTH_HEADER)
    second = client.post("/api/reconciliation/runs/ingest", json=payload, headers=TEST_AUTH_HEADER)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["status"] == "run_created"
    assert second.json()["status"] == "run_reused"
    assert second.json()["run_id"] == "run-123"
def test_post_ingest_rejects_when_invoices_missing(tmp_path: Path):
    app = create_app()

    def _reconcile_and_save(invoice_path: Path, payment_path: Path, **kwargs):
        raise AssertionError("reconcile_and_save should not be called")

    app.state.ingestion_run_runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=_reconcile_and_save,
        batch_root=tmp_path,
    )

    client = TestClient(app)

    response = client.post(
        "/api/reconciliation/runs/ingest",
        headers=TEST_AUTH_HEADER,
        json={
            "ingestion_batch_id": "batch-no-invoices",
            "invoices": [],
            "payments": [
                {
                    "id": "pay-1",
                    "date": "2026-04-08",
                    "amount": "100.00",
                    "currency": "SEK",
                    "reference": "REF-1",
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "run_rejected"
    assert body["reason_code"] == "no_accepted_invoices"
    assert body["run_id"] is None


def test_post_ingest_rejects_when_payments_missing(tmp_path: Path):
    app = create_app()

    def _reconcile_and_save(invoice_path: Path, payment_path: Path, **kwargs):
        raise AssertionError("reconcile_and_save should not be called")

    app.state.ingestion_run_runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=_reconcile_and_save,
        batch_root=tmp_path,
    )

    client = TestClient(app)

    response = client.post(
        "/api/reconciliation/runs/ingest",
        headers=TEST_AUTH_HEADER,
        json={
            "ingestion_batch_id": "batch-no-payments",
            "invoices": [
                {
                    "id": "inv-1",
                    "date": "2026-04-08",
                    "amount": "100.00",
                    "currency": "SEK",
                    "reference": "REF-1",
                }
            ],
            "payments": [],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "run_rejected"
    assert body["reason_code"] == "no_accepted_payments"
    assert body["run_id"] is None
def test_post_ingest_rejects_when_invoices_missing(tmp_path: Path):
    app = create_app()

    def _reconcile_and_save(invoice_path: Path, payment_path: Path, **kwargs):
        raise AssertionError("reconcile_and_save should not be called")

    app.state.ingestion_run_runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=_reconcile_and_save,
        batch_root=tmp_path,
    )

    client = TestClient(app)

    response = client.post(
        "/api/reconciliation/runs/ingest",
        headers=TEST_AUTH_HEADER,
        json={
            "ingestion_batch_id": "batch-no-invoices",
            "invoices": [],
            "payments": [
                {
                    "id": "pay-1",
                    "date": "2026-04-08",
                    "amount": "100.00",
                    "currency": "SEK",
                    "reference": "REF-1",
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "run_rejected"
    assert body["reason_code"] == "no_accepted_invoices"
    assert body["run_id"] is None


def test_post_ingest_rejects_when_payments_missing(tmp_path: Path):
    app = create_app()

    def _reconcile_and_save(invoice_path: Path, payment_path: Path, **kwargs):
        raise AssertionError("reconcile_and_save should not be called")

    app.state.ingestion_run_runtime_adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=_reconcile_and_save,
        batch_root=tmp_path,
    )

    client = TestClient(app)

    response = client.post(
        "/api/reconciliation/runs/ingest",
        headers=TEST_AUTH_HEADER,
        json={
            "ingestion_batch_id": "batch-no-payments",
            "invoices": [
                {
                    "id": "inv-1",
                    "date": "2026-04-08",
                    "amount": "100.00",
                    "currency": "SEK",
                    "reference": "REF-1",
                }
            ],
            "payments": [],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "run_rejected"
    assert body["reason_code"] == "no_accepted_payments"
    assert body["run_id"] is None
