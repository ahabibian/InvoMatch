from __future__ import annotations


class IngestionToRunMapper:
    def map(
        self,
        *,
        accepted_invoices: list[object],
        accepted_payments: list[object],
    ) -> dict:
        return {
            "invoices": list(accepted_invoices),
            "payments": list(accepted_payments),
        }