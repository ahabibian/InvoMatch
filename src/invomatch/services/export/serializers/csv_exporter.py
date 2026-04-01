from __future__ import annotations

import csv
import io
from decimal import Decimal

from invomatch.domain.export import ExportBundle


class CsvExporter:
    HEADERS = [
        "result_id",
        "decision_type",
        "invoice_id",
        "invoice_number",
        "invoice_date",
        "invoice_amount",
        "currency",
        "vendor_name",
        "payment_ids",
        "payment_dates",
        "payment_total",
        "matched_amount",
        "difference_amount",
        "confidence",
        "match_method",
        "review_status",
        "reviewed_by",
        "reviewed_at",
    ]

    def export(self, bundle: ExportBundle) -> bytes:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=self.HEADERS)
        writer.writeheader()

        for r in bundle.results:
            payment_ids = [p.payment_id for p in r.payments]
            payment_dates = [
                p.payment_date.isoformat() if p.payment_date else "" for p in r.payments
            ]
            payment_total = sum((p.amount for p in r.payments), Decimal("0"))

            row = {
                "result_id": r.result_id,
                "decision_type": r.decision_type.value,
                "invoice_id": r.invoice.invoice_id,
                "invoice_number": r.invoice.invoice_number,
                "invoice_date": r.invoice.invoice_date.isoformat() if r.invoice.invoice_date else "",
                "invoice_amount": str(r.invoice.amount),
                "currency": r.invoice.currency,
                "vendor_name": r.invoice.vendor_name or "",
                "payment_ids": "|".join(payment_ids),
                "payment_dates": "|".join(payment_dates),
                "payment_total": str(payment_total),
                "matched_amount": str(r.match.matched_amount),
                "difference_amount": str(r.match.difference_amount),
                "confidence": str(r.match.confidence) if r.match.confidence is not None else "",
                "match_method": r.match.method,
                "review_status": r.review.status.value,
                "reviewed_by": r.review.reviewed_by or "",
                "reviewed_at": r.review.reviewed_at.isoformat() if r.review.reviewed_at else "",
            }

            writer.writerow(row)

        return buf.getvalue().encode("utf-8")
