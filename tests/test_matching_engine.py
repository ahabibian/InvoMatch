from datetime import date
from decimal import Decimal

from invomatch.domain.models import Invoice, MatchResult, Payment
from invomatch.services.matching_engine import match


def test_match_returns_exact_match_with_date_and_reference_weighting():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"), reference="INV-100")
    payments = [
        Payment(id="p2", date=date(2024, 1, 10), amount=Decimal("100.00"), reference="INV-100"),
        Payment(id="p1", date=date(2024, 1, 11), amount=Decimal("25.00")),
    ]

    result = match(invoice, payments)

    assert isinstance(result, MatchResult)
    assert result.status == "matched"
    assert result.payment_id == "p2"
    assert result.confidence_score == 1.0
    assert result.mismatch_reasons == ["amount_match", "date_near", "reference_match"]


def test_match_uses_date_tolerance_for_confidence_when_reference_missing():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"))
    payments = [Payment(id="p1", date=date(2024, 1, 13), amount=Decimal("100.00"))]

    result = match(invoice, payments)

    assert isinstance(result, MatchResult)
    assert result.status == "matched"
    assert result.payment_id == "p1"
    assert result.confidence_score == 0.87
    assert "date_near" in result.mismatch_reasons
    assert "reference_missing" in result.mismatch_reasons


def test_match_uses_far_date_score_and_omits_reference_reason_on_reference_mismatch():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"), reference="INV-100")
    payments = [
        Payment(id="p1", date=date(2024, 1, 20), amount=Decimal("100.00"), reference="OTHER")
    ]

    result = match(invoice, payments)

    assert result.status == "matched"
    assert result.confidence_score == 0.7
    assert result.mismatch_reasons == ["amount_match", "date_far"]


def test_match_detects_duplicate_exact_matches_deterministically_with_scoring():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"), reference="INV-100")
    payments = [
        Payment(id="p2", date=date(2024, 1, 12), amount=Decimal("100.00"), reference="wrong"),
        Payment(id="p1", date=date(2024, 1, 10), amount=Decimal("100.00"), reference="INV-100"),
    ]

    result = match(invoice, payments)

    assert isinstance(result, MatchResult)
    assert result.status == "duplicate_detected"
    assert result.payment_id == "p1"
    assert result.duplicate_payment_ids == ["p2"]
    assert result.confidence_score == 0.8
    assert "duplicate_candidates" in result.mismatch_reasons


def test_match_detects_partial_payment_combination():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"))
    payments = [
        Payment(id="p2", date=date(2024, 1, 12), amount=Decimal("60.00")),
        Payment(id="p1", date=date(2024, 1, 11), amount=Decimal("40.00")),
    ]

    result = match(invoice, payments)

    assert isinstance(result, MatchResult)
    assert result.status == "partial_match"
    assert result.payment_ids == ["p1", "p2"]
    assert result.confidence_score == 0.75
    assert result.mismatch_reasons == ["partial_sum_match"]


def test_match_returns_unmatched_with_clear_reason_taxonomy():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"))
    payments = [Payment(id="p1", date=date(2024, 1, 20), amount=Decimal("35.00"))]

    result = match(invoice, payments)

    assert isinstance(result, MatchResult)
    assert result.status == "unmatched"
    assert result.confidence_score == 0.0
    assert result.mismatch_reasons == ["no_viable_candidate"]
    assert "no_viable_candidate" in result.confidence_explanation


def test_duplicate_selection_is_deterministic_on_tied_scores():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"))
    payments = [
        Payment(id="p2", date=date(2024, 1, 11), amount=Decimal("100.00")),
        Payment(id="p1", date=date(2024, 1, 11), amount=Decimal("100.00")),
    ]

    result = match(invoice, payments)

    assert result.status == "duplicate_detected"
    assert result.payment_id == "p1"
    assert result.duplicate_payment_ids == ["p2"]


def test_explanation_contains_reasons_for_auditability():
    invoice = Invoice(id="i1", date=date(2024, 1, 10), amount=Decimal("100.00"), reference="INV-100")
    payments = [Payment(id="p1", date=date(2024, 1, 10), amount=Decimal("100.00"), reference="INV-100")]

    result = match(invoice, payments)

    assert result.status == "matched"
    assert "amount_match" in result.confidence_explanation
    assert "date_near" in result.confidence_explanation
    assert "reference_match" in result.confidence_explanation
