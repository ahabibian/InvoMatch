from __future__ import annotations

from typing import Literal

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


class IngestionInvoiceInput(BaseModel):
    id: str = Field(min_length=1)
    date: str = Field(min_length=1)
    amount: str = Field(min_length=1)
    currency: str = Field(min_length=1)
    reference: str | None = None

    @field_validator("id", "date", "amount", "currency")
    @classmethod
    def _strip_required_fields(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field must not be empty")
        return normalized

    @field_validator("reference")
    @classmethod
    def _normalize_reference(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class IngestionPaymentInput(BaseModel):
    id: str = Field(min_length=1)
    date: str = Field(min_length=1)
    amount: str = Field(min_length=1)
    currency: str = Field(min_length=1)
    reference: str | None = None

    @field_validator("id", "date", "amount", "currency")
    @classmethod
    def _strip_required_fields(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Field must not be empty")
        return normalized

    @field_validator("reference")
    @classmethod
    def _normalize_reference(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class CreateRunFromIngestionRequest(BaseModel):
    ingestion_batch_id: str = Field(min_length=1)
    invoices: list[IngestionInvoiceInput] = Field(default_factory=list)
    payments: list[IngestionPaymentInput] = Field(default_factory=list)

    @field_validator("ingestion_batch_id")
    @classmethod
    def _strip_batch_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("ingestion_batch_id must not be empty")
        return normalized


class IngestionRunResponse(BaseModel):
    status: Literal["run_created", "run_reused", "run_rejected", "run_failed"]
    run_id: str | None = None
    reason_code: str
    ingestion_batch_id: str
    accepted_invoice_count: int
    accepted_payment_count: int
    rejected_count: int
    conflict_count: int
    partial_ingestion: bool


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