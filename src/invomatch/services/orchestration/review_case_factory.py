from typing import Any, Dict


class ReviewCaseFactory:
    def build(self, outcome: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "invoice_id": outcome["invoice_id"],
            "status": "pending",
            "reason": outcome.get("reason", "manual_review_required"),
            "blocking": True,
            "candidates": outcome.get("candidates", []),
            "confidence": outcome.get("confidence"),
            "source_status": outcome.get("status"),
        }