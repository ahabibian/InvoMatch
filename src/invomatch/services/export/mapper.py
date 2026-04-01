from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from invomatch.domain.export import (
    ExportBundle,
    ExportSummary,
    FinalDecisionType,
    FinalizedPaymentRef,
    FinalizedResult,
)
from invomatch.services.export.errors import FinalizedResultIntegrityError


class ExportMapper:
    SCHEMA_VERSION = "1.0"

    def build_bundle(
        self,
        *,
        run_id: str,
        status: str,
        currency: str,
        exported_at: datetime,
        results: list[FinalizedResult],
    ) -> ExportBundle:
        if not run_id:
            raise ValueError("run_id is required")
        if not status:
            raise ValueError("status is required")
        if not currency:
            raise ValueError("currency is required")
        if exported_at is None:
            raise ValueError("exported_at is required")

        normalized_results = [self._normalize_result(result, currency) for result in results]
        ordered_results = tuple(self._sort_results(normalized_results))
        summary = self._build_summary(ordered_results)

        return ExportBundle(
            schema_version=self.SCHEMA_VERSION,
            run_id=run_id,
            status=status,
            exported_at=exported_at,
            currency=currency,
            summary=summary,
            results=ordered_results,
        )

    def _normalize_result(self, result: FinalizedResult, currency: str) -> FinalizedResult:
        if result.invoice.currency != currency:
            raise FinalizedResultIntegrityError(
                "result invoice currency does not match export bundle currency"
            )

        normalized_payments = tuple(self._sort_payments(result.payments))
        return replace(result, payments=normalized_payments)

    def _sort_results(self, results: list[FinalizedResult]) -> list[FinalizedResult]:
        return sorted(
            results,
            key=lambda item: (
                item.invoice.invoice_date is None,
                item.invoice.invoice_date,
                item.invoice.invoice_id,
            ),
        )

    def _sort_payments(
        self,
        payments: tuple[FinalizedPaymentRef, ...],
    ) -> list[FinalizedPaymentRef]:
        return sorted(
            payments,
            key=lambda item: (
                item.payment_date is None,
                item.payment_date,
                item.payment_id,
            ),
        )

    def _build_summary(self, results: tuple[FinalizedResult, ...]) -> ExportSummary:
        total_invoices = len(results)
        total_payments = sum(len(result.payments) for result in results)
        matched = sum(1 for result in results if result.decision_type is FinalDecisionType.MATCH)
        partial = sum(1 for result in results if result.decision_type is FinalDecisionType.PARTIAL)
        unmatched = sum(
            1 for result in results if result.decision_type is FinalDecisionType.UNMATCHED
        )

        return ExportSummary(
            total_invoices=total_invoices,
            total_payments=total_payments,
            matched=matched,
            unmatched=unmatched,
            partial=partial,
        )
