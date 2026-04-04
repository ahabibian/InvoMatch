from typing import Any, Dict, List

from invomatch.services.orchestration.review_case_factory import ReviewCaseFactory


_REVIEW_REQUIRED_STATUSES = {
    "unmatched",
    "ambiguous",
    "low_confidence",
    "conflict",
    "forced_review",
}


class ReviewCaseGenerationService:
    def __init__(self) -> None:
        self._factory = ReviewCaseFactory()

    def generate(self, outcomes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        review_cases: List[Dict[str, Any]] = []
        seen_invoice_ids = set()

        for outcome in outcomes:
            invoice_id = outcome.get("invoice_id")
            status = outcome.get("status")

            if status not in _REVIEW_REQUIRED_STATUSES:
                continue

            if invoice_id in seen_invoice_ids:
                continue

            review_cases.append(self._factory.build(outcome))
            seen_invoice_ids.add(invoice_id)

        return review_cases