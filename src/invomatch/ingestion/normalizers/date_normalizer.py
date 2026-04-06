from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from .string_normalizer import normalize_optional_string


_ACCEPTED_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
)


def normalize_date(value: Optional[str]) -> Optional[date]:
    normalized = normalize_optional_string(value)
    if normalized is None:
        return None

    for fmt in _ACCEPTED_DATE_FORMATS:
        try:
            return datetime.strptime(normalized, fmt).date()
        except ValueError:
            continue

    return None