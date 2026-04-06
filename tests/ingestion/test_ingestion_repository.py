from invomatch.ingestion.models.raw_models import RawInvoiceInput, RawPaymentInput
from invomatch.ingestion.repositories import InMemoryIngestionRepository
from invomatch.ingestion.services import ingest_invoice_input, ingest_payment_input


def test_repository_saves_and_finds_by_idempotency_key():
    repository = InMemoryIngestionRepository()
    result = ingest_invoice_input(
        RawInvoiceInput(
            invoice_number="INV-001",
            issue_date="2026-04-07",
            currency="SEK",
            gross_amount="100.00",
        )
    )

    saved = repository.save_result(result)
    found = repository.find_by_idempotency_key(result.idempotency_key)

    assert found is not None
    assert found.record_id == saved.record_id
    assert found.result.idempotency_key == result.idempotency_key


def test_repository_saves_and_finds_latest_by_semantic_key():
    repository = InMemoryIngestionRepository()
    result = ingest_payment_input(
        RawPaymentInput(
            payment_reference="RF12345",
            payment_date="2026-04-07",
            amount="99.50",
            currency="EUR",
        )
    )

    saved = repository.save_result(result)
    found = repository.find_latest_by_semantic_key(result.semantic_key)

    assert found is not None
    assert found.record_id == saved.record_id
    assert found.result.semantic_key == result.semantic_key


def test_repository_returns_none_for_unknown_idempotency_key():
    repository = InMemoryIngestionRepository()
    assert repository.find_by_idempotency_key("missing") is None


def test_repository_returns_none_for_unknown_semantic_key():
    repository = InMemoryIngestionRepository()
    assert repository.find_latest_by_semantic_key("missing") is None