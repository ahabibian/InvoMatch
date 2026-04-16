from dataclasses import dataclass
from typing import Dict, List


RUNTIME_REVIEW_REQUIRED_STATUSES = {
    "unmatched",
    "partial_match",
    "duplicate_detected",
}


@dataclass
class ReviewRequirementResult:
    requires_review: bool
    review_items: List[Dict]


class ReviewRequirementEvaluator:
    def evaluate(self, reconciliation_results: List[Dict]) -> ReviewRequirementResult:
        review_items = []

        for item in reconciliation_results:
            status = str(item.get("status", "")).strip().lower()

            if status in RUNTIME_REVIEW_REQUIRED_STATUSES:
                review_items.append(item)

        return ReviewRequirementResult(
            requires_review=len(review_items) > 0,
            review_items=review_items,
        )