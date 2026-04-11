from __future__ import annotations

from typing import Any, Callable

from invomatch.domain.input_boundary.models import (
    InputSession,
    InputSessionStatus,
    InputType,
    InputError,
)
from invomatch.services.input_boundary.repository import InputSessionRepository
from invomatch.services.input_boundary.json_input_service import JsonInputService


class InputProcessingService:
    def __init__(
        self,
        repository: InputSessionRepository,
        json_service: JsonInputService,
        ingestion_service: Callable[[dict[str, Any]], str],
        run_creation_service: Callable[[str], str],
    ) -> None:
        self._repository = repository
        self._json_service = json_service
        self._ingestion_service = ingestion_service
        self._run_creation_service = run_creation_service


    def process_json(self, payload: dict[str, Any]) -> InputSession:
        session = InputSession(input_type=InputType.JSON)
        session = self._repository.create(session)

        errors = self._json_service.validate(payload)

        if errors:
            session.mark_rejected(errors)
            return self._repository.save(session)

        session.mark_validated()
        session = self._repository.save(session)

        try:
            ingestion_request = self._json_service.build_ingestion_request(payload)

            ingestion_batch_id = self._ingestion_service(ingestion_request)
            session.mark_ingested(ingestion_batch_id)
            session = self._repository.save(session)

            run_id = self._run_creation_service(ingestion_batch_id)
            session.mark_run_created(run_id)
            session = self._repository.save(session)

            return session

        except Exception as exc:
            error = InputError(
                type="runtime_error",
                code="processing_failed",
                message=str(exc)
            )
            session.mark_failed([error])
            return self._repository.save(session)