from inspect import isabstract

from invomatch.domain.feedback.repositories import FeedbackRepository


def test_feedback_repository_is_abstract() -> None:
    assert isabstract(FeedbackRepository)


def test_feedback_repository_exposes_required_methods() -> None:
    required_methods = {
        "save_correction_event",
        "get_correction_event",
        "list_correction_events_by_tenant",
        "list_correction_events_by_run",
        "list_correction_events_by_match",
        "save_learning_signal",
        "get_learning_signal",
        "list_learning_signals_by_tenant",
        "save_candidate_rule_recommendation",
        "get_candidate_rule_recommendation",
        "list_candidate_rule_recommendations_by_status",
        "record_rule_promotion",
        "record_rule_rollback",
    }

    repository_methods = {
        name
        for name in dir(FeedbackRepository)
        if not name.startswith("_")
    }

    assert required_methods.issubset(repository_methods)