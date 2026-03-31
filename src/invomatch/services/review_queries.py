from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(slots=True)
class ReviewCaseProjection:
    case_id: str
    run_id: str
    status: str
    reason_code: str
    match_id: Optional[str] = None
    recommended_action: Optional[str] = None


def _normalize_review_status(item_status: str) -> str:
    normalized = str(item_status).upper()

    if normalized in {"PENDING", "IN_REVIEW", "DEFERRED"}:
        return "open"

    if normalized in {"APPROVED", "MODIFIED", "CLOSED"}:
        return "resolved"

    if normalized in {"REJECTED"}:
        return "dismissed"

    return "open"


def _extract_reason_code(feedback: Any) -> str:
    raw_payload = getattr(feedback, "raw_payload", None)
    if isinstance(raw_payload, dict):
        for key in ("reason_code", "primary_mismatch_code", "review_reason"):
            value = raw_payload.get(key)
            if value:
                return str(value)
    return "manual_review"


def _extract_match_id(feedback: Any) -> Optional[str]:
    raw_payload = getattr(feedback, "raw_payload", None)
    if isinstance(raw_payload, dict):
        for key in ("match_id", "candidate_match_id"):
            value = raw_payload.get(key)
            if value:
                return str(value)
    return None


def _extract_recommended_action(review_item: Any) -> Optional[str]:
    decision = getattr(review_item, "current_decision", None)
    if decision is None:
        return None
    return str(getattr(decision, "value", decision)).lower()


class ReviewQueryService:
    """
    Query-side boundary for assembling product-facing review cases.

    Current implementation depends on a review store that exposes:
    - list_review_items()
    - get_feedback(feedback_id)

    This is intentionally minimal and suitable for the current in-memory
    review store. SQLite-backed review query coverage can be added later.
    """

    def __init__(self, review_store: Any) -> None:
        self._review_store = review_store

    def get_review_case_for_run(self, run_id: str) -> Optional[ReviewCaseProjection]:
        list_review_items = getattr(self._review_store, "list_review_items", None)
        get_feedback = getattr(self._review_store, "get_feedback", None)

        if list_review_items is None or get_feedback is None:
            return None

        for review_item in list_review_items():
            feedback = get_feedback(review_item.feedback_id)
            if feedback is None:
                continue

            if str(getattr(feedback, "run_id", "")) != str(run_id):
                continue

            return ReviewCaseProjection(
                case_id=str(review_item.review_item_id),
                run_id=str(run_id),
                status=_normalize_review_status(str(review_item.item_status)),
                reason_code=_extract_reason_code(feedback),
                match_id=_extract_match_id(feedback),
                recommended_action=_extract_recommended_action(review_item),
            )

        return None