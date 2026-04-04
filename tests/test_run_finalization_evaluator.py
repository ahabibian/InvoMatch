from invomatch.services.orchestration.run_finalization_evaluator import (
    RunFinalizationEvaluator,
)


def test_run_is_finalizable_when_no_active_review_items_exist():
    evaluator = RunFinalizationEvaluator()

    outcome = evaluator.evaluate(
        review_items=[],
        matching_completed=True,
    )

    assert outcome.is_finalizable is True


def test_run_is_not_finalizable_when_active_review_item_exists():
    evaluator = RunFinalizationEvaluator()

    outcome = evaluator.evaluate(
        review_items=[
            {"invoice_id": "1", "status": "pending"},
        ],
        matching_completed=True,
    )

    assert outcome.is_finalizable is False


def test_run_is_not_finalizable_when_matching_not_completed():
    evaluator = RunFinalizationEvaluator()

    outcome = evaluator.evaluate(
        review_items=[],
        matching_completed=False,
    )

    assert outcome.is_finalizable is False


def test_run_is_not_finalizable_when_review_item_is_deferred():
    evaluator = RunFinalizationEvaluator()

    outcome = evaluator.evaluate(
        review_items=[
            {"invoice_id": "1", "status": "deferred"},
        ],
        matching_completed=True,
    )

    assert outcome.is_finalizable is False


def test_run_is_not_finalizable_when_review_item_is_reopened():
    evaluator = RunFinalizationEvaluator()

    outcome = evaluator.evaluate(
        review_items=[
            {"invoice_id": "1", "status": "reopened"},
        ],
        matching_completed=True,
    )

    assert outcome.is_finalizable is False


def test_run_is_not_finalizable_when_review_item_status_is_pending_uppercase():
    evaluator = RunFinalizationEvaluator()

    outcome = evaluator.evaluate(
        review_items=[
            {"invoice_id": "1", "status": "PENDING"},
        ],
        matching_completed=True,
    )

    assert outcome.is_finalizable is False


def test_run_is_not_finalizable_when_review_item_status_is_in_review_uppercase():
    evaluator = RunFinalizationEvaluator()

    outcome = evaluator.evaluate(
        review_items=[
            {"invoice_id": "1", "status": "IN_REVIEW"},
        ],
        matching_completed=True,
    )

    assert outcome.is_finalizable is False


def test_run_is_not_finalizable_when_review_item_status_is_deferred_uppercase():
    evaluator = RunFinalizationEvaluator()

    outcome = evaluator.evaluate(
        review_items=[
            {"invoice_id": "1", "status": "DEFERRED"},
        ],
        matching_completed=True,
    )

    assert outcome.is_finalizable is False