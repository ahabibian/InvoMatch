from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from invomatch.api.reconciliation_schemas import CreateRunFromIngestionRequest
from invomatch.domain.input_boundary.models import InputError, InputErrorType


class JsonInputService:
    def validate(self, payload: dict[str, Any]) -> list[InputError]:
        try:
            CreateRunFromIngestionRequest(
                ingestion_batch_id="epic20-validation",
                invoices=payload.get("invoices", []),
                payments=payload.get("payments", []),
            )
            return []
        except ValidationError as exc:
            errors: list[InputError] = []
            for item in exc.errors():
                location = item.get("loc", ())
                field_name = ".".join(str(part) for part in location if part != "ingestion_batch_id") or None
                errors.append(InputError(
                    type=InputErrorType.VALIDATION,
                    code=item.get("type", "validation_error"),
                    message=item.get("msg", "Invalid input"),
                    field=field_name,
                ))
            return errors

    def build_ingestion_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_model = CreateRunFromIngestionRequest(
            ingestion_batch_id="epic20-build",
            invoices=payload.get("invoices", []),
            payments=payload.get("payments", []),
        )
        return {
            "invoices": [item.model_dump(exclude_none=True) for item in request_model.invoices],
            "payments": [item.model_dump(exclude_none=True) for item in request_model.payments],
        }