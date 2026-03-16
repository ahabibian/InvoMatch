from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Mapping

from invomatch.domain.models import Invoice, Payment


def _clean_value(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _require_field(row: Mapping[str, str | None], field_name: str) -> str:
    value = _clean_value(row.get(field_name))
    if value is None:
        raise ValueError(f"Missing required field '{field_name}'")
    return value


def _parse_date(raw_value: str, field_name: str = "date") -> date:
    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name}: {raw_value}") from exc


def _parse_amount(raw_value: str) -> Decimal:
    try:
        return Decimal(raw_value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid amount: {raw_value}") from exc


def normalize_reference(value: str | None) -> str | None:
    return _clean_value(value)


def parse_invoice_row(row: Mapping[str, str | None]) -> Invoice:
    return Invoice(
        id=_require_field(row, "id"),
        date=_parse_date(_require_field(row, "date")),
        amount=_parse_amount(_require_field(row, "amount")),
        reference=normalize_reference(row.get("reference")),
    )


def parse_payment_row(row: Mapping[str, str | None]) -> Payment:
    return Payment(
        id=_require_field(row, "id"),
        date=_parse_date(_require_field(row, "date")),
        amount=_parse_amount(_require_field(row, "amount")),
        reference=normalize_reference(row.get("reference")),
    )


def load_invoices_from_csv(path: Path) -> list[Invoice]:
    invoices: list[Invoice] = []
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            invoices.append(parse_invoice_row(row))
    return invoices


def load_payments_from_csv(path: Path) -> list[Payment]:
    payments: list[Payment] = []
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            payments.append(parse_payment_row(row))
    return payments
