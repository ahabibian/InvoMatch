from invomatch.services.orchestration.review_case_generation_service import (
    ReviewCaseGenerationService,
)


def test_generate_returns_empty_when_no_review_required_outcomes_exist():
    service = ReviewCaseGenerationService()

    outcomes = [
        {"invoice_id": "INV-001", "status": "finalizable"},
        {"invoice_id": "INV-002", "status": "finalizable"},
    ]

    review_cases = service.generate(outcomes)

    assert review_cases == []


def test_generate_creates_review_cases_for_review_required_outcomes():
    service = ReviewCaseGenerationService()

    outcomes = [
        {"invoice_id": "INV-001", "status": "unmatched", "reason": "no_match"},
        {"invoice_id": "INV-002", "status": "ambiguous", "reason": "multiple_candidates"},
    ]

    review_cases = service.generate(outcomes)

    assert len(review_cases) == 2
    assert review_cases[0]["invoice_id"] == "INV-001"
    assert review_cases[1]["invoice_id"] == "INV-002"


def test_generate_skips_finalizable_outcomes():
    service = ReviewCaseGenerationService()

    outcomes = [
        {"invoice_id": "INV-001", "status": "finalizable"},
        {"invoice_id": "INV-002", "status": "low_confidence", "reason": "below_threshold"},
    ]

    review_cases = service.generate(outcomes)

    assert len(review_cases) == 1
    assert review_cases[0]["invoice_id"] == "INV-002"


def test_generate_is_idempotent_by_invoice_id():
    service = ReviewCaseGenerationService()

    outcomes = [
        {"invoice_id": "INV-001", "status": "unmatched", "reason": "no_match"},
        {"invoice_id": "INV-001", "status": "unmatched", "reason": "no_match"},
    ]

    review_cases = service.generate(outcomes)

    assert len(review_cases) == 1
    assert review_cases[0]["invoice_id"] == "INV-001"


def test_generate_preserves_first_active_case_for_same_invoice_scope():
    service = ReviewCaseGenerationService()

    outcomes = [
        {"invoice_id": "INV-001", "status": "unmatched", "reason": "first_reason"},
        {"invoice_id": "INV-001", "status": "ambiguous", "reason": "second_reason"},
    ]

    review_cases = service.generate(outcomes)

    assert len(review_cases) == 1
    assert review_cases[0]["reason"] == "first_reason"