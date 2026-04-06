from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class ValidationError(BaseModel):
    field: Optional[str]
    message: str
    code: str


class ValidationWarning(BaseModel):
    field: Optional[str]
    message: str
    code: str


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationWarning]