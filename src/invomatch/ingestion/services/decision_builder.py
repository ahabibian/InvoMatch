from __future__ import annotations

from invomatch.ingestion.models.ingestion_result import IngestionStatus
from invomatch.ingestion.models.validation_models import ValidationResult


def build_ingestion_status(validation: ValidationResult) -> IngestionStatus:
    if validation.errors:
        return IngestionStatus.REJECTED

    if validation.warnings:
        return IngestionStatus.ACCEPTED_WITH_FLAGS

    return IngestionStatus.ACCEPTED_CLEAN