from __future__ import annotations

from typing import Any, Callable

from invomatch.domain.input_boundary.models import (
    InputError,
    InputErrorType,
    InputSession,
    InputType,
)
from invomatch.services.input_boundary.file_input_service import FileInputService
from invomatch.services.input_boundary.json_input_service import JsonInputService
from invomatch.services.input_boundary.repository import InputSessionRepository


class InputProcessingService:
    def __init__(
        self,
        repository: InputSessionRepository,
        json_service: JsonInputService,
        file_service: FileInputService,
        run_from_ingestion_service: Callable[[str, dict[str, Any]], Any],
    ) -> None:
        self._repository = repository
        self._json_service = json_service
        self._file_service = file_service
        self._run_from_ingestion_service = run_from_ingestion_service

    def process_json(self, payload: dict[str, Any]) -> InputSession:
        session = InputSession(input_type=InputType.JSON)
        session = self._repository.create(session)

        errors = self._json_service.validate(payload)
        if errors:
            session.mark_rejected(errors)
            return self._repository.save(session)

        session.mark_validated()
        session = self._repository.save(session)

        ingestion_request = self._json_service.build_ingestion_request(payload)
        ingestion_batch_id = session.input_id

        session.mark_ingested(ingestion_batch_id)
        session = self._repository.save(session)

        try:
            result = self._run_from_ingestion_service(ingestion_batch_id, ingestion_request)

            if getattr(result, "run_id", None):
                session.mark_run_created(result.run_id)
                return self._repository.save(session)

            error = InputError(
                type=InputErrorType.INGESTION,
                code=getattr(result, "reason_code", "run_not_created"),
                message=f"Run was not created. status={getattr(result, 'status', 'unknown')}",
            )
            session.mark_failed([error])
            return self._repository.save(session)

        except Exception as exc:
            error = InputError(
                type=InputErrorType.RUNTIME,
                code="processing_failed",
                message=str(exc),
            )
            session.mark_failed([error])
            return self._repository.save(session)

    def process_file(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        content_bytes: bytes,
    ) -> InputSession:
        session = InputSession(
            input_type=InputType.FILE,
            source_filename=filename,
            source_content_type=content_type,
            source_size_bytes=len(content_bytes),
        )
        session = self._repository.create(session)

        errors = self._file_service.validate_file(
            filename=filename,
            content_type=content_type,
            content_bytes=content_bytes,
        )
        if errors:
            session.mark_rejected(errors)
            return self._repository.save(session)

        try:
            ingestion_request = self._file_service.build_ingestion_request(
                filename=filename,
                content_type=content_type,
                content_bytes=content_bytes,
            )
        except Exception as exc:
            error = InputError(
                type=InputErrorType.FILE,
                code="file_processing_failed",
                message=str(exc),
            )
            session.mark_failed([error])
            return self._repository.save(session)

        session.mark_validated()
        session = self._repository.save(session)

        ingestion_batch_id = session.input_id
        session.mark_ingested(ingestion_batch_id)
        session = self._repository.save(session)

        try:
            result = self._run_from_ingestion_service(ingestion_batch_id, ingestion_request)

            if getattr(result, "run_id", None):
                session.mark_run_created(result.run_id)
                return self._repository.save(session)

            error = InputError(
                type=InputErrorType.INGESTION,
                code=getattr(result, "reason_code", "run_not_created"),
                message=f"Run was not created. status={getattr(result, 'status', 'unknown')}",
            )
            session.mark_failed([error])
            return self._repository.save(session)

        except Exception as exc:
            error = InputError(
                type=InputErrorType.RUNTIME,
                code="processing_failed",
                message=str(exc),
            )
            session.mark_failed([error])
            return self._repository.save(session)