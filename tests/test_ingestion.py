from datetime import date
from decimal import Decimal

import pytest

from invomatch.domain.models import Invoice, Payment
from invomatch.services.ingestion import parse_invoice_row, parse_payment_row


def test_parse_invoice_row_with_valid_values():
    invoice = parse_invoice_row(
        {
            "id": "INV-1001",
            "date": "2024-01-03",
            "amount": "120.00",
            "reference": "  Invoice REF-001  ",
        }
    )

    assert isinstance(invoice, Invoice)
    assert invoice.id == "INV-1001"
    assert invoice.date == date(2024, 1, 3)
    assert invoice.amount == Decimal("120.00")
    assert invoice.reference == "Invoice REF-001"


def test_parse_payment_row_with_valid_values():
    payment = parse_payment_row(
        {
            "id": "PAY-1001",
            "date": "2024-01-05",
            "amount": "120.00",
            "reference": "  Payment REF-001  ",
        }
    )

    assert isinstance(payment, Payment)
    assert payment.id == "PAY-1001"
    assert payment.date == date(2024, 1, 5)
    assert payment.amount == Decimal("120.00")
    assert payment.reference == "Payment REF-001"


def test_parse_row_raises_on_missing_amount():
    with pytest.raises(ValueError, match="Missing required field 'amount'"):
        parse_invoice_row({"id": "INV-1001", "date": "2024-01-03", "amount": "   "})


def test_parse_row_raises_on_invalid_date():
    with pytest.raises(ValueError, match="Invalid date"):
        parse_payment_row({"id": "PAY-1001", "date": "01-05-2024", "amount": "120.00"})


def test_blank_reference_is_normalized_to_none():
    invoice = parse_invoice_row(
        {
            "id": "INV-1001",
            "date": "2024-01-03",
            "amount": "120.00",
            "reference": "   ",
        }
    )

    payment = parse_payment_row(
        {
            "id": "PAY-1001",
            "date": "2024-01-05",
            "amount": "120.00",
            "reference": "  ",
        }
    )

    assert invoice.reference is None
    assert payment.reference is None
