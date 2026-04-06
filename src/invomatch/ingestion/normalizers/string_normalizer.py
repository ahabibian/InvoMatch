from __future__ import annotations

import unicodedata
from typing import Optional


def normalize_optional_string(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.strip()

    if normalized == "":
        return None

    normalized = " ".join(normalized.split())
    return normalized


def normalize_upper_string(value: Optional[str]) -> Optional[str]:
    normalized = normalize_optional_string(value)
    if normalized is None:
        return None
    return normalized.upper()