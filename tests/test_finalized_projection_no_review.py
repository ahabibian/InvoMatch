from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from invomatch.domain.export import FinalDecisionType, FinalizedReviewStatus
from invomatch.domain.models import (
    Invoice,
    MatchResult,
    Payment,
    ReconciliationReport,
    ReconciliationResult,
    ReconciliationRun,
)
from invomatch.services.export.errors import RunNotExportableError
from invomatch.services.export.finalized_projection import FinalizedResultProjection
from invomatch.services.export.source_loader import ExportSourceSnapshot
from invomatch.services.review_store import InMemoryReviewStore


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _invoice(invoice_id: str = "inv-1") -> Invoice:
    return Invoice(
        id=invoice_id,
        date=date(2024, 1, 10),
        amount=Decimal("100.00"),
        currency="USD",
        reference="INV-1",
    )


def _payment(payment_id: str = "pay-1") -> Payment:
    return Payment(
        id=payment_id,
        date=date(2024, 1, 12),
        amount=Decimal("100.00"),
        currency="USD",
        reference="Payment for INV-1",
    )


def _run_with_match_result(
    match_result: MatchResult,
    *,
    matched: int,
    unmatched: int,
    duplicate_detected: int,
    partial_match: int,
) -> ReconciliationRun:
    now = _now()
    report = ReconciliationReport(
        total_invoices=1,
        matched=matched,
        unmatched=unmatched,
        duplicate_detected=duplicate_detected,
        partial_match=partial_match,
        results=[
            ReconciliationResult(
                invoice_id="inv-1",
                match_result=match_result,
            )
        ],
    )

    return ReconciliationRun(
        run_id="run-no-review-001",
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
        invoice_csv_path="unused/invoices.csv",
        payment_csv_path="unused/payments.csv",
        error_message=None,
        report=report,
    )


def _snapshot_for_single_pair() -> ExportSourceSnapshot:
    invoice = _invoice()
    payment = _payment()
    return ExportSourceSnapshot(
        invoices_by_id={invoice.id: invoice},
        payments_by_id={payment.id: payment},
    )


def test_no_review_matched_result_is_exportable() -> None:
    projection = FinalizedResultProjection()
    review_store = InMemoryReviewStore()

    match_result = MatchResult(
        status="matched",
        payment_id="pay-1",
        payment_ids=["pay-1"],
        duplicate_payment_ids=None,
        confidence_score=0.99,
        confidence_explanation="exact match",
        mismatch_reasons=["amount_match", "reference_match"],
    )

    run = _run_with_match_result(
        match_result,
        matched=1,
        unmatched=0,
        duplicate_detected=0,
        partial_match=0,
    )
    snapshot = _snapshot_for_single_pair()

    results = projection.build_results_for_run(
        run=run,
        source_snapshot=snapshot,
        review_store=review_store,
    )

    assert len(results) == 1
    assert results[0].decision_type is FinalDecisionType.MATCH
    assert results[0].review.status is FinalizedReviewStatus.NOT_REQUIRED
    assert len(results[0].payments) == 1
    assert results[0].payments[0].payment_id == "pay-1"


def test_no_review_unmatched_result_is_exportable() -> None:
    projection = FinalizedResultProjection()
    review_store = InMemoryReviewStore()

    match_result = MatchResult(
        status="unmatched",
        payment_id=None,
        payment_ids=None,
        duplicate_payment_ids=None,
        confidence_score=0.0,
        confidence_explanation="no viable candidate",
        mismatch_reasons=["no_viable_candidate"],
    )

    run = _run_with_match_result(
        match_result,
        matched=0,
        unmatched=1,
        duplicate_detected=0,
        partial_match=0,
    )
    snapshot = _snapshot_for_single_pair()

    results = projection.build_results_for_run(
        run=run,
        source_snapshot=snapshot,
        review_store=review_store,
    )

    assert len(results) == 1
    assert results[0].decision_type is FinalDecisionType.UNMATCHED
    assert results[0].review.status is FinalizedReviewStatus.NOT_REQUIRED
    assert len(results[0].payments) == 0
    assert results[0].match.matched_amount == Decimal("0")


def test_no_review_partial_match_remains_non_exportable() -> None:
    projection = FinalizedResultProjection()
    review_store = InMemoryReviewStore()

    match_result = MatchResult(
        status="partial_match",
        payment_id=None,
        payment_ids=["pay-1"],
        duplicate_payment_ids=None,
        confidence_score=0.75,
        confidence_explanation="combined partial payments equal invoice amount",
        mismatch_reasons=["partial_sum_match"],
    )

    run = _run_with_match_result(
        match_result,
        matched=0,
        unmatched=0,
        duplicate_detected=0,
        partial_match=1,
    )
    snapshot = _snapshot_for_single_pair()

    try:
        projection.build_results_for_run(
            run=run,
            source_snapshot=snapshot,
            review_store=review_store,
        )
        raise AssertionError("expected RunNotExportableError for no-review partial_match")
    except RunNotExportableError as exc:
        assert "requires finalized review before export" in str(exc)


def test_no_review_duplicate_detected_remains_non_exportable() -> None:
    projection = FinalizedResultProjection()
    review_store = InMemoryReviewStore()

    match_result = MatchResult(
        status="duplicate_detected",
        payment_id="pay-1",
        payment_ids=None,
        duplicate_payment_ids=["pay-2"],
        confidence_score=0.6,
        confidence_explanation="duplicate candidates detected",
        mismatch_reasons=["amount_match", "reference_match", "duplicate_candidates"],
    )

    run = _run_with_match_result(
        match_result,
        matched=0,
        unmatched=0,
        duplicate_detected=1,
        partial_match=0,
    )
    snapshot = _snapshot_for_single_pair()

    try:
        projection.build_results_for_run(
            run=run,
            source_snapshot=snapshot,
            review_store=review_store,
        )
        raise AssertionError("expected RunNotExportableError for no-review duplicate_detected")
    except RunNotExportableError as exc:
        assert "requires finalized review before export" in str(exc)