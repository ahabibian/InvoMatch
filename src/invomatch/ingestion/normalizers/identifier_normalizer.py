from __future__ import annotations

from typing import Optional

from .string_normalizer import normalize_optional_string, normalize_upper_string


def normalize_invoice_number(value: Optional[str]) -> Optional[str]:
    normalized = normalize_upper_string(value)
    if normalized is None:
        return None

    normalized = normalized.replace(" ", "")
    return normalized


def normalize_payment_reference(value: Optional[str]) -> Optional[str]:
    normalized = normalize_upper_string(value)
    if normalized is None:
        return None

    normalized = normalized.replace(" ", "")
    return normalized


def normalize_external_id(value: Optional[str]) -> Optional[str]:
    return normalize_optional_string(value)