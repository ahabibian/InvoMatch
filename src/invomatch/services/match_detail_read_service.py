"""Backend-owned Match Detail / Evidence read service."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Iterable

from invomatch.api.product_models.review_case import (
    ProductMatchDetailEvidenceItem,
    ProductMatchDetailFailure,
    ProductMatchDetailResponse,
    ProductMatchDetailTraceability,
)


class MatchDetailFailureCode(StrEnum):
    MATCH_NOT_FOUND = "match_not_found"
    MISSING_EVIDENCE = "missing_evidence"
    UNAVAILABLE_EVIDENCE = "unavailable_evidence"
    MALFORMED_PAYLOAD = "malformed_or_incomplete_payload"
    BACKEND_ERROR = "backend_error"


class MatchDetailReadError(RuntimeError):
    """Base error for backend-owned Match Detail failure semantics."""

    failure_code: MatchDetailFailureCode

    def __init__(self, failure_code: MatchDetailFailureCode, message: str) -> None:
        super().__init__(message)
        self.failure_code = failure_code
        self.message = message

    def to_failure(self) -> ProductMatchDetailFailure:
        return ProductMatchDetailFailure(
            code=self.failure_code.value,
            message=self.message,
        )


def _get_attr(source: Any, name: str, default: Any = None) -> Any:
    if isinstance(source, dict):
        return source.get(name, default)
    return getattr(source, name, default)


def _as_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def build_match_detail_response(match: Any) -> ProductMatchDetailResponse:
    """Build backend-owned product-facing Match Detail response."""

    match_id = _as_string(_get_attr(match, "match_id", None))
    if not match_id:
        match_id = _as_string(_get_attr(match, "id", None))

    if not match_id:
        raise MatchDetailReadError(
            MatchDetailFailureCode.MALFORMED_PAYLOAD,
            "Match detail payload is missing match_id.",
        )

    invoice_id = _as_string(_get_attr(match, "invoice_id", None))
    payment_id = _as_string(_get_attr(match, "payment_id", None))
    status = str(_get_attr(match, "status", "unknown"))

    return ProductMatchDetailResponse(
        match_id=match_id,
        match_status=status,
        invoice_summary={"invoice_id": invoice_id} if invoice_id else {},
        payment_summary={"payment_id": payment_id} if payment_id else {},
        evidence=[
            ProductMatchDetailEvidenceItem(
                evidence_id=match_id + ":status",
                evidence_type="match_status",
                label="Match status",
                value=status,
                source="backend_match_record",
            )
        ],
        traceability=ProductMatchDetailTraceability(
            invoice_id=invoice_id,
            payment_id=payment_id,
            source_references=[],
            audit_identifiers=[],
        ),
        explanation=[],
        confidence=_get_attr(match, "confidence", None),
        failure=None,
    )


def read_match_detail_by_id(
    *,
    match_id: str,
    matches: Iterable[Any] | None = None,
) -> ProductMatchDetailResponse:
    """Retrieve product-facing Match Detail by stable backend-owned match_id."""

    if not match_id:
        raise MatchDetailReadError(
            MatchDetailFailureCode.MALFORMED_PAYLOAD,
            "match_id is required.",
        )

    for match in matches or []:
        candidate = _as_string(_get_attr(match, "match_id", None))
        if not candidate:
            candidate = _as_string(_get_attr(match, "id", None))

        if candidate == match_id:
            return build_match_detail_response(match)

    raise MatchDetailReadError(
        MatchDetailFailureCode.MATCH_NOT_FOUND,
        "Match detail was not found for the provided match_id.",
    )
