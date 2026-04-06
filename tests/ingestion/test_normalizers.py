from decimal import Decimal
from datetime import date

from invomatch.ingestion.normalizers import (
    normalize_amount,
    normalize_currency,
    normalize_date,
    normalize_external_id,
    normalize_invoice_number,
    normalize_optional_string,
    normalize_payment_reference,
)


def test_normalize_optional_string_trims_and_collapses_whitespace():
    assert normalize_optional_string("  A   B  ") == "A B"


def test_normalize_optional_string_empty_to_none():
    assert normalize_optional_string("   ") is None


def test_normalize_invoice_number_uppercases_and_removes_spaces():
    assert normalize_invoice_number(" inv  001 ") == "INV001"


def test_normalize_payment_reference_uppercases_and_removes_spaces():
    assert normalize_payment_reference(" rf  123 45 ") == "RF12345"


def test_normalize_external_id_preserves_internal_spacing_shape():
    assert normalize_external_id("  ext  1 ") == "ext 1"


def test_normalize_currency_accepts_allowed_code():
    assert normalize_currency(" sek ") == "SEK"


def test_normalize_currency_rejects_unknown_code():
    assert normalize_currency("AUD") is None


def test_normalize_amount_accepts_dot_decimal():
    assert normalize_amount("123.456") == Decimal("123.46")


def test_normalize_amount_accepts_comma_decimal():
    assert normalize_amount("123,456") == Decimal("123.46")


def test_normalize_amount_rejects_invalid_value():
    assert normalize_amount("abc") is None


def test_normalize_date_accepts_iso_format():
    assert normalize_date("2026-04-07") == date(2026, 4, 7)


def test_normalize_date_accepts_day_first_format():
    assert normalize_date("07/04/2026") == date(2026, 4, 7)


def test_normalize_date_rejects_invalid_date():
    assert normalize_date("2026-99-99") is None