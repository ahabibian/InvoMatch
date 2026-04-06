from __future__ import annotations

from typing import Optional

from .string_normalizer import normalize_upper_string


_ALLOWED_CURRENCY_CODES = {
    "SEK",
    "EUR",
    "USD",
    "GBP",
    "NOK",
    "DKK",
}


def normalize_currency(value: Optional[str]) -> Optional[str]:
    normalized = normalize_upper_string(value)
    if normalized is None:
        return None

    if normalized not in _ALLOWED_CURRENCY_CODES:
        return None

    return normalized