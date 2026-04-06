from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class NormalizedInvoice(BaseModel):
    external_id: Optional[str]

    invoice_number: str

    issue_date: date
    due_date: Optional[date]

    currency: str

    gross_amount: Decimal
    net_amount: Optional[Decimal]
    tax_amount: Optional[Decimal]

    counterparty: Optional[str]


class NormalizedPayment(BaseModel):
    external_id: Optional[str]

    payment_reference: str

    payment_date: date

    amount: Decimal
    currency: str

    counterparty: Optional[str]