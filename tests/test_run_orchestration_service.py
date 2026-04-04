from invomatch.services.orchestration.run_orchestration_service import (
    RunOrchestrationService,
)


class DummyReviewStore:
    def __init__(self):
        self.created = []

    def create_review_case(self, case):
        self.created.append(case)

    def list_active(self):
        return list(self.created)


def test_orchestrate_post_matching_completes_run_when_no_review_is_required():
    store = DummyReviewStore()
    service = RunOrchestrationService(review_store=store)

    outcomes = [
        {"invoice_id": "INV-001", "status": "finalizable"},
        {"invoice_id": "INV-002", "status": "finalizable"},
    ]

    result = service.orchestrate_post_matching(outcomes)

    assert result.run_status == "completed"
    assert result.review_cases == []
    assert store.created == []


def test_orchestrate_post_matching_moves_run_to_review_required_and_persists_cases():
    store = DummyReviewStore()
    service = RunOrchestrationService(review_store=store)

    outcomes = [
        {"invoice_id": "INV-001", "status": "finalizable"},
        {"invoice_id": "INV-002", "status": "unmatched", "reason": "no_match"},
    ]

    result = service.orchestrate_post_matching(outcomes)

    assert result.run_status == "review_required"
    assert len(result.review_cases) == 1
    assert result.review_cases[0]["invoice_id"] == "INV-002"
    assert len(store.created) == 1
    assert store.created[0]["invoice_id"] == "INV-002"


def test_orchestrate_post_matching_keeps_all_generated_review_cases():
    store = DummyReviewStore()
    service = RunOrchestrationService(review_store=store)

    outcomes = [
        {"invoice_id": "INV-001", "status": "ambiguous", "reason": "multiple_candidates"},
        {"invoice_id": "INV-002", "status": "low_confidence", "reason": "below_threshold"},
    ]

    result = service.orchestrate_post_matching(outcomes)

    assert result.run_status == "review_required"
    assert len(result.review_cases) == 2
    assert len(store.created) == 2


def test_orchestrate_post_matching_is_deterministic_for_same_input():
    store_1 = DummyReviewStore()
    service_1 = RunOrchestrationService(review_store=store_1)

    store_2 = DummyReviewStore()
    service_2 = RunOrchestrationService(review_store=store_2)

    outcomes = [
        {"invoice_id": "INV-001", "status": "unmatched", "reason": "no_match"},
    ]

    result_1 = service_1.orchestrate_post_matching(outcomes)
    result_2 = service_2.orchestrate_post_matching(outcomes)

    assert result_1.run_status == result_2.run_status
    assert result_1.review_cases == result_2.review_cases


def test_orchestrate_post_review_resolution_completes_when_no_blocking_review_items_remain():
    store = DummyReviewStore()
    service = RunOrchestrationService(review_store=store)

    result = service.orchestrate_post_review_resolution(
        matching_completed=True,
    )

    assert result.run_status == "completed"
    assert result.review_cases == []


def test_orchestrate_post_review_resolution_stays_in_review_required_when_pending_item_exists():
    store = DummyReviewStore()
    store.created = [
        {"invoice_id": "INV-001", "status": "pending", "blocking": True},
    ]
    service = RunOrchestrationService(review_store=store)

    result = service.orchestrate_post_review_resolution(
        matching_completed=True,
    )

    assert result.run_status == "review_required"
    assert len(result.review_cases) == 1


def test_orchestrate_post_review_resolution_stays_in_review_required_when_deferred_item_exists():
    store = DummyReviewStore()
    store.created = [
        {"invoice_id": "INV-002", "status": "deferred", "blocking": True},
    ]
    service = RunOrchestrationService(review_store=store)

    result = service.orchestrate_post_review_resolution(
        matching_completed=True,
    )

    assert result.run_status == "review_required"
    assert len(result.review_cases) == 1


def test_orchestrate_post_review_resolution_fails_when_matching_not_completed():
    store = DummyReviewStore()
    service = RunOrchestrationService(review_store=store)

    result = service.orchestrate_post_review_resolution(
        matching_completed=False,
    )

    assert result.run_status == "failed"
    assert result.review_cases == []