from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from invomatch.services.reconciliation_errors import ReconciliationServiceError


class CreateRunRequest(BaseModel):
    invoice_csv_path: str = Field(min_length=1)
    payment_csv_path: str = Field(min_length=1)

    @field_validator("invoice_csv_path", "payment_csv_path")
    @classmethod
    def _strip_and_validate_non_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Path must not be empty")
        return normalized


class ApiErrorResponse(BaseModel):
    error_code: str
    message: str
    run_id: str | None = None


def to_api_error_response(error: ReconciliationServiceError) -> ApiErrorResponse:
    return ApiErrorResponse(
        error_code=error.error_code,
        message=error.message,
        run_id=error.run_id,
    )