from invomatch.domain.feedback.enums import (
    CorrectionType,
    PromotionStatus,
    ReasonCode,
    ReviewerAction,
    SignalType,
)


def test_correction_type_values_are_stable() -> None:
    assert CorrectionType.ACCEPT_MATCH == "accept_match"
    assert CorrectionType.REPLACE_MATCH_TARGET == "replace_match_target"


def test_reviewer_action_values_are_stable() -> None:
    assert ReviewerAction.ACCEPT == "accept"
    assert ReviewerAction.OVERRIDE == "override"


def test_reason_code_values_are_stable() -> None:
    assert ReasonCode.FALSE_POSITIVE_MATCH == "false_positive_match"
    assert ReasonCode.VENDOR_ALIAS_DISCOVERED == "vendor_alias_discovered"


def test_signal_type_values_are_stable() -> None:
    assert SignalType.DATE_WINDOW_TOO_WIDE == "date_window_too_wide"


def test_promotion_status_values_are_stable() -> None:
    assert PromotionStatus.ACTIVE == "active"
    assert PromotionStatus.ROLLED_BACK == "rolled_back"