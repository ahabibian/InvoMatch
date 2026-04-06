from __future__ import annotations

from invomatch.ingestion.models.normalized_models import NormalizedInvoice, NormalizedPayment
from invomatch.ingestion.utils.fingerprint import fingerprint_payload


def build_invoice_semantic_key(invoice: NormalizedInvoice) -> str:
    identity = {
        "invoice_number": invoice.invoice_number,
        "issue_date": invoice.issue_date.isoformat(),
        "currency": invoice.currency,
        "gross_amount": str(invoice.gross_amount),
    }
    return f"invoice:{fingerprint_payload(identity)}"


def build_payment_semantic_key(payment: NormalizedPayment) -> str:
    identity = {
        "payment_reference": payment.payment_reference,
        "payment_date": payment.payment_date.isoformat(),
        "currency": payment.currency,
        "amount": str(payment.amount),
    }
    return f"payment:{fingerprint_payload(identity)}"