from __future__ import annotations

from invomatch.ingestion.models.normalized_models import NormalizedInvoice, NormalizedPayment
from invomatch.ingestion.utils.fingerprint import fingerprint_payload


def build_invoice_identity_key(invoice: NormalizedInvoice) -> str:
    identity = {
        "invoice_number": invoice.invoice_number,
        "issue_date": invoice.issue_date.isoformat(),
        "currency": invoice.currency,
    }
    return f"invoice_identity:{fingerprint_payload(identity)}"


def build_payment_identity_key(payment: NormalizedPayment) -> str:
    identity = {
        "payment_reference": payment.payment_reference,
        "payment_date": payment.payment_date.isoformat(),
        "currency": payment.currency,
    }
    return f"payment_identity:{fingerprint_payload(identity)}"