from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Optional

from .string_normalizer import normalize_optional_string


_CANONICAL_QUANTUM = Decimal("0.01")


def normalize_amount(value: Optional[str]) -> Optional[Decimal]:
    normalized = normalize_optional_string(value)
    if normalized is None:
        return None

    candidate = normalized.replace(",", ".")

    try:
        parsed = Decimal(candidate)
    except InvalidOperation:
        return None

    return parsed.quantize(_CANONICAL_QUANTUM, rounding=ROUND_HALF_UP)