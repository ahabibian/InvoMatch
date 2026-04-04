from invomatch.services.orchestration.review_integration_service import (
    ReviewIntegrationService,
)


class DummyReviewStore:
    def __init__(self):
        self.created = []

    def create_review_case(self, case):
        self.created.append(case)

    def list_active(self):
        return self.created


def test_create_review_cases_persists_cases():
    store = DummyReviewStore()
    service = ReviewIntegrationService(review_store=store)

    cases = [
        {"invoice_id": "INV-1"},
        {"invoice_id": "INV-2"},
    ]

    service.create_cases(cases)

    assert len(store.created) == 2


def test_get_active_review_cases_returns_store_data():
    store = DummyReviewStore()
    store.created = [{"invoice_id": "INV-1"}]

    service = ReviewIntegrationService(review_store=store)

    result = service.get_active_cases()

    assert len(result) == 1
    assert result[0]["invoice_id"] == "INV-1"