from __future__ import annotations

from enum import Enum
from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel

from .normalized_models import NormalizedInvoice, NormalizedPayment
from .traceability_models import RawTraceReference
from .validation_models import ValidationResult


class IngestionStatus(str, Enum):
    REJECTED = "rejected"
    ACCEPTED_WITH_FLAGS = "accepted_with_flags"
    ACCEPTED_CLEAN = "accepted_clean"


class IngestionResult(BaseModel):
    status: IngestionStatus
    validation: ValidationResult
    normalized: Optional[Union[NormalizedInvoice, NormalizedPayment]]
    raw_reference: RawTraceReference
    processed_at: datetime
    idempotency_key: str
    semantic_key: Optional[str] = None
    notes: Optional[str] = None