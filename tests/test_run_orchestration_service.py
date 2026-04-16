from invomatch.services.orchestration.run_orchestration_service import (
    RunOrchestrationService,
)
from invomatch.services.review_store import InMemoryReviewStore


def test_orchestrate_post_matching_completes_run_when_no_review_is_required():
    store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=store)

    outcomes = [
        {"invoice_id": "INV-001", "status": "matched"},
        {"invoice_id": "INV-002", "status": "matched"},
    ]

    result = service.orchestrate_post_matching(
        run_id="run_001",
        reconciliation_outcomes=outcomes,
    )

    assert result.run_status == "completed"
    assert result.review_cases == []
    assert store.snapshot_counts()["review_items"] == 0


def test_orchestrate_post_matching_moves_run_to_review_required_and_persists_cases():
    store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=store)

    outcomes = [
        {"invoice_id": "INV-001", "status": "matched"},
        {"invoice_id": "INV-002", "status": "unmatched", "reason": "no_match"},
    ]

    result = service.orchestrate_post_matching(
        run_id="run_002",
        reconciliation_outcomes=outcomes,
    )

    assert result.run_status == "review_required"
    assert len(result.review_cases) == 1
    assert result.review_cases[0]["invoice_id"] == "INV-002"
    assert result.review_cases[0]["status"] == "PENDING"
    assert result.review_cases[0]["source_status"] == "unmatched"
    assert store.snapshot_counts()["review_items"] == 1


def test_orchestrate_post_matching_keeps_all_generated_review_cases():
    store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=store)

    outcomes = [
        {"invoice_id": "INV-001", "status": "partial_match", "reason": "partial_match_requires_review"},
        {"invoice_id": "INV-002", "status": "duplicate_detected", "reason": "duplicate_candidates_require_review"},
    ]

    result = service.orchestrate_post_matching(
        run_id="run_003",
        reconciliation_outcomes=outcomes,
    )

    assert result.run_status == "review_required"
    assert len(result.review_cases) == 2
    assert result.review_cases[0]["invoice_id"] == "INV-001"
    assert result.review_cases[0]["source_status"] == "partial_match"
    assert result.review_cases[1]["invoice_id"] == "INV-002"
    assert result.review_cases[1]["source_status"] == "duplicate_detected"
    assert store.snapshot_counts()["review_items"] == 2


def test_orchestrate_post_matching_is_deterministic_for_same_input():
    store_1 = InMemoryReviewStore()
    service_1 = RunOrchestrationService(review_store=store_1)

    store_2 = InMemoryReviewStore()
    service_2 = RunOrchestrationService(review_store=store_2)

    outcomes = [
        {"invoice_id": "INV-001", "status": "unmatched", "reason": "no_match"},
    ]

    result_1 = service_1.orchestrate_post_matching(
        run_id="run_004",
        reconciliation_outcomes=outcomes,
    )
    result_2 = service_2.orchestrate_post_matching(
        run_id="run_004",
        reconciliation_outcomes=outcomes,
    )

    assert result_1.run_status == result_2.run_status
    assert result_1.review_cases == result_2.review_cases


def test_orchestrate_post_review_resolution_completes_when_no_blocking_review_items_remain():
    store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=store)

    result = service.orchestrate_post_review_resolution(
        matching_completed=True,
    )

    assert result.run_status == "completed"
    assert result.review_cases == []


def test_orchestrate_post_review_resolution_stays_in_review_required_when_pending_item_exists():
    store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=store)

    service.orchestrate_post_matching(
        run_id="run_005",
        reconciliation_outcomes=[
            {"invoice_id": "INV-001", "status": "unmatched", "reason": "no_match"},
        ],
    )

    result = service.orchestrate_post_review_resolution(
        matching_completed=True,
    )

    assert result.run_status == "review_required"
    assert len(result.review_cases) == 1
    assert result.review_cases[0]["status"] == "PENDING"


def test_orchestrate_post_review_resolution_stays_in_review_required_when_deferred_item_exists():
    store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=store)

    service.orchestrate_post_matching(
        run_id="run_006",
        reconciliation_outcomes=[
            {"invoice_id": "INV-002", "status": "unmatched", "reason": "no_match"},
        ],
    )

    review_item = store.list_review_items()[0]
    review_item.item_status = review_item.item_status.DEFERRED
    store.save_review_item(review_item)

    result = service.orchestrate_post_review_resolution(
        matching_completed=True,
    )

    assert result.run_status == "review_required"
    assert len(result.review_cases) == 1
    assert result.review_cases[0]["status"] == "DEFERRED"


def test_orchestrate_post_review_resolution_fails_when_matching_not_completed():
    store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=store)

    result = service.orchestrate_post_review_resolution(
        matching_completed=False,
    )

    assert result.run_status == "failed"
    assert result.review_cases == []