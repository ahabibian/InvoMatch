from invomatch.ingestion.models.duplicate_models import DuplicateClassification
from invomatch.ingestion.models.raw_models import RawInvoiceInput, RawPaymentInput
from invomatch.ingestion.repositories import InMemoryIngestionRepository
from invomatch.ingestion.services import InvoiceIngestionGateway, PaymentIngestionGateway


def test_invoice_gateway_marks_first_ingestion_as_unique():
    repository = InMemoryIngestionRepository()
    gateway = InvoiceIngestionGateway(repository)

    outcome = gateway.ingest(
        RawInvoiceInput(
            invoice_number="INV-001",
            issue_date="2026-04-07",
            currency="SEK",
            gross_amount="100.00",
        )
    )

    assert outcome.duplicate_check.classification == DuplicateClassification.UNIQUE
    assert outcome.record.result.idempotency_key
    assert outcome.record.result.semantic_key


def test_invoice_gateway_marks_exact_replay():
    repository = InMemoryIngestionRepository()
    gateway = InvoiceIngestionGateway(repository)

    raw = RawInvoiceInput(
        invoice_number="INV-001",
        issue_date="2026-04-07",
        currency="SEK",
        gross_amount="100.00",
    )

    first = gateway.ingest(raw)
    second = gateway.ingest(raw)

    assert first.duplicate_check.classification == DuplicateClassification.UNIQUE
    assert second.duplicate_check.classification == DuplicateClassification.EXACT_REPLAY


def test_invoice_gateway_marks_semantic_duplicate():
    repository = InMemoryIngestionRepository()
    gateway = InvoiceIngestionGateway(repository)

    first = gateway.ingest(
        RawInvoiceInput(
            invoice_number="INV 001",
            issue_date="2026-04-07",
            currency="SEK",
            gross_amount="100.00",
            counterparty="Vendor A",
        )
    )
    second = gateway.ingest(
        RawInvoiceInput(
            invoice_number="INV001",
            issue_date="2026-04-07",
            currency="sek",
            gross_amount="100.0",
            counterparty="Vendor B",
        )
    )

    assert first.duplicate_check.classification == DuplicateClassification.UNIQUE
    assert second.duplicate_check.classification == DuplicateClassification.SEMANTIC_DUPLICATE


def test_invoice_gateway_marks_conflict():
    repository = InMemoryIngestionRepository()
    gateway = InvoiceIngestionGateway(repository)

    first = gateway.ingest(
        RawInvoiceInput(
            invoice_number="INV-001",
            issue_date="2026-04-07",
            currency="SEK",
            gross_amount="100.00",
        )
    )
    second = gateway.ingest(
        RawInvoiceInput(
            invoice_number="INV-001",
            issue_date="2026-04-07",
            currency="SEK",
            gross_amount="120.00",
        )
    )

    assert first.duplicate_check.classification == DuplicateClassification.UNIQUE
    assert second.duplicate_check.classification == DuplicateClassification.CONFLICT


def test_payment_gateway_marks_exact_replay():
    repository = InMemoryIngestionRepository()
    gateway = PaymentIngestionGateway(repository)

    raw = RawPaymentInput(
        payment_reference="RF12345",
        payment_date="2026-04-07",
        amount="99.50",
        currency="EUR",
    )

    first = gateway.ingest(raw)
    second = gateway.ingest(raw)

    assert first.duplicate_check.classification == DuplicateClassification.UNIQUE
    assert second.duplicate_check.classification == DuplicateClassification.EXACT_REPLAY


def test_payment_gateway_marks_semantic_duplicate():
    repository = InMemoryIngestionRepository()
    gateway = PaymentIngestionGateway(repository)

    first = gateway.ingest(
        RawPaymentInput(
            payment_reference="RF 12345",
            payment_date="2026-04-07",
            amount="99.50",
            currency="EUR",
            counterparty="A",
        )
    )
    second = gateway.ingest(
        RawPaymentInput(
            payment_reference="RF12345",
            payment_date="2026-04-07",
            amount="99.5",
            currency="eur",
            counterparty="B",
        )
    )

    assert first.duplicate_check.classification == DuplicateClassification.UNIQUE
    assert second.duplicate_check.classification == DuplicateClassification.SEMANTIC_DUPLICATE


def test_payment_gateway_marks_conflict():
    repository = InMemoryIngestionRepository()
    gateway = PaymentIngestionGateway(repository)

    first = gateway.ingest(
        RawPaymentInput(
            payment_reference="RF12345",
            payment_date="2026-04-07",
            amount="99.50",
            currency="EUR",
        )
    )
    second = gateway.ingest(
        RawPaymentInput(
            payment_reference="RF12345",
            payment_date="2026-04-07",
            amount="109.50",
            currency="EUR",
        )
    )

    assert first.duplicate_check.classification == DuplicateClassification.UNIQUE
    assert second.duplicate_check.classification == DuplicateClassification.CONFLICT