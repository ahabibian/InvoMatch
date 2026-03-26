from __future__ import annotations

from enum import StrEnum


class CorrectionType(StrEnum):
    ACCEPT_MATCH = "accept_match"
    REJECT_MATCH = "reject_match"
    REPLACE_MATCH_TARGET = "replace_match_target"
    SPLIT_MATCH = "split_match"
    MERGE_MATCH = "merge_match"
    MARK_DUPLICATE_INVOICE = "mark_duplicate_invoice"
    MARK_VALID_UNMATCHED = "mark_valid_unmatched"
    VENDOR_NORMALIZATION_FIX = "vendor_normalization_fix"
    AMOUNT_TOLERANCE_OVERRIDE = "amount_tolerance_override"
    DATE_TOLERANCE_OVERRIDE = "date_tolerance_override"
    INVOICE_NUMBER_OVERRIDE = "invoice_number_override"


class ReviewerAction(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"
    OVERRIDE = "override"
    SPLIT = "split"
    MERGE = "merge"
    MARK_DUPLICATE = "mark_duplicate"
    MARK_UNMATCHED = "mark_unmatched"
    NORMALIZE_VENDOR = "normalize_vendor"
    ADJUST_AMOUNT_TOLERANCE = "adjust_amount_tolerance"
    ADJUST_DATE_TOLERANCE = "adjust_date_tolerance"
    OVERRIDE_INVOICE_NUMBER = "override_invoice_number"


class ReasonCode(StrEnum):
    EXACT_MATCH_CONFIRMED = "exact_match_confirmed"
    WRONG_PAYMENT_TARGET = "wrong_payment_target"
    FALSE_POSITIVE_MATCH = "false_positive_match"
    FALSE_NEGATIVE_MATCH = "false_negative_match"
    DUPLICATE_INVOICE_DETECTED = "duplicate_invoice_detected"
    VALID_UNMATCHED_CASE = "valid_unmatched_case"
    OCR_INVOICE_NUMBER_ERROR = "ocr_invoice_number_error"
    OCR_VENDOR_NAME_ERROR = "ocr_vendor_name_error"
    VENDOR_ALIAS_DISCOVERED = "vendor_alias_discovered"
    AMOUNT_TOLERANCE_TOO_STRICT = "amount_tolerance_too_strict"
    AMOUNT_TOLERANCE_TOO_WIDE = "amount_tolerance_too_wide"
    DATE_WINDOW_TOO_STRICT = "date_window_too_strict"
    DATE_WINDOW_TOO_WIDE = "date_window_too_wide"
    PAYMENT_REFERENCE_MORE_RELIABLE = "payment_reference_more_reliable"
    MANUAL_REVIEW_POLICY = "manual_review_policy"
    OTHER = "other"


class SignalType(StrEnum):
    VENDOR_ALIAS_DISCOVERED = "vendor_alias_discovered"
    INVOICE_NUMBER_OCR_CONFUSION = "invoice_number_ocr_confusion"
    AMOUNT_TOLERANCE_TOO_STRICT = "amount_tolerance_too_strict"
    AMOUNT_TOLERANCE_TOO_WIDE = "amount_tolerance_too_wide"
    DATE_WINDOW_TOO_STRICT = "date_window_too_strict"
    DATE_WINDOW_TOO_WIDE = "date_window_too_wide"
    PAYMENT_REFERENCE_MORE_RELIABLE = "payment_reference_more_reliable"
    DUPLICATE_DETECTION_FALSE_POSITIVE = "duplicate_detection_false_positive"
    DUPLICATE_DETECTION_FALSE_NEGATIVE = "duplicate_detection_false_negative"
    LOW_CONFIDENCE_REGION_REPEATEDLY_CORRECTED = "low_confidence_region_repeatedly_corrected"


class PromotionStatus(StrEnum):
    DRAFT = "draft"
    CANDIDATE = "candidate"
    APPROVED = "approved"
    ACTIVE = "active"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"