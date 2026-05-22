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

def test_match_detail_route_binds_review_store_match_id_to_detail_response():
class FakeReviewItem:
review_item_id = "review-item-1"
feedback_id = "feedback-1"
item_status = "PENDING"
current_decision = None

class FakeFeedback:
    run_id = "run-1"
    source_reference = "review-feedback-source"
    raw_payload = {
        "match_id": "match-bound-1",
        "reason_code": "amount_date_candidate",
        "invoice_id": "inv-bound-1",
        "payment_id": "pay-bound-1",
        "confidence": 0.88,
    }

class FakeReviewStore:
    def list_review_items(self):
        return [FakeReviewItem()]

    def get_feedback(self, feedback_id):
        assert feedback_id == "feedback-1"
        return FakeFeedback()

app = FastAPI()
app.state.review_store = FakeReviewStore()
app.include_router(review_cases.router)

response = TestClient(app).get("/api/review/matches/match-bound-1/detail")

assert response.status_code == 200
payload = response.json()
assert payload["match_id"] == "match-bound-1"
assert payload["invoice_summary"]["invoice_id"] == "inv-bound-1"
assert payload["payment_summary"]["payment_id"] == "pay-bound-1"
assert payload["traceability"]["invoice_id"] == "inv-bound-1"
assert payload["traceability"]["payment_id"] == "pay-bound-1"
assert payload["evidence"][0]["source"] == "backend_match_record"
assert payload["failure"] is None

