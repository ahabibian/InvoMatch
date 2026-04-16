from typing import Any, Dict


_REASON_BY_SOURCE_STATUS = {
    "unmatched": "no_match",
    "partial_match": "partial_match_requires_review",
    "duplicate_detected": "duplicate_candidates_require_review",
}


class ReviewCaseFactory:
    def build(self, outcome: Dict[str, Any]) -> Dict[str, Any]:
        source_status = str(outcome.get("status", "")).strip().lower()

        return {
            "invoice_id": outcome["invoice_id"],
            "status": "pending",
            "reason": outcome.get(
                "reason",
                _REASON_BY_SOURCE_STATUS.get(source_status, "manual_review_required"),
            ),
            "blocking": True,
            "candidates": outcome.get("candidates", []),
            "confidence": outcome.get("confidence"),
            "source_status": source_status,
        }