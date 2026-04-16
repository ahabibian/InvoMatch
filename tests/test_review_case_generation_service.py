from invomatch.services.orchestration.review_case_generation_service import (
    ReviewCaseGenerationService,
)


def test_generate_returns_empty_when_no_review_required_outcomes_exist():
    service = ReviewCaseGenerationService()

    outcomes = [
        {"invoice_id": "INV-001", "status": "matched"},
        {"invoice_id": "INV-002", "status": "matched"},
    ]

    review_cases = service.generate(outcomes)

    assert review_cases == []


def test_generate_creates_review_cases_for_runtime_review_required_outcomes():
    service = ReviewCaseGenerationService()

    outcomes = [
        {"invoice_id": "INV-001", "status": "unmatched"},
        {"invoice_id": "INV-002", "status": "partial_match"},
        {"invoice_id": "INV-003", "status": "duplicate_detected"},
    ]

    review_cases = service.generate(outcomes)

    assert len(review_cases) == 3
    assert review_cases[0]["invoice_id"] == "INV-001"
    assert review_cases[0]["source_status"] == "unmatched"
    assert review_cases[1]["invoice_id"] == "INV-002"
    assert review_cases[1]["source_status"] == "partial_match"
    assert review_cases[2]["invoice_id"] == "INV-003"
    assert review_cases[2]["source_status"] == "duplicate_detected"


def test_generate_skips_non_review_runtime_outcomes():
    service = ReviewCaseGenerationService()

    outcomes = [
        {"invoice_id": "INV-001", "status": "matched"},
        {"invoice_id": "INV-002", "status": "partial_match"},
    ]

    review_cases = service.generate(outcomes)

    assert len(review_cases) == 1
    assert review_cases[0]["invoice_id"] == "INV-002"


def test_generate_is_idempotent_by_invoice_id():
    service = ReviewCaseGenerationService()

    outcomes = [
        {"invoice_id": "INV-001", "status": "unmatched"},
        {"invoice_id": "INV-001", "status": "duplicate_detected"},
    ]

    review_cases = service.generate(outcomes)

    assert len(review_cases) == 1
    assert review_cases[0]["invoice_id"] == "INV-001"
    assert review_cases[0]["source_status"] == "unmatched"


def test_generate_ignores_unknown_statuses():
    service = ReviewCaseGenerationService()

    outcomes = [
        {"invoice_id": "INV-001", "status": "ambiguous"},
        {"invoice_id": "INV-002", "status": "matched"},
    ]

    review_cases = service.generate(outcomes)

    assert review_cases == []