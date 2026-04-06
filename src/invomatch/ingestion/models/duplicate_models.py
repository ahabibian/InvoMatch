from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class DuplicateClassification(str, Enum):
    UNIQUE = "unique"
    EXACT_REPLAY = "exact_replay"
    SEMANTIC_DUPLICATE = "semantic_duplicate"
    CONFLICT = "conflict"


class DuplicateCheckResult(BaseModel):
    classification: DuplicateClassification
    reason: str
    semantic_key: Optional[str] = None
    compared_against_idempotency_key: Optional[str] = None