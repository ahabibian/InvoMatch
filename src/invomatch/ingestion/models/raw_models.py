from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class RawInvoiceInput(BaseModel):
    external_id: Optional[str] = None
    invoice_number: Optional[str] = None

    issue_date: Optional[str] = None
    due_date: Optional[str] = None

    currency: Optional[str] = None

    gross_amount: Optional[str] = None
    net_amount: Optional[str] = None
    tax_amount: Optional[str] = None

    counterparty: Optional[str] = None

    metadata: Optional[Dict[str, Any]] = None


class RawPaymentInput(BaseModel):
    external_id: Optional[str] = None
    payment_reference: Optional[str] = None

    payment_date: Optional[str] = None

    amount: Optional[str] = None
    currency: Optional[str] = None

    counterparty: Optional[str] = None

    metadata: Optional[Dict[str, Any]] = None


class RawIngestionEnvelope(BaseModel):
    source: Optional[str] = None
    received_at: Optional[datetime] = None

    payload: Dict[str, Any]