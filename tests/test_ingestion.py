from decimal import Decimal

import pytest

from invomatch.services.ingestion import parse_invoice_row, parse_payment_row


def test_parse_invoice_row_with_valid_values():
    invoice = parse_invoice_row(
        {
            "id": "INV-1001",
            "date": "2024-01-03",
            "amount": "120.00",
            "reference": "  Invoice REF-001  ",
            "currency": "SEK",
        }
    )

    assert invoice.id == "INV-1001"
    assert invoice.amount == Decimal("120.00")
    assert invoice.reference == "Invoice REF-001"
    assert invoice.currency == "SEK"


def test_parse_payment_row_with_valid_values():
    payment = parse_payment_row(
        {
            "id": "PAY-1001",
            "date": "2024-01-05",
            "amount": "120.00",
            "reference": "  Payment REF-001  ",
            "currency": "SEK",
        }
    )

    assert payment.id == "PAY-1001"
    assert payment.amount == Decimal("120.00")
    assert payment.reference == "Payment REF-001"
    assert payment.currency == "SEK"


def test_parse_invoice_row_requires_reference_to_be_optional():
    invoice = parse_invoice_row(
        {
            "id": "INV-1001",
            "date": "2024-01-03",
            "amount": "120.00",
            "currency": "SEK",
        }
    )

    assert invoice.reference is None
    assert invoice.currency == "SEK"


def test_parse_payment_row_requires_amount_field():
    with pytest.raises(ValueError, match="amount"):
        parse_payment_row(
            {
                "id": "PAY-1001",
                "date": "2024-01-05",
                "reference": "Payment REF-001",
                "currency": "SEK",
            }
        )


def test_blank_reference_is_normalized_to_none():
    invoice = parse_invoice_row(
        {
            "id": "INV-1001",
            "date": "2024-01-03",
            "amount": "120.00",
            "reference": "   ",
            "currency": "SEK",
        }
    )

    assert invoice.reference is None
    assert invoice.currency == "SEK"