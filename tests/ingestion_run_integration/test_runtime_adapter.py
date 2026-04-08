from pathlib import Path

from invomatch.domain.models import ReconciliationRun
from invomatch.services.ingestion_run_integration.models import IngestionRunStatus
from invomatch.services.ingestion_run_integration.runtime_adapter import (
    IngestionRunRuntimeAdapter,
)


def _fake_run(run_id: str) -> ReconciliationRun:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        run_id=run_id,
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
        invoice_csv_path="output/ingestion_batches/batch-1/invoices.csv",
        payment_csv_path="output/ingestion_batches/batch-1/payments.csv",
        error_message=None,
        report=None,
    )


def test_runtime_adapter_creates_batch_files_and_run(tmp_path: Path):
    created = {"count": 0}

    def _reconcile_and_save(invoice_path: Path, payment_path: Path):
        created["count"] += 1
        assert invoice_path.exists()
        assert payment_path.exists()
        return _fake_run("run-123")

    adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=_reconcile_and_save,
        batch_root=tmp_path,
    )

    result = adapter.create_run_from_ingestion(
        ingestion_batch_id="batch-1",
        ingestion_succeeded=True,
        accepted_invoices=[{"invoice_number": "INV-1", "amount": "100"}],
        accepted_payments=[{"payment_reference": "PAY-1", "amount": "100"}],
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
    )

    assert result.status == IngestionRunStatus.RUN_CREATED
    assert result.run_id == "run-123"
    assert created["count"] == 1
    assert (tmp_path / "batch-1" / "traceability.json").exists()
    assert (tmp_path / "batch-1" / "run_result.json").exists()


def test_runtime_adapter_reuses_existing_run_for_same_batch_and_fingerprint(tmp_path: Path):
    created = {"count": 0}

    def _reconcile_and_save(invoice_path: Path, payment_path: Path):
        created["count"] += 1
        return _fake_run("run-123")

    adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=_reconcile_and_save,
        batch_root=tmp_path,
    )

    first = adapter.create_run_from_ingestion(
        ingestion_batch_id="batch-1",
        ingestion_succeeded=True,
        accepted_invoices=[{"invoice_number": "INV-1", "amount": "100"}],
        accepted_payments=[{"payment_reference": "PAY-1", "amount": "100"}],
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
    )

    second = adapter.create_run_from_ingestion(
        ingestion_batch_id="batch-1",
        ingestion_succeeded=True,
        accepted_invoices=[{"invoice_number": "INV-1", "amount": "100"}],
        accepted_payments=[{"payment_reference": "PAY-1", "amount": "100"}],
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
    )

    assert first.status == IngestionRunStatus.RUN_CREATED
    assert second.status == IngestionRunStatus.RUN_REUSED
    assert second.run_id == "run-123"
    assert created["count"] == 1


def test_runtime_adapter_fails_on_same_batch_with_different_fingerprint(tmp_path: Path):
    created = {"count": 0}

    def _reconcile_and_save(invoice_path: Path, payment_path: Path):
        created["count"] += 1
        return _fake_run("run-123")

    adapter = IngestionRunRuntimeAdapter(
        reconcile_and_save=_reconcile_and_save,
        batch_root=tmp_path,
    )

    adapter.create_run_from_ingestion(
        ingestion_batch_id="batch-1",
        ingestion_succeeded=True,
        accepted_invoices=[{"invoice_number": "INV-1", "amount": "100"}],
        accepted_payments=[{"payment_reference": "PAY-1", "amount": "100"}],
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
    )

    result = adapter.create_run_from_ingestion(
        ingestion_batch_id="batch-1",
        ingestion_succeeded=True,
        accepted_invoices=[{"invoice_number": "INV-2", "amount": "999"}],
        accepted_payments=[{"payment_reference": "PAY-1", "amount": "100"}],
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
    )

    assert result.status == IngestionRunStatus.RUN_FAILED
    assert result.reason_code == "batch_identity_conflict"
    assert created["count"] == 1