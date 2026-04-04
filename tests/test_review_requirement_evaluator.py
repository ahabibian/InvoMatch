from invomatch.services.orchestration.review_requirement_evaluator import (
    ReviewRequirementEvaluator,
)


def test_no_review_required_when_all_finalizable():
    evaluator = ReviewRequirementEvaluator()

    results = [
        {"invoice_id": "1", "status": "finalizable"},
        {"invoice_id": "2", "status": "finalizable"},
    ]

    outcome = evaluator.evaluate(results)

    assert outcome.requires_review is False
    assert outcome.review_items == []


def test_review_required_when_unmatched_exists():
    evaluator = ReviewRequirementEvaluator()

    results = [
        {"invoice_id": "1", "status": "finalizable"},
        {"invoice_id": "2", "status": "unmatched"},
    ]

    outcome = evaluator.evaluate(results)

    assert outcome.requires_review is True
    assert len(outcome.review_items) == 1


def test_review_required_for_ambiguous():
    evaluator = ReviewRequirementEvaluator()

    results = [
        {"invoice_id": "1", "status": "ambiguous"},
    ]

    outcome = evaluator.evaluate(results)

    assert outcome.requires_review is True


def test_review_required_for_low_confidence():
    evaluator = ReviewRequirementEvaluator()

    results = [
        {"invoice_id": "1", "status": "low_confidence"},
    ]

    outcome = evaluator.evaluate(results)

    assert outcome.requires_review is True