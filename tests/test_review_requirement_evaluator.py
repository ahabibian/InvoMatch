from invomatch.services.orchestration.review_requirement_evaluator import (
    ReviewRequirementEvaluator,
)


def test_no_review_required_when_all_outcomes_are_matched():
    evaluator = ReviewRequirementEvaluator()

    results = [
        {"invoice_id": "1", "status": "matched"},
        {"invoice_id": "2", "status": "matched"},
    ]

    outcome = evaluator.evaluate(results)

    assert outcome.requires_review is False
    assert outcome.review_items == []


def test_review_required_when_unmatched_exists():
    evaluator = ReviewRequirementEvaluator()

    results = [
        {"invoice_id": "1", "status": "matched"},
        {"invoice_id": "2", "status": "unmatched"},
    ]

    outcome = evaluator.evaluate(results)

    assert outcome.requires_review is True
    assert len(outcome.review_items) == 1
    assert outcome.review_items[0]["invoice_id"] == "2"


def test_review_required_when_partial_match_exists():
    evaluator = ReviewRequirementEvaluator()

    results = [
        {"invoice_id": "1", "status": "partial_match"},
    ]

    outcome = evaluator.evaluate(results)

    assert outcome.requires_review is True
    assert len(outcome.review_items) == 1
    assert outcome.review_items[0]["status"] == "partial_match"


def test_review_required_when_duplicate_detected_exists():
    evaluator = ReviewRequirementEvaluator()

    results = [
        {"invoice_id": "1", "status": "duplicate_detected"},
    ]

    outcome = evaluator.evaluate(results)

    assert outcome.requires_review is True
    assert len(outcome.review_items) == 1
    assert outcome.review_items[0]["status"] == "duplicate_detected"


def test_unknown_status_does_not_create_review_requirement():
    evaluator = ReviewRequirementEvaluator()

    results = [
        {"invoice_id": "1", "status": "ambiguous"},
    ]

    outcome = evaluator.evaluate(results)

    assert outcome.requires_review is False
    assert outcome.review_items == []