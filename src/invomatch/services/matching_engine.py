from decimal import Decimal

from invomatch.domain.models import Invoice, MatchResult, Payment


EXACT_MATCH_CONFIDENCE = 1.0
DUPLICATE_MATCH_CONFIDENCE = 0.6
PARTIAL_MATCH_CONFIDENCE = 0.75
UNMATCHED_CONFIDENCE = 0.0


def _ordered(payments: list[Payment]) -> list[Payment]:
    return sorted(payments, key=lambda p: (p.date, p.id))


def match(invoice: Invoice, payments: list[Payment]) -> MatchResult:
    ordered_payments = _ordered(payments)
    exact_matches = [p for p in ordered_payments if p.amount == invoice.amount]

    if len(exact_matches) == 1:
        payment = exact_matches[0]
        return MatchResult(
            status="matched",
            payment_id=payment.id,
            confidence_score=EXACT_MATCH_CONFIDENCE,
            confidence_explanation="Single exact amount match found.",
        )

    if len(exact_matches) > 1:
        primary = exact_matches[0]
        duplicate_ids = [p.id for p in exact_matches[1:]]
        return MatchResult(
            status="duplicate_detected",
            payment_id=primary.id,
            duplicate_payment_ids=duplicate_ids,
            confidence_score=DUPLICATE_MATCH_CONFIDENCE,
            confidence_explanation="Multiple exact amount matches found; first candidate selected deterministically.",
        )

    partial_payments = [p for p in ordered_payments if Decimal("0") < p.amount < invoice.amount]
    partial_total = sum((p.amount for p in partial_payments), start=Decimal("0"))

    if partial_payments and partial_total == invoice.amount:
        return MatchResult(
            status="partial_match",
            payment_ids=[p.id for p in partial_payments],
            confidence_score=PARTIAL_MATCH_CONFIDENCE,
            confidence_explanation="No exact match found; combined partial payments equal invoice amount.",
        )

    return MatchResult(
        status="unmatched",
        confidence_score=UNMATCHED_CONFIDENCE,
        confidence_explanation="No exact or complete partial payment match found.",
    )
