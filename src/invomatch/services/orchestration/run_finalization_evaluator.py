from dataclasses import dataclass
from typing import Dict, List


_BLOCKING_REVIEW_STATUSES = {
    "pending",
    "deferred",
    "reopened",
    "in_review",
}


@dataclass
class RunFinalizationResult:
    is_finalizable: bool


class RunFinalizationEvaluator:
    def evaluate(
        self,
        review_items: List[Dict],
        matching_completed: bool,
    ) -> RunFinalizationResult:
        if not matching_completed:
            return RunFinalizationResult(is_finalizable=False)

        for item in review_items:
            raw_status = item.get("status")
            normalized_status = str(raw_status).strip().lower()

            if normalized_status in _BLOCKING_REVIEW_STATUSES:
                return RunFinalizationResult(is_finalizable=False)

        return RunFinalizationResult(is_finalizable=True)