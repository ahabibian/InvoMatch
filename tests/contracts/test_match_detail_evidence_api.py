from fastapi import FastAPI
from fastapi.testclient import TestClient

from invomatch.api import review_cases
from invomatch.api.product_models.review_case import (
    ProductMatchDetailEvidenceItem,
    ProductMatchDetailResponse,
    ProductMatchDetailTraceability,
)
from invomatch.services.match_detail_read_service import (
    MatchDetailFailureCode,
    MatchDetailReadError,
)


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(review_cases.router)
    return TestClient(app)


def test_match_detail_retrieval_by_match_id_exposes_backend_owned_payload(monkeypatch):
    def fake_read_match_detail_by_id(*, match_id, matches=None):
        assert match_id == "match-123"
        return ProductMatchDetailResponse(
            match_id="match-123",
            match_status="review_required",
            invoice_summary={"invoice_id": "inv-1", "invoice_amount": 1000},
            payment_summary={"payment_id": "pay-1", "payment_amount": 1000},
            evidence=[
                ProductMatchDetailEvidenceItem(
                    evidence_id="ev-1",
                    evidence_type="amount_match",
                    label="Amount match",
                    value="1000",
                    source="backend_match_record",
                )
            ],
            traceability=ProductMatchDetailTraceability(
                invoice_id="inv-1",
                payment_id="pay-1",
                source_references=["source-a"],
                audit_identifiers=["audit-a"],
            ),
            explanation=[],
            confidence=0.97,
        )

    monkeypatch.setattr(
        review_cases,
        "read_match_detail_by_id",
        fake_read_match_detail_by_id,
    )

    response = _client().get("/api/review/matches/match-123/detail")

    assert response.status_code == 200
    payload = response.json()
    assert payload["match_id"] == "match-123"
    assert payload["match_status"] == "review_required"
    assert payload["evidence"][0]["evidence_id"] == "ev-1"
    assert payload["traceability"]["invoice_id"] == "inv-1"
    assert payload["traceability"]["payment_id"] == "pay-1"
    assert payload["failure"] is None


def test_match_detail_not_found_uses_backend_owned_failure_semantics(monkeypatch):
    def fake_read_match_detail_by_id(*, match_id, matches=None):
        raise MatchDetailReadError(
            MatchDetailFailureCode.MATCH_NOT_FOUND,
            "Match detail was not found for the provided match_id.",
        )

    monkeypatch.setattr(
        review_cases,
        "read_match_detail_by_id",
        fake_read_match_detail_by_id,
    )

    response = _client().get("/api/review/matches/missing-match/detail")

    assert response.status_code == 404
    payload = response.json()
    assert payload["detail"]["code"] == "match_not_found"
    assert "not found" in payload["detail"]["message"].lower()


def test_match_detail_malformed_payload_is_distinguishable(monkeypatch):
    def fake_read_match_detail_by_id(*, match_id, matches=None):
        raise MatchDetailReadError(
            MatchDetailFailureCode.MALFORMED_PAYLOAD,
            "Match detail payload is missing match_id.",
        )

    monkeypatch.setattr(
        review_cases,
        "read_match_detail_by_id",
        fake_read_match_detail_by_id,
    )

    response = _client().get("/api/review/matches/malformed/detail")

    assert response.status_code == 422
    payload = response.json()
    assert payload["detail"]["code"] == "malformed_or_incomplete_payload"
