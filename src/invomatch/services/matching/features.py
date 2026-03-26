from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Final

from invomatch.domain.matching.features import InvoiceRecord, MatchFeatures, PaymentRecord

_NOISE_TOKENS: Final[frozenset[str]] = frozenset(
    {
        "ab",
        "aktiebolag",
        "as",
        "bank",
        "company",
        "co",
        "corp",
        "gmbh",
        "inc",
        "invoice",
        "limited",
        "llc",
        "ltd",
        "of",
        "oy",
        "payment",
        "ref",
        "reference",
        "the",
    }
)

_WHITESPACE_RE: Final[re.Pattern[str]] = re.compile(r"\s+")
_NON_ALNUM_RE: Final[re.Pattern[str]] = re.compile(r"[^A-Z0-9]+")
_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"[A-Z0-9]+")


def _normalize_text(value: str) -> str:
    collapsed = _WHITESPACE_RE.sub(" ", value.strip().upper())
    return collapsed


def _normalize_identifier(value: str) -> str:
    normalized = _normalize_text(value)
    return _NON_ALNUM_RE.sub("", normalized)


def _tokenize(value: str) -> tuple[str, ...]:
    normalized = _normalize_text(value)
    tokens = [token for token in _TOKEN_RE.findall(normalized) if token not in _NOISE_TOKENS]
    return tuple(tokens)


def _token_overlap_score(left: Iterable[str], right: Iterable[str]) -> float:
    left_set = set(left)
    right_set = set(right)

    if not left_set or not right_set:
        return 0.0

    intersection = left_set & right_set
    denominator = max(len(left_set), len(right_set))
    return len(intersection) / denominator


def _contains_invoice_number(invoice_number_normalized: str, *texts: str) -> bool:
    if not invoice_number_normalized:
        return False

    for text in texts:
        if invoice_number_normalized and invoice_number_normalized in _normalize_identifier(text):
            return True
    return False


def _safe_percentage_delta(invoice_amount: float, payment_amount: float) -> float:
    if invoice_amount == 0:
        return 0.0 if payment_amount == 0 else 1.0
    return abs(invoice_amount - payment_amount) / invoice_amount


def build_match_features(invoice: InvoiceRecord, payment: PaymentRecord) -> MatchFeatures:
    invoice_number_normalized = _normalize_identifier(invoice.invoice_number)
    payment_reference_normalized = _normalize_identifier(payment.reference_text)
    bank_reference_normalized = _normalize_identifier(payment.bank_reference)

    supplier_name_normalized = _normalize_identifier(invoice.supplier_name)
    counterparty_name_normalized = _normalize_identifier(payment.counterparty_name)

    invoice_reference_tokens = _tokenize(
        " ".join(
            part
            for part in (
                invoice.invoice_number,
                invoice.reference_text,
                invoice.supplier_name,
            )
            if part
        )
    )

    payment_reference_tokens = _tokenize(
        " ".join(
            part
            for part in (
                payment.reference_text,
                payment.bank_reference,
                payment.counterparty_name,
            )
            if part
        )
    )

    amount_delta_absolute = abs(invoice.gross_amount - payment.amount)
    amount_delta_percentage = _safe_percentage_delta(invoice.gross_amount, payment.amount)

    reference_token_overlap_score = _token_overlap_score(
        invoice_reference_tokens,
        payment_reference_tokens,
    )

    invoice_number_in_payment_reference = _contains_invoice_number(
        invoice_number_normalized,
        payment.reference_text,
        payment.bank_reference,
    )

    invoice_number_exact_match = _normalize_text(invoice.invoice_number) in {
        _normalize_text(payment.reference_text),
        _normalize_text(payment.bank_reference),
    }

    invoice_number_normalized_match = invoice_number_in_payment_reference

    supplier_name_exact_match = _normalize_text(invoice.supplier_name) == _normalize_text(
        payment.counterparty_name
    )
    supplier_name_normalized_match = (
        bool(supplier_name_normalized)
        and supplier_name_normalized == counterparty_name_normalized
    )

    currency_match = _normalize_text(invoice.currency) == _normalize_text(payment.currency)

    date_delta_days = abs((payment.payment_date - invoice.invoice_date).days)
    payment_before_invoice = payment.payment_date < invoice.invoice_date
    payment_after_due_date = (
        payment.payment_date > invoice.due_date if invoice.due_date is not None else None
    )

    invoice_ocr_low_confidence_flag = (
        invoice.ocr_confidence is not None and invoice.ocr_confidence < 0.70
    )

    duplicate_risk_flag = bool(invoice.duplicate_risk_flags or payment.duplicate_risk_flags)

    combined_reference_signal_score = max(
        reference_token_overlap_score,
        1.0 if invoice_number_normalized_match else 0.0,
    )

    return MatchFeatures(
        invoice_id=invoice.invoice_id,
        payment_id=payment.payment_id,
        amount_exact_match=amount_delta_absolute == 0,
        amount_delta_absolute=amount_delta_absolute,
        amount_delta_percentage=amount_delta_percentage,
        currency_match=currency_match,
        date_delta_days=date_delta_days,
        payment_before_invoice=payment_before_invoice,
        payment_after_due_date=payment_after_due_date,
        invoice_number_exact_match=invoice_number_exact_match,
        invoice_number_normalized_match=invoice_number_normalized_match,
        invoice_number_in_payment_reference=invoice_number_in_payment_reference,
        supplier_name_exact_match=supplier_name_exact_match,
        supplier_name_normalized_match=supplier_name_normalized_match,
        reference_token_overlap_score=reference_token_overlap_score,
        combined_reference_signal_score=combined_reference_signal_score,
        invoice_ocr_low_confidence_flag=invoice_ocr_low_confidence_flag,
        duplicate_risk_flag=duplicate_risk_flag,
        extracted_facts={
            "invoice_number_normalized": invoice_number_normalized,
            "payment_reference_normalized": payment_reference_normalized,
            "bank_reference_normalized": bank_reference_normalized,
            "invoice_reference_tokens": invoice_reference_tokens,
            "payment_reference_tokens": payment_reference_tokens,
        },
    )