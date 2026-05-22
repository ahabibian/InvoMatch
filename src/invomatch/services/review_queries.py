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


@dataclass(slots=True)
class ReviewQueueRowProjection:
    case_id: str
    run_id: str
    status: str
    reason_code: str
    match_id: Optional[str] = None
    priority: Optional[str] = None


@dataclass(slots=True)
class MatchDetailProjection:
    match_id: str
    run_id: str
    status: str
    reason_code: str
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None
    confidence: Optional[float] = None
    source_references: tuple[str, ...] = ()


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


def _is_terminal_review_item(review_item: Any) -> bool:
    closed_at = getattr(review_item, "closed_at", None)
    if closed_at is not None:
        return True

    is_closed = getattr(review_item, "is_closed", None)
    if isinstance(is_closed, bool):
        return is_closed
    if callable(is_closed):
        return bool(is_closed())

    current_decision = getattr(review_item, "current_decision", None)
    if current_decision is not None:
        return True

    return False

def _extract_recommended_action(review_item: Any) -> Optional[str]:
    decision = getattr(review_item, "current_decision", None)
    if decision is None:
        return None
    return str(getattr(decision, "value", decision)).lower()


def _optional_str(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    return str(value)


def _optional_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    return float(value)


class ReviewQueryService:
    """Query-side boundary for assembling product-facing review cases."""

    def init(self, review_store: Any) -> None:
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

    def list_review_queue_rows(self) -> list[ReviewQueueRowProjection]:
        list_review_items = getattr(self._review_store, "list_review_items", None)
        get_feedback = getattr(self._review_store, "get_feedback", None)

        if list_review_items is None or get_feedback is None:
            return []

        rows: list[ReviewQueueRowProjection] = []

        for review_item in list_review_items():
            feedback = get_feedback(review_item.feedback_id)
            if feedback is None:
                continue

            status = _normalize_review_status(str(review_item.item_status))
            if status != "open":
                continue

            rows.append(
                ReviewQueueRowProjection(
                    case_id=str(review_item.review_item_id),
                    run_id=str(getattr(feedback, "run_id", "")),
                    status=status,
                    reason_code=_extract_reason_code(feedback),
                    match_id=_extract_match_id(feedback),
                    priority=None,
                )
            )

        return rows

    def list_match_detail_candidates(self) -> list[MatchDetailProjection]:
        list_review_items = getattr(self._review_store, "list_review_items", None)
        get_feedback = getattr(self._review_store, "get_feedback", None)

        if list_review_items is None or get_feedback is None:
            return []

        candidates: list[MatchDetailProjection] = []

        for review_item in list_review_items():
            feedback = get_feedback(review_item.feedback_id)
            if feedback is None:
                continue

            match_id = _extract_match_id(feedback)
            if not match_id:
                continue

            raw_payload = getattr(feedback, "raw_payload", None)
            if not isinstance(raw_payload, dict):
                raw_payload = {}

            source_reference = getattr(feedback, "source_reference", None)

            candidates.append(
                MatchDetailProjection(
                    match_id=str(match_id),
                    run_id=str(getattr(feedback, "run_id", "")),
                    status=_normalize_review_status(str(review_item.item_status)),
                    reason_code=_extract_reason_code(feedback),
                    invoice_id=_optional_str(raw_payload.get("invoice_id")),
                    payment_id=_optional_str(raw_payload.get("payment_id")),
                    confidence=_optional_float(raw_payload.get("confidence")),
                    source_references=(str(source_reference),) if source_reference else (),
                )
            )

        return candidates
