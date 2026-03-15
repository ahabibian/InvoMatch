from datetime import date
from decimal import Decimal

from invomatch.domain.models import Invoice, Payment
from invomatch.services.matching_engine import match


def test_match_returns_exact_match_with_full_confidence():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"))
    payments = [
        Payment(id="p2", date=date(2024, 1, 12), amount=Decimal("100.00")),
        Payment(id="p1", date=date(2024, 1, 11), amount=Decimal("25.00")),
    ]

    result = match(invoice, payments)

    assert result == {
        "status": "matched",
        "payment_id": "p2",
        "confidence_score": 1.0,
        "confidence_explanation": "Single exact amount match found.",
    }


def test_match_detects_duplicate_exact_matches_deterministically():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"))
    payments = [
        Payment(id="p2", date=date(2024, 1, 12), amount=Decimal("100.00")),
        Payment(id="p1", date=date(2024, 1, 11), amount=Decimal("100.00")),
    ]

    result = match(invoice, payments)

    assert result == {
        "status": "duplicate_detected",
        "payment_id": "p1",
        "duplicate_payment_ids": ["p2"],
        "confidence_score": 0.6,
        "confidence_explanation": "Multiple exact amount matches found; first candidate selected deterministically.",
    }


def test_match_detects_partial_payment_combination():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"))
    payments = [
        Payment(id="p2", date=date(2024, 1, 12), amount=Decimal("60.00")),
        Payment(id="p1", date=date(2024, 1, 11), amount=Decimal("40.00")),
    ]

    result = match(invoice, payments)

    assert result == {
        "status": "partial_match",
        "payment_ids": ["p1", "p2"],
        "confidence_score": 0.75,
        "confidence_explanation": "No exact match found; combined partial payments equal invoice amount.",
    }


def test_match_returns_unmatched_when_no_pattern_fits():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"))
    payments = [Payment(id="p1", date=date(2024, 1, 11), amount=Decimal("35.00"))]

    result = match(invoice, payments)

    assert result == {
        "status": "unmatched",
        "confidence_score": 0.0,
        "confidence_explanation": "No exact or complete partial payment match found.",
    }
