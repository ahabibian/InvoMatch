from datetime import date
from decimal import Decimal

from invomatch.domain.models import Invoice, MatchResult, Payment


DATE_EXACT_SCORE = 0.2
DATE_NEAR_SCORE = 0.12
DATE_FAR_SCORE = 0.0
REFERENCE_EXACT_SCORE = 0.1
REFERENCE_MISSING_SCORE = 0.05

AMOUNT_WEIGHT = 0.7
DUPLICATE_MATCH_CONFIDENCE = 0.6
PARTIAL_MATCH_CONFIDENCE = 0.75
UNMATCHED_CONFIDENCE = 0.0
DATE_TOLERANCE_DAYS = 3


def _ordered(payments: list[Payment]) -> list[Payment]:
    return sorted(payments, key=lambda p: (p.date, p.id))


def _reference_equal(invoice_reference: str | None, payment_reference: str | None) -> bool:
    if invoice_reference is None or payment_reference is None:
        return False
    return invoice_reference.strip().casefold() == payment_reference.strip().casefold()


def _date_score(invoice_date: date, payment_date: date) -> tuple[float, str]:
    days_diff = abs((payment_date - invoice_date).days)
    if days_diff == 0:
        return DATE_EXACT_SCORE, "date_near"
    if days_diff <= DATE_TOLERANCE_DAYS:
        return DATE_NEAR_SCORE, "date_near"
    return DATE_FAR_SCORE, "date_far"


def _reference_score(invoice: Invoice, payment: Payment) -> tuple[float, str | None]:
    if _reference_equal(invoice.reference, payment.reference):
        return REFERENCE_EXACT_SCORE, "reference_match"
    if invoice.reference is None or payment.reference is None:
        return REFERENCE_MISSING_SCORE, "reference_missing"
    return 0.0, None


def _candidate_score(invoice: Invoice, payment: Payment) -> tuple[float, list[str]]:
    date_score, date_reason = _date_score(invoice.date, payment.date)
    reference_score, reference_reason = _reference_score(invoice, payment)
    score = AMOUNT_WEIGHT + date_score + reference_score
    reasons = ["amount_match", date_reason]
    if reference_reason is not None:
        reasons.append(reference_reason)
    return round(score, 2), reasons


def _explanation(base: str, reasons: list[str]) -> str:
    return f"{base} Reasons: {', '.join(reasons)}."


def match(invoice: Invoice, payments: list[Payment]) -> MatchResult:
    ordered_payments = _ordered(payments)
    exact_matches = [p for p in ordered_payments if p.amount == invoice.amount]

    if len(exact_matches) == 1:
        payment = exact_matches[0]
        score, reasons = _candidate_score(invoice, payment)
        return MatchResult(
            status="matched",
            payment_id=payment.id,
            confidence_score=score,
            confidence_explanation=_explanation(
                "Single exact amount candidate scored using date and reference signals.",
                reasons,
            ),
            mismatch_reasons=reasons,
        )

    if len(exact_matches) > 1:
        scored_candidates = [
            (payment, *_candidate_score(invoice, payment)) for payment in exact_matches
        ]
        scored_candidates.sort(key=lambda item: (-item[1], item[0].date, item[0].id))
        primary_payment, primary_score, primary_reasons = scored_candidates[0]
        duplicate_ids = [payment.id for payment, _, _ in scored_candidates[1:]]

        return MatchResult(
            status="duplicate_detected",
            payment_id=primary_payment.id,
            duplicate_payment_ids=duplicate_ids,
            confidence_score=round(max(DUPLICATE_MATCH_CONFIDENCE, primary_score - 0.2), 2),
            confidence_explanation=_explanation(
                "Multiple exact amount candidates found; best score selected and ties resolved deterministically.",
                primary_reasons + ["duplicate_candidates"],
            ),
            mismatch_reasons=primary_reasons + ["duplicate_candidates"],
        )

    partial_payments = [p for p in ordered_payments if Decimal("0") < p.amount < invoice.amount]
    partial_total = sum((p.amount for p in partial_payments), start=Decimal("0"))

    if partial_payments and partial_total == invoice.amount:
        return MatchResult(
            status="partial_match",
            payment_ids=[p.id for p in partial_payments],
            confidence_score=PARTIAL_MATCH_CONFIDENCE,
            confidence_explanation=_explanation(
                "No exact candidate found; combined partial payments equal invoice amount.",
                ["partial_sum_match"],
            ),
            mismatch_reasons=["partial_sum_match"],
        )

    return MatchResult(
        status="unmatched",
        confidence_score=UNMATCHED_CONFIDENCE,
        confidence_explanation=_explanation(
            "No exact or complete partial payment candidate found.",
            ["no_viable_candidate"],
        ),
        mismatch_reasons=["no_viable_candidate"],
    )
