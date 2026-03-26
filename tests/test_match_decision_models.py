from invomatch.domain.matching.models import (
    ConfidenceLevel,
    DecisionProvenance,
    DecisionStatus,
    DecisionType,
    MatchDecision,
    MatchExplanation,
)


def build_explanation() -> MatchExplanation:
    return MatchExplanation(
        summary="Exact amount and normalized invoice number match.",
        reasons=("exact_amount_match", "invoice_number_normalized_match"),
        penalties=(),
        key_facts={"amount_delta": 0.0, "date_delta_days": 2},
        competing_candidate_count=1,
        top_score_gap=18.0,
    )


def build_provenance() -> DecisionProvenance:
    return DecisionProvenance(
        match_engine_version="1.0.0",
        rule_set_version="1.0.0",
        confidence_policy_version="1.0.0",
        taxonomy_version="1.0.0",
        feature_schema_version="1.0.0",
    )


def test_one_to_one_match_decision_is_valid() -> None:
    decision = MatchDecision(
        decision_id="dec_001",
        run_id="run_001",
        invoice_ids=("inv_001",),
        payment_ids=("pay_001",),
        decision_type=DecisionType.ONE_TO_ONE,
        status=DecisionStatus.PROPOSED,
        score=94.0,
        confidence=ConfidenceLevel.HIGH,
        explanation=build_explanation(),
        auto_action_eligible=True,
        provenance=build_provenance(),
    )

    assert decision.decision_type == DecisionType.ONE_TO_ONE
    assert decision.auto_action_eligible is True


def test_review_required_cannot_be_high_confidence() -> None:
    try:
        MatchDecision(
            decision_id="dec_002",
            run_id="run_001",
            invoice_ids=("inv_002",),
            payment_ids=("pay_002",),
            decision_type=DecisionType.REVIEW_REQUIRED,
            status=DecisionStatus.PROPOSED,
            score=72.0,
            confidence=ConfidenceLevel.HIGH,
            explanation=build_explanation(),
            provenance=build_provenance(),
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "cannot use confidence=high" in str(exc)


def test_one_to_many_requires_multiple_payments() -> None:
    try:
        MatchDecision(
            decision_id="dec_003",
            run_id="run_001",
            invoice_ids=("inv_003",),
            payment_ids=("pay_003",),
            decision_type=DecisionType.ONE_TO_MANY,
            status=DecisionStatus.PROPOSED,
            score=81.0,
            confidence=ConfidenceLevel.MEDIUM,
            explanation=build_explanation(),
            provenance=build_provenance(),
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "ONE_TO_MANY requires 1 invoice_id and at least 2 payment_ids." in str(exc)


def test_unmatched_can_carry_mismatch_code() -> None:
    decision = MatchDecision(
        decision_id="dec_004",
        run_id="run_001",
        invoice_ids=("inv_004",),
        payment_ids=(),
        decision_type=DecisionType.UNMATCHED,
        status=DecisionStatus.PROPOSED,
        score=21.0,
        confidence=ConfidenceLevel.LOW,
        explanation=MatchExplanation(
            summary="No plausible payment candidate within the allowed amount and date window.",
            reasons=(),
            penalties=("no_candidate_found",),
            key_facts={"candidate_count": 0},
        ),
        primary_mismatch_code="NO_CANDIDATE_AMOUNT",
        secondary_mismatch_codes=("NO_CANDIDATE_DATE",),
        provenance=build_provenance(),
    )

    assert decision.primary_mismatch_code == "NO_CANDIDATE_AMOUNT"


def test_auto_action_requires_high_confidence() -> None:
    try:
        MatchDecision(
            decision_id="dec_005",
            run_id="run_001",
            invoice_ids=("inv_005",),
            payment_ids=("pay_005",),
            decision_type=DecisionType.ONE_TO_ONE,
            status=DecisionStatus.PROPOSED,
            score=75.0,
            confidence=ConfidenceLevel.MEDIUM,
            explanation=build_explanation(),
            auto_action_eligible=True,
            provenance=build_provenance(),
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "auto_action_eligible requires confidence=high." in str(exc)