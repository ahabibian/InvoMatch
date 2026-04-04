from invomatch.services.orchestration.review_integration_service import (
    ReviewIntegrationService,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore


def test_create_cases_persists_feedback_session_item_and_audit_records():
    review_service = ReviewService()
    review_store = InMemoryReviewStore()
    service = ReviewIntegrationService(
        review_service=review_service,
        review_store=review_store,
    )

    cases = [
        {
            "invoice_id": "INV-1",
            "reason": "no_match",
            "blocking": True,
            "status": "pending",
        },
        {
            "invoice_id": "INV-2",
            "reason": "multiple_candidates",
            "blocking": True,
            "status": "pending",
        },
    ]

    service.create_cases(
        run_id="run_123",
        review_cases=cases,
        created_by="run_orchestration",
    )

    counts = review_store.snapshot_counts()

    assert counts["feedback_records"] == 2
    assert counts["review_sessions"] == 1
    assert counts["review_items"] == 2
    assert counts["audit_events"] == 2


def test_get_active_cases_returns_pending_review_items_mapped_to_case_shape():
    review_service = ReviewService()
    review_store = InMemoryReviewStore()
    service = ReviewIntegrationService(
        review_service=review_service,
        review_store=review_store,
    )

    service.create_cases(
        run_id="run_456",
        review_cases=[
            {
                "invoice_id": "INV-9",
                "reason": "below_threshold",
                "blocking": True,
                "status": "pending",
                "confidence": 0.61,
            }
        ],
        created_by="run_orchestration",
    )

    result = service.get_active_cases()

    assert len(result) == 1
    assert result[0]["invoice_id"] == "INV-9"
    assert result[0]["status"] == "PENDING"
    assert result[0]["blocking"] is True
    assert result[0]["reason"] == "below_threshold"


def test_get_active_cases_excludes_terminal_review_items():
    review_service = ReviewService()
    review_store = InMemoryReviewStore()
    service = ReviewIntegrationService(
        review_service=review_service,
        review_store=review_store,
    )

    service.create_cases(
        run_id="run_789",
        review_cases=[
            {
                "invoice_id": "INV-3",
                "reason": "no_match",
                "blocking": True,
                "status": "pending",
            }
        ],
        created_by="run_orchestration",
    )

    review_item = review_store.list_review_items()[0]
    review_item.close()
    review_store.save_review_item(review_item)

    result = service.get_active_cases()

    assert result == []


def test_create_cases_is_idempotent_for_same_run_and_invoice_scope():
    review_service = ReviewService()
    review_store = InMemoryReviewStore()
    service = ReviewIntegrationService(
        review_service=review_service,
        review_store=review_store,
    )

    cases = [
        {
            "invoice_id": "INV-10",
            "reason": "no_match",
            "blocking": True,
            "status": "pending",
        }
    ]

    service.create_cases(
        run_id="run_same",
        review_cases=cases,
        created_by="run_orchestration",
    )
    service.create_cases(
        run_id="run_same",
        review_cases=cases,
        created_by="run_orchestration",
    )

    counts = review_store.snapshot_counts()

    assert counts["feedback_records"] == 1
    assert counts["review_items"] == 1
    assert len(service.get_active_cases()) == 1


def test_create_cases_allows_distinct_invoice_scopes_in_same_run():
    review_service = ReviewService()
    review_store = InMemoryReviewStore()
    service = ReviewIntegrationService(
        review_service=review_service,
        review_store=review_store,
    )

    service.create_cases(
        run_id="run_multi",
        review_cases=[
            {
                "invoice_id": "INV-11",
                "reason": "no_match",
                "blocking": True,
                "status": "pending",
            },
            {
                "invoice_id": "INV-12",
                "reason": "below_threshold",
                "blocking": True,
                "status": "pending",
            },
        ],
        created_by="run_orchestration",
    )

    counts = review_store.snapshot_counts()

    assert counts["feedback_records"] == 2
    assert counts["review_items"] == 2
    assert len(service.get_active_cases()) == 2