from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from invomatch.domain.models import Invoice, Payment, ReconciliationRun
from invomatch.services.export.errors import FinalizedResultIntegrityError
from invomatch.services.ingestion import load_invoices_from_csv, load_payments_from_csv


@dataclass(frozen=True, slots=True)
class ExportSourceSnapshot:
    invoices_by_id: dict[str, Invoice]
    payments_by_id: dict[str, Payment]


class ExportSourceLoader:
    def load_sources_for_run(self, run: ReconciliationRun) -> ExportSourceSnapshot:
        invoices = load_invoices_from_csv(Path(run.invoice_csv_path))
        payments = load_payments_from_csv(Path(run.payment_csv_path))

        invoices_by_id = self._index_invoices(invoices)
        payments_by_id = self._index_payments(payments)

        return ExportSourceSnapshot(
            invoices_by_id=invoices_by_id,
            payments_by_id=payments_by_id,
        )

    def _index_invoices(self, invoices: list[Invoice]) -> dict[str, Invoice]:
        indexed: dict[str, Invoice] = {}

        for invoice in invoices:
            if invoice.id in indexed:
                raise FinalizedResultIntegrityError(
                    f"duplicate invoice id in source data: {invoice.id}"
                )
            indexed[invoice.id] = invoice

        return indexed

    def _index_payments(self, payments: list[Payment]) -> dict[str, Payment]:
        indexed: dict[str, Payment] = {}

        for payment in payments:
            if payment.id in indexed:
                raise FinalizedResultIntegrityError(
                    f"duplicate payment id in source data: {payment.id}"
                )
            indexed[payment.id] = payment

        return indexed
