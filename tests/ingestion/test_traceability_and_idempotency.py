from invomatch.ingestion.models.raw_models import RawInvoiceInput, RawPaymentInput
from invomatch.ingestion.services import ingest_invoice_input, ingest_payment_input
from invomatch.ingestion.utils import build_idempotency_key, fingerprint_payload


def test_fingerprint_payload_is_deterministic_for_same_model_input():
    raw = RawInvoiceInput(
        external_id="ext-1",
        invoice_number="INV-001",
        issue_date="2026-04-07",
        currency="SEK",
        gross_amount="100.00",
    )

    assert fingerprint_payload(raw) == fingerprint_payload(raw)


def test_build_idempotency_key_is_stable():
    fingerprint = "abc123"
    assert build_idempotency_key("invoice", fingerprint) == "invoice:abc123"


def test_invoice_ingestion_populates_traceability_and_idempotency():
    raw = RawInvoiceInput(
        external_id="ext-1",
        invoice_number="INV-001",
        issue_date="2026-04-07",
        currency="SEK",
        gross_amount="100.00",
    )

    result = ingest_invoice_input(raw)

    assert result.raw_reference.payload_kind == "invoice"
    assert result.raw_reference.schema_version == "invoice_input/v1"
    assert result.raw_reference.rule_version == "ingestion_rules/v1"
    assert result.raw_reference.payload_fingerprint
    assert result.idempotency_key == f"invoice:{result.raw_reference.payload_fingerprint}"


def test_payment_ingestion_populates_traceability_and_idempotency():
    raw = RawPaymentInput(
        external_id="pay-1",
        payment_reference="RF12345",
        payment_date="2026-04-07",
        amount="99.50",
        currency="EUR",
    )

    result = ingest_payment_input(raw)

    assert result.raw_reference.payload_kind == "payment"
    assert result.raw_reference.schema_version == "payment_input/v1"
    assert result.raw_reference.rule_version == "ingestion_rules/v1"
    assert result.raw_reference.payload_fingerprint
    assert result.idempotency_key == f"payment:{result.raw_reference.payload_fingerprint}"


def test_same_invoice_input_produces_same_idempotency_key():
    raw1 = RawInvoiceInput(
        external_id="ext-1",
        invoice_number="INV-001",
        issue_date="2026-04-07",
        currency="SEK",
        gross_amount="100.00",
    )
    raw2 = RawInvoiceInput(
        external_id="ext-1",
        invoice_number="INV-001",
        issue_date="2026-04-07",
        currency="SEK",
        gross_amount="100.00",
    )

    result1 = ingest_invoice_input(raw1)
    result2 = ingest_invoice_input(raw2)

    assert result1.idempotency_key == result2.idempotency_key
    assert result1.raw_reference.payload_fingerprint == result2.raw_reference.payload_fingerprint