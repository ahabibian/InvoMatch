from invomatch.services.ingestion_run_integration.run_creation_policy import (
    RunCreationPolicy,
)


def test_rejects_when_ingestion_failed():
    policy = RunCreationPolicy()

    result = policy.evaluate(
        ingestion_succeeded=False,
        accepted_invoice_count=1,
        accepted_payment_count=1,
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
    )

    assert result.creatable is False
    assert result.reason_code == "ingestion_failed"


def test_rejects_when_no_invoices():
    policy = RunCreationPolicy()

    result = policy.evaluate(
        ingestion_succeeded=True,
        accepted_invoice_count=0,
        accepted_payment_count=1,
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
    )

    assert result.creatable is False
    assert result.reason_code == "no_accepted_invoices"


def test_rejects_when_no_payments():
    policy = RunCreationPolicy()

    result = policy.evaluate(
        ingestion_succeeded=True,
        accepted_invoice_count=1,
        accepted_payment_count=0,
        rejected_count=0,
        conflict_count=0,
        blocking_conflict=False,
    )

    assert result.creatable is False
    assert result.reason_code == "no_accepted_payments"


def test_rejects_when_blocking_conflict_exists():
    policy = RunCreationPolicy()

    result = policy.evaluate(
        ingestion_succeeded=True,
        accepted_invoice_count=1,
        accepted_payment_count=1,
        rejected_count=0,
        conflict_count=1,
        blocking_conflict=True,
    )

    assert result.creatable is False
    assert result.reason_code == "blocking_conflict"


def test_allows_partial_ingestion_when_minimum_dataset_exists():
    policy = RunCreationPolicy()

    result = policy.evaluate(
        ingestion_succeeded=True,
        accepted_invoice_count=2,
        accepted_payment_count=1,
        rejected_count=3,
        conflict_count=0,
        blocking_conflict=False,
    )

    assert result.creatable is True
    assert result.reason_code == "creatable"
    assert result.partial_ingestion is True