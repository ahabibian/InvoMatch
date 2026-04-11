from __future__ import annotations

from datetime import datetime, timezone

from invomatch.api.product_models.input_boundary import (
    ProductInputError,
    ProductInputSessionView,
    ProductInputSubmissionResponse,
)


def test_product_input_submission_response_shape() -> None:
    model = ProductInputSubmissionResponse(
        input_id="input-123",
        status="run_created",
        ingestion_batch_id="batch-123",
        run_id="run-123",
        errors=[],
    )

    dumped = model.model_dump()

    assert dumped == {
        "input_id": "input-123",
        "status": "run_created",
        "ingestion_batch_id": "batch-123",
        "run_id": "run-123",
        "errors": [],
    }


def test_product_input_session_view_shape() -> None:
    now = datetime.now(timezone.utc)

    model = ProductInputSessionView(
        input_id="input-123",
        input_type="json",
        status="rejected",
        source_filename=None,
        source_size_bytes=None,
        ingestion_batch_id=None,
        run_id=None,
        errors=[
            ProductInputError(
                type="validation_error",
                code="string_too_short",
                message="String should have at least 1 character",
                field="invoices.0.amount",
            )
        ],
        created_at=now,
        updated_at=now,
    )

    dumped = model.model_dump()

    assert dumped["input_id"] == "input-123"
    assert dumped["input_type"] == "json"
    assert dumped["status"] == "rejected"
    assert dumped["ingestion_batch_id"] is None
    assert dumped["run_id"] is None
    assert dumped["errors"][0]["type"] == "validation_error"
    assert dumped["errors"][0]["field"] == "invoices.0.amount"


def test_product_input_error_shape() -> None:
    model = ProductInputError(
        type="validation_error",
        code="invalid_value",
        message="Invalid input",
        field="invoices.0.amount",
    )

    dumped = model.model_dump()

    assert dumped == {
        "type": "validation_error",
        "code": "invalid_value",
        "message": "Invalid input",
        "field": "invoices.0.amount",
    }