from invomatch.services.orchestration.review_case_factory import ReviewCaseFactory


def test_build_maps_unmatched_to_no_match_reason():
    factory = ReviewCaseFactory()

    review_case = factory.build(
        {
            "invoice_id": "INV-001",
            "status": "unmatched",
        }
    )

    assert review_case["invoice_id"] == "INV-001"
    assert review_case["status"] == "pending"
    assert review_case["reason"] == "no_match"
    assert review_case["blocking"] is True
    assert review_case["source_status"] == "unmatched"


def test_build_maps_partial_match_to_specific_reason():
    factory = ReviewCaseFactory()

    review_case = factory.build(
        {
            "invoice_id": "INV-002",
            "status": "partial_match",
        }
    )

    assert review_case["reason"] == "partial_match_requires_review"
    assert review_case["source_status"] == "partial_match"


def test_build_maps_duplicate_detected_to_specific_reason():
    factory = ReviewCaseFactory()

    review_case = factory.build(
        {
            "invoice_id": "INV-003",
            "status": "duplicate_detected",
        }
    )

    assert review_case["reason"] == "duplicate_candidates_require_review"
    assert review_case["source_status"] == "duplicate_detected"


def test_build_preserves_explicit_reason_when_provided():
    factory = ReviewCaseFactory()

    review_case = factory.build(
        {
            "invoice_id": "INV-004",
            "status": "unmatched",
            "reason": "explicit_reason",
        }
    )

    assert review_case["reason"] == "explicit_reason"