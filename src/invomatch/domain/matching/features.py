from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Mapping


@dataclass(frozen=True, slots=True)
class InvoiceRecord:
    invoice_id: str
    supplier_name: str
    invoice_number: str
    invoice_date: date
    due_date: date | None
    currency: str
    gross_amount: float
    reference_text: str = ""
    ocr_confidence: float | None = None
    duplicate_risk_flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.invoice_id.strip():
            raise ValueError("invoice_id must not be empty.")
        if not self.supplier_name.strip():
            raise ValueError("supplier_name must not be empty.")
        if not self.invoice_number.strip():
            raise ValueError("invoice_number must not be empty.")
        if not self.currency.strip():
            raise ValueError("currency must not be empty.")
        if self.gross_amount < 0:
            raise ValueError("gross_amount must be >= 0.")
        if self.ocr_confidence is not None and not (0.0 <= self.ocr_confidence <= 1.0):
            raise ValueError("ocr_confidence must be between 0.0 and 1.0.")


@dataclass(frozen=True, slots=True)
class PaymentRecord:
    payment_id: str
    counterparty_name: str
    payment_date: date
    currency: str
    amount: float
    reference_text: str = ""
    bank_reference: str = ""
    duplicate_risk_flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.payment_id.strip():
            raise ValueError("payment_id must not be empty.")
        if not self.counterparty_name.strip():
            raise ValueError("counterparty_name must not be empty.")
        if not self.currency.strip():
            raise ValueError("currency must not be empty.")
        if self.amount < 0:
            raise ValueError("amount must be >= 0.")


@dataclass(frozen=True, slots=True)
class MatchFeatures:
    invoice_id: str
    payment_id: str

    amount_exact_match: bool
    amount_delta_absolute: float
    amount_delta_percentage: float

    currency_match: bool

    date_delta_days: int
    payment_before_invoice: bool
    payment_after_due_date: bool | None

    invoice_number_exact_match: bool
    invoice_number_normalized_match: bool
    invoice_number_in_payment_reference: bool

    supplier_name_exact_match: bool
    supplier_name_normalized_match: bool

    reference_token_overlap_score: float
    combined_reference_signal_score: float

    invoice_ocr_low_confidence_flag: bool
    duplicate_risk_flag: bool

    extracted_facts: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.invoice_id.strip():
            raise ValueError("invoice_id must not be empty.")
        if not self.payment_id.strip():
            raise ValueError("payment_id must not be empty.")
        if self.amount_delta_absolute < 0:
            raise ValueError("amount_delta_absolute must be >= 0.")
        if self.amount_delta_percentage < 0:
            raise ValueError("amount_delta_percentage must be >= 0.")
        if not (0.0 <= self.reference_token_overlap_score <= 1.0):
            raise ValueError("reference_token_overlap_score must be between 0.0 and 1.0.")
        if not (0.0 <= self.combined_reference_signal_score <= 1.0):
            raise ValueError("combined_reference_signal_score must be between 0.0 and 1.0.")