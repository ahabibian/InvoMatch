from __future__ import annotations

from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel

from .normalized_models import NormalizedInvoice, NormalizedPayment
from .validation_models import ValidationResult


class IngestionStatus:
    REJECTED = "rejected"
    ACCEPTED_WITH_FLAGS = "accepted_with_flags"
    ACCEPTED_CLEAN = "accepted_clean"


class IngestionResult(BaseModel):
    status: str

    validation: ValidationResult

    normalized: Optional[Union[NormalizedInvoice, NormalizedPayment]]

    raw_reference: Optional[str]

    processed_at: datetime

    idempotency_key: Optional[str]

    notes: Optional[str] = None