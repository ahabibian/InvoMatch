from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from invomatch.domain.export import (
    FinalDecisionType,
    FinalizedInvoiceRef,
    FinalizedMatchMeta,
    FinalizedPaymentRef,
    FinalizedResult,
    FinalizedReviewMeta,
    FinalizedReviewStatus,
)
from invomatch.domain.models import Invoice, MatchResult, Payment, ReconciliationRun
from invomatch.domain.review.models import DecisionType, ReviewItemStatus
from invomatch.services.export.errors import (
    ExportDataIncompleteError,
    FinalizedResultIntegrityError,
    RunNotExportableError,
)
from invomatch.services.export.source_loader import ExportSourceSnapshot


@dataclass(frozen=True, slots=True)
class _ResolvedReview:
    invoice_id: str
    item_status: ReviewItemStatus
    decision: DecisionType | None
    reviewed_by: str | None
    reviewed_at: Any
    reviewed_payload: dict[str, Any] | None


class FinalizedResultProjection:
    TERMINAL_REVIEW_STATUSES = {
        ReviewItemStatus.APPROVED,
        ReviewItemStatus.MODIFIED,
        ReviewItemStatus.REJECTED,
    }

    NON_EXPORTABLE_REVIEW_STATUSES = {
        ReviewItemStatus.PENDING,
        ReviewItemStatus.IN_REVIEW,
        ReviewItemStatus.DEFERRED,
    }

    def build_results_for_run(
        self,
        *,
        run: ReconciliationRun,
        source_snapshot: ExportSourceSnapshot,
        review_store: Any,
    ) -> list[FinalizedResult]:
        if run.report is None:
            raise ExportDataIncompleteError("run has no reconciliation report")

        if review_store is None:
            raise ExportDataIncompleteError("review store is required for finalized projection")

        review_index = self._build_review_index(
            run_id=str(run.run_id),
            review_store=review_store,
        )

        results: list[FinalizedResult] = []

        for report_result in run.report.results:
            invoice_id = str(report_result.invoice_id)
            invoice = source_snapshot.invoices_by_id.get(invoice_id)
            if invoice is None:
                raise ExportDataIncompleteError(
                    f"invoice not found in source data: {invoice_id}"
                )

            resolved_review = review_index.get(invoice_id)

            if resolved_review is None:
                finalized_result = self._build_result_without_review(
                    invoice=invoice,
                    match_result=report_result.match_result,
                    source_snapshot=source_snapshot,
                    run_id=str(run.run_id),
                )
            else:
                finalized_result = self._build_result(
                    invoice=invoice,
                    match_result=report_result.match_result,
                    resolved_review=resolved_review,
                    source_snapshot=source_snapshot,
                    run_id=str(run.run_id),
                )
            results.append(finalized_result)

        return results

    def _build_review_index(
        self,
        *,
        run_id: str,
        review_store: Any,
    ) -> dict[str, _ResolvedReview]:
        list_review_items = getattr(review_store, "list_review_items", None)
        get_feedback = getattr(review_store, "get_feedback", None)

        if list_review_items is None or get_feedback is None:
            raise ExportDataIncompleteError(
                "review store does not provide required query methods"
            )

        index: dict[str, _ResolvedReview] = {}

        for review_item in list_review_items():
            feedback = get_feedback(review_item.feedback_id)
            if feedback is None:
                continue

            if str(getattr(feedback, "run_id", "")) != run_id:
                continue

            invoice_id = str(getattr(feedback, "source_reference", "")).strip()
            if not invoice_id:
                raise ExportDataIncompleteError(
                    "review feedback source_reference is required for export projection"
                )

            item_status = review_item.item_status
            if item_status in self.NON_EXPORTABLE_REVIEW_STATUSES:
                raise RunNotExportableError(
                    f"review item for invoice {invoice_id} is not finalized: {item_status.value}"
                )

            if item_status not in self.TERMINAL_REVIEW_STATUSES:
                continue

            if invoice_id in index:
                raise FinalizedResultIntegrityError(
                    f"multiple finalized review items found for invoice: {invoice_id}"
                )

            index[invoice_id] = _ResolvedReview(
                invoice_id=invoice_id,
                item_status=item_status,
                decision=review_item.current_decision,
                reviewed_by=review_item.reviewed_by,
                reviewed_at=review_item.reviewed_at,
                reviewed_payload=review_item.reviewed_payload,
            )

        return index

    def _build_result_without_review(
        self,
        *,
        invoice: Invoice,
        match_result: MatchResult,
        source_snapshot: ExportSourceSnapshot,
        run_id: str,
    ) -> FinalizedResult:
        invoice_ref = FinalizedInvoiceRef(
            invoice_id=invoice.id,
            invoice_number=invoice.reference or invoice.id,
            invoice_date=invoice.date,
            amount=invoice.amount,
            currency=invoice.currency,
            vendor_name=None,
        )

        review_meta = self._build_no_review_meta()

        if match_result.status == "matched":
            return self._build_approved_result(
                invoice_ref=invoice_ref,
                match_result=match_result,
                review_meta=review_meta,
                source_snapshot=source_snapshot,
                run_id=run_id,
            )

        if match_result.status == "unmatched":
            return self._build_rejected_result(
                invoice_ref=invoice_ref,
                review_meta=review_meta,
                run_id=run_id,
            )

        if match_result.status in {"partial_match", "duplicate_detected"}:
            raise RunNotExportableError(
                f"match status requires finalized review before export: {match_result.status}"
            )

        raise RunNotExportableError(
            f"unsupported no-review export path for match status: {match_result.status}"
        )

    def _build_no_review_meta(self) -> FinalizedReviewMeta:
        return FinalizedReviewMeta(
            status=FinalizedReviewStatus.NOT_REQUIRED,
            reviewed_by=None,
            reviewed_at=None,
        )
    def _build_result(
        self,
        *,
        invoice: Invoice,
        match_result: MatchResult,
        resolved_review: _ResolvedReview,
        source_snapshot: ExportSourceSnapshot,
        run_id: str,
    ) -> FinalizedResult:
        invoice_ref = FinalizedInvoiceRef(
            invoice_id=invoice.id,
            invoice_number=invoice.reference or invoice.id,
            invoice_date=invoice.date,
            amount=invoice.amount,
            currency=invoice.currency,
            vendor_name=None,
        )

        review_meta = self._build_review_meta(resolved_review)

        if resolved_review.item_status is ReviewItemStatus.APPROVED:
            return self._build_approved_result(
                invoice_ref=invoice_ref,
                match_result=match_result,
                review_meta=review_meta,
                source_snapshot=source_snapshot,
                run_id=run_id,
            )

        if resolved_review.item_status is ReviewItemStatus.REJECTED:
            return self._build_rejected_result(
                invoice_ref=invoice_ref,
                review_meta=review_meta,
                run_id=run_id,
            )

        if resolved_review.item_status is ReviewItemStatus.MODIFIED:
            return self._build_modified_result(
                invoice_ref=invoice_ref,
                match_result=match_result,
                review_meta=review_meta,
                reviewed_payload=resolved_review.reviewed_payload,
                source_snapshot=source_snapshot,
                run_id=run_id,
            )

        raise FinalizedResultIntegrityError(
            f"unsupported finalized review status: {resolved_review.item_status.value}"
        )

    def _build_review_meta(self, resolved_review: _ResolvedReview) -> FinalizedReviewMeta:
        if resolved_review.item_status is ReviewItemStatus.APPROVED:
            status = FinalizedReviewStatus.APPROVED
        elif resolved_review.item_status is ReviewItemStatus.MODIFIED:
            status = FinalizedReviewStatus.MODIFIED
        elif resolved_review.item_status is ReviewItemStatus.REJECTED:
            status = FinalizedReviewStatus.REJECTED
        else:
            raise FinalizedResultIntegrityError(
                f"cannot map review status: {resolved_review.item_status.value}"
            )

        return FinalizedReviewMeta(
            status=status,
            reviewed_by=resolved_review.reviewed_by,
            reviewed_at=resolved_review.reviewed_at,
        )

    def _build_approved_result(
        self,
        *,
        invoice_ref: FinalizedInvoiceRef,
        match_result: MatchResult,
        review_meta: FinalizedReviewMeta,
        source_snapshot: ExportSourceSnapshot,
        run_id: str,
    ) -> FinalizedResult:
        payment_ids = self._extract_payment_ids(match_result)
        payments = self._resolve_payments(
            payment_ids=payment_ids,
            source_snapshot=source_snapshot,
            expected_currency=invoice_ref.currency,
        )

        matched_amount = self._derive_matched_amount_for_match_result(
            invoice_amount=invoice_ref.amount,
            match_result=match_result,
            payments=payments,
        )

        decision_type = self._map_match_status_to_final_decision(match_result.status)
        difference_amount = invoice_ref.amount - matched_amount

        return FinalizedResult(
            result_id=invoice_ref.invoice_id,
            run_id=run_id,
            decision_type=decision_type,
            invoice=invoice_ref,
            payments=tuple(payments),
            match=FinalizedMatchMeta(
                confidence=self._to_decimal_confidence(match_result.confidence_score),
                method="rule_based",
                matched_amount=matched_amount,
                difference_amount=difference_amount,
            ),
            review=review_meta,
        )

    def _build_rejected_result(
        self,
        *,
        invoice_ref: FinalizedInvoiceRef,
        review_meta: FinalizedReviewMeta,
        run_id: str,
    ) -> FinalizedResult:
        return FinalizedResult(
            result_id=invoice_ref.invoice_id,
            run_id=run_id,
            decision_type=FinalDecisionType.UNMATCHED,
            invoice=invoice_ref,
            payments=tuple(),
            match=FinalizedMatchMeta(
                confidence=None,
                method="review_rejected",
                matched_amount=Decimal("0"),
                difference_amount=invoice_ref.amount,
            ),
            review=review_meta,
        )

    def _build_modified_result(
        self,
        *,
        invoice_ref: FinalizedInvoiceRef,
        match_result: MatchResult,
        review_meta: FinalizedReviewMeta,
        reviewed_payload: dict[str, Any] | None,
        source_snapshot: ExportSourceSnapshot,
        run_id: str,
    ) -> FinalizedResult:
        payload = reviewed_payload or {}

        payment_ids = payload.get("payment_ids")
        if payment_ids is None:
            payment_ids = self._extract_payment_ids(match_result)

        if not isinstance(payment_ids, list):
            raise ExportDataIncompleteError("reviewed_payload.payment_ids must be a list when provided")

        payments = self._resolve_payments(
            payment_ids=[str(payment_id) for payment_id in payment_ids],
            source_snapshot=source_snapshot,
            expected_currency=invoice_ref.currency,
        )

        if "matched_amount" in payload:
            matched_amount = self._to_decimal_amount(payload["matched_amount"])
        else:
            matched_amount = sum((payment.amount for payment in payments), Decimal("0"))

        decision_type = self._derive_decision_from_amount(
            matched_amount=matched_amount,
            invoice_amount=invoice_ref.amount,
        )
        difference_amount = invoice_ref.amount - matched_amount

        return FinalizedResult(
            result_id=invoice_ref.invoice_id,
            run_id=run_id,
            decision_type=decision_type,
            invoice=invoice_ref,
            payments=tuple(payments),
            match=FinalizedMatchMeta(
                confidence=self._to_decimal_confidence(match_result.confidence_score),
                method="review_modified",
                matched_amount=matched_amount,
                difference_amount=difference_amount,
            ),
            review=review_meta,
        )

    def _extract_payment_ids(self, match_result: MatchResult) -> list[str]:
        if match_result.payment_ids:
            return [str(payment_id) for payment_id in match_result.payment_ids]

        if match_result.payment_id:
            return [str(match_result.payment_id)]

        if match_result.status in {"matched", "partial_match"}:
            raise ExportDataIncompleteError(
                f"payment ids are required for match status: {match_result.status}"
            )

        if match_result.status == "duplicate_detected":
            raise FinalizedResultIntegrityError(
                "duplicate_detected is not supported by finalized export contract"
            )

        return []

    def _resolve_payments(
        self,
        *,
        payment_ids: list[str],
        source_snapshot: ExportSourceSnapshot,
        expected_currency: str,
    ) -> list[FinalizedPaymentRef]:
        payments: list[FinalizedPaymentRef] = []

        for payment_id in payment_ids:
            payment = source_snapshot.payments_by_id.get(payment_id)
            if payment is None:
                raise ExportDataIncompleteError(
                    f"payment not found in source data: {payment_id}"
                )

            if payment.currency != expected_currency:
                raise FinalizedResultIntegrityError(
                    f"payment currency mismatch for payment {payment_id}"
                )

            payments.append(
                FinalizedPaymentRef(
                    payment_id=payment.id,
                    payment_date=payment.date,
                    amount=payment.amount,
                    currency=payment.currency,
                )
            )

        return payments

    def _derive_matched_amount_for_match_result(
        self,
        *,
        invoice_amount: Decimal,
        match_result: MatchResult,
        payments: list[FinalizedPaymentRef],
    ) -> Decimal:
        if match_result.status == "matched":
            return invoice_amount

        if match_result.status == "partial_match":
            return sum((payment.amount for payment in payments), Decimal("0"))

        if match_result.status == "unmatched":
            return Decimal("0")

        if match_result.status == "duplicate_detected":
            raise FinalizedResultIntegrityError(
                "duplicate_detected is not supported by finalized export contract"
            )

        raise FinalizedResultIntegrityError(
            f"unsupported match result status: {match_result.status}"
        )

    def _map_match_status_to_final_decision(self, status: str) -> FinalDecisionType:
        if status == "matched":
            return FinalDecisionType.MATCH
        if status == "partial_match":
            return FinalDecisionType.PARTIAL
        if status == "unmatched":
            return FinalDecisionType.UNMATCHED

        raise FinalizedResultIntegrityError(
            f"unsupported match result status: {status}"
        )

    def _derive_decision_from_amount(
        self,
        *,
        matched_amount: Decimal,
        invoice_amount: Decimal,
    ) -> FinalDecisionType:
        if matched_amount == Decimal("0"):
            return FinalDecisionType.UNMATCHED
        if matched_amount == invoice_amount:
            return FinalDecisionType.MATCH
        if Decimal("0") < matched_amount < invoice_amount:
            return FinalDecisionType.PARTIAL

        raise FinalizedResultIntegrityError(
            "matched_amount is inconsistent with invoice amount"
        )

    def _to_decimal_confidence(self, confidence_score: float) -> Decimal:
        return Decimal(str(confidence_score))

    def _to_decimal_amount(self, raw_value: Any) -> Decimal:
        return Decimal(str(raw_value))
