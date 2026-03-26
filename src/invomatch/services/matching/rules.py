from __future__ import annotations

from invomatch.domain.matching.features import MatchFeatures
from invomatch.domain.matching.rules import RuleEffect, RuleResult, ScoreResult


class RuleEngine:
    def evaluate(self, features: MatchFeatures) -> ScoreResult:
        rule_results: list[RuleResult] = []

        if not features.currency_match:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_CURRENCY_MISMATCH",
                    effect=RuleEffect.HARD_BLOCK,
                    score_delta=0.0,
                    reason_code="currency_mismatch",
                    triggered=True,
                )
            )

        if features.duplicate_risk_flag:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_DUPLICATE_RISK",
                    effect=RuleEffect.NEGATIVE,
                    score_delta=25.0,
                    reason_code="duplicate_risk_flag",
                    triggered=True,
                )
            )

        if features.invoice_ocr_low_confidence_flag:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_OCR_LOW_CONFIDENCE",
                    effect=RuleEffect.NEGATIVE,
                    score_delta=10.0,
                    reason_code="ocr_low_confidence",
                    triggered=True,
                )
            )

        if features.amount_exact_match:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_AMOUNT_EXACT",
                    effect=RuleEffect.POSITIVE,
                    score_delta=40.0,
                    reason_code="exact_amount_match",
                    triggered=True,
                )
            )
        elif features.amount_delta_percentage <= 0.01:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_AMOUNT_NEAR",
                    effect=RuleEffect.POSITIVE,
                    score_delta=25.0,
                    reason_code="near_amount_match",
                    triggered=True,
                )
            )
        elif features.amount_delta_percentage <= 0.05:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_AMOUNT_TOLERABLE",
                    effect=RuleEffect.POSITIVE,
                    score_delta=10.0,
                    reason_code="tolerable_amount_match",
                    triggered=True,
                )
            )
        else:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_AMOUNT_DRIFT",
                    effect=RuleEffect.NEGATIVE,
                    score_delta=20.0,
                    reason_code="high_amount_drift",
                    triggered=True,
                )
            )

        if features.invoice_number_normalized_match:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_INVNUM_NORMALIZED_MATCH",
                    effect=RuleEffect.POSITIVE,
                    score_delta=35.0,
                    reason_code="invoice_number_normalized_match",
                    triggered=True,
                )
            )
        elif features.invoice_number_in_payment_reference:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_INVNUM_REFERENCE_CONTAINS",
                    effect=RuleEffect.POSITIVE,
                    score_delta=25.0,
                    reason_code="invoice_number_found_in_reference",
                    triggered=True,
                )
            )

        if features.supplier_name_exact_match:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_SUPPLIER_EXACT",
                    effect=RuleEffect.POSITIVE,
                    score_delta=15.0,
                    reason_code="supplier_name_exact_match",
                    triggered=True,
                )
            )
        elif features.supplier_name_normalized_match:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_SUPPLIER_NORMALIZED",
                    effect=RuleEffect.POSITIVE,
                    score_delta=10.0,
                    reason_code="supplier_name_normalized_match",
                    triggered=True,
                )
            )

        if features.date_delta_days <= 3:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_DATE_CLOSE",
                    effect=RuleEffect.POSITIVE,
                    score_delta=10.0,
                    reason_code="payment_date_close_to_invoice_date",
                    triggered=True,
                )
            )
        elif features.date_delta_days <= 10:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_DATE_ACCEPTABLE",
                    effect=RuleEffect.POSITIVE,
                    score_delta=5.0,
                    reason_code="payment_date_within_acceptable_window",
                    triggered=True,
                )
            )
        else:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_DATE_DRIFT",
                    effect=RuleEffect.NEGATIVE,
                    score_delta=10.0,
                    reason_code="payment_date_far_from_invoice_date",
                    triggered=True,
                )
            )

        if features.payment_before_invoice:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_PAYMENT_BEFORE_INVOICE",
                    effect=RuleEffect.NEGATIVE,
                    score_delta=10.0,
                    reason_code="payment_before_invoice_date",
                    triggered=True,
                )
            )

        if features.payment_after_due_date is True:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_PAYMENT_AFTER_DUE",
                    effect=RuleEffect.NEGATIVE,
                    score_delta=5.0,
                    reason_code="payment_after_due_date",
                    triggered=True,
                )
            )

        if features.reference_token_overlap_score >= 0.6:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_REFERENCE_STRONG",
                    effect=RuleEffect.POSITIVE,
                    score_delta=12.0,
                    reason_code="strong_reference_token_overlap",
                    triggered=True,
                )
            )
        elif features.reference_token_overlap_score > 0.0:
            rule_results.append(
                RuleResult(
                    rule_id="RULE_REFERENCE_WEAK",
                    effect=RuleEffect.POSITIVE,
                    score_delta=5.0,
                    reason_code="weak_reference_token_overlap",
                    triggered=True,
                )
            )

        hard_block_codes = tuple(
            result.reason_code
            for result in rule_results
            if result.effect == RuleEffect.HARD_BLOCK and result.triggered
        )
        reason_codes = tuple(
            result.reason_code
            for result in rule_results
            if result.effect == RuleEffect.POSITIVE and result.triggered
        )
        penalty_codes = tuple(
            result.reason_code
            for result in rule_results
            if result.effect == RuleEffect.NEGATIVE and result.triggered
        )

        positive_total = sum(
            result.score_delta
            for result in rule_results
            if result.effect == RuleEffect.POSITIVE and result.triggered
        )
        negative_total = sum(
            result.score_delta
            for result in rule_results
            if result.effect == RuleEffect.NEGATIVE and result.triggered
        )

        raw_score = max(0.0, positive_total - negative_total)
        normalized_score = min(100.0, raw_score)

        if hard_block_codes:
            raw_score = 0.0
            normalized_score = 0.0

        return ScoreResult(
            raw_score=raw_score,
            normalized_score=normalized_score,
            rule_results=tuple(rule_results),
            reason_codes=reason_codes,
            penalty_codes=penalty_codes,
            hard_block_codes=hard_block_codes,
            is_hard_blocked=bool(hard_block_codes),
            extracted_facts={
                "invoice_id": features.invoice_id,
                "payment_id": features.payment_id,
                "amount_delta_absolute": features.amount_delta_absolute,
                "amount_delta_percentage": features.amount_delta_percentage,
                "date_delta_days": features.date_delta_days,
                "reference_token_overlap_score": features.reference_token_overlap_score,
            },
        )