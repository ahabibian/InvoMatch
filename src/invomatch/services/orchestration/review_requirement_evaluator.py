from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ReviewRequirementResult:
    requires_review: bool
    review_items: List[Dict]


class ReviewRequirementEvaluator:
    def evaluate(self, reconciliation_results: List[Dict]) -> ReviewRequirementResult:
        review_items = []

        for item in reconciliation_results:
            status = item.get("status")

            if status in {
                "unmatched",
                "ambiguous",
                "low_confidence",
                "conflict",
                "forced_review",
            }:
                review_items.append(item)

        return ReviewRequirementResult(
            requires_review=len(review_items) > 0,
            review_items=review_items,
        )