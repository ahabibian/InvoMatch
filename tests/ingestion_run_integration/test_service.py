from invomatch.services.ingestion_run_integration.models import IngestionRunStatus
from invomatch.services.ingestion_run_integration.service import (
    IngestionRunIntegrationService,
)


def test_service_creates_run_for_valid_ingestion():
    service = IngestionRunIntegrationService()

    created = {}

    def _create_run(*, run_input, traceability):
        created["run_input"] = run_input
        created["traceability"] = traceability
        return "run-123"

    result = service.create_run_from_ingestion(
        ingestion_batch_id="batch-1",
        ingestion_succeeded=True,
        accepted_invoices=[{"id": "inv-1"}],
        accepted_payments=[{"id": "pay-1"}],
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
        existing_run_id=None,
        same_batch_identity=False,
        same_normalized_fingerprint=False,
        create_run=_create_run,
    )

    assert result.status == IngestionRunStatus.RUN_CREATED
    assert result.run_id == "run-123"
    assert created["traceability"]["ingestion_batch_id"] == "batch-1"


def test_service_reuses_existing_run_on_idempotent_replay():
    service = IngestionRunIntegrationService()

    def _create_run(*, run_input, traceability):
        raise AssertionError("create_run should not be called")

    result = service.create_run_from_ingestion(
        ingestion_batch_id="batch-1",
        ingestion_succeeded=True,
        accepted_invoices=[{"id": "inv-1"}],
        accepted_payments=[{"id": "pay-1"}],
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
        existing_run_id="run-existing",
        same_batch_identity=True,
        same_normalized_fingerprint=True,
        create_run=_create_run,
    )

    assert result.status == IngestionRunStatus.RUN_REUSED
    assert result.run_id == "run-existing"


def test_service_rejects_when_policy_disallows_creation():
    service = IngestionRunIntegrationService()

    def _create_run(*, run_input, traceability):
        raise AssertionError("create_run should not be called")

    result = service.create_run_from_ingestion(
        ingestion_batch_id="batch-1",
        ingestion_succeeded=True,
        accepted_invoices=[],
        accepted_payments=[{"id": "pay-1"}],
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
        existing_run_id=None,
        same_batch_identity=False,
        same_normalized_fingerprint=False,
        create_run=_create_run,
    )

    assert result.status == IngestionRunStatus.RUN_REJECTED
    assert result.reason_code == "no_accepted_invoices"