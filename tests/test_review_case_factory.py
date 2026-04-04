from invomatch.services.orchestration.review_case_factory import ReviewCaseFactory


def test_build_creates_blocking_review_case_from_unmatched_outcome():
    factory = ReviewCaseFactory()

    outcome = {
        "invoice_id": "INV-001",
        "status": "unmatched",
        "reason": "no_acceptable_match",
    }

    review_case = factory.build(outcome)

    assert review_case["invoice_id"] == "INV-001"
    assert review_case["reason"] == "no_acceptable_match"
    assert review_case["blocking"] is True
    assert review_case["status"] == "pending"


def test_build_preserves_candidate_context_when_present():
    factory = ReviewCaseFactory()

    outcome = {
        "invoice_id": "INV-002",
        "status": "ambiguous",
        "reason": "multiple_candidates",
        "candidates": [
            {"payment_id": "PAY-1"},
            {"payment_id": "PAY-2"},
        ],
    }

    review_case = factory.build(outcome)

    assert review_case["invoice_id"] == "INV-002"
    assert review_case["reason"] == "multiple_candidates"
    assert len(review_case["candidates"]) == 2
    assert review_case["blocking"] is True


def test_build_includes_confidence_when_present():
    factory = ReviewCaseFactory()

    outcome = {
        "invoice_id": "INV-003",
        "status": "low_confidence",
        "reason": "confidence_below_threshold",
        "confidence": 0.61,
    }

    review_case = factory.build(outcome)

    assert review_case["invoice_id"] == "INV-003"
    assert review_case["confidence"] == 0.61
    assert review_case["status"] == "pending"


def test_build_defaults_reason_when_missing():
    factory = ReviewCaseFactory()

    outcome = {
        "invoice_id": "INV-004",
        "status": "forced_review",
    }

    review_case = factory.build(outcome)

    assert review_case["invoice_id"] == "INV-004"
    assert review_case["reason"] == "manual_review_required"