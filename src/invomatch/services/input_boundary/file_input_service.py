from __future__ import annotations

from invomatch.domain.input_boundary.models import InputError, InputErrorType
from invomatch.services.input_boundary.csv_input_mapper import CsvInputMapper
from invomatch.services.input_boundary.csv_input_parser import CsvInputParser
from invomatch.services.input_boundary.file_decoder import FileDecoder
from invomatch.services.input_boundary.file_validator import FileValidator


class FileInputService:
    def __init__(
        self,
        *,
        validator: FileValidator | None = None,
        decoder: FileDecoder | None = None,
        parser: CsvInputParser | None = None,
        mapper: CsvInputMapper | None = None,
    ) -> None:
        self._validator = validator or FileValidator()
        self._decoder = decoder or FileDecoder()
        self._parser = parser or CsvInputParser()
        self._mapper = mapper or CsvInputMapper()

    def validate_file(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        content_bytes: bytes,
    ) -> list[InputError]:
        errors = self._validator.validate(
            filename=filename,
            content_type=content_type,
            content_bytes=content_bytes,
        )
        if errors:
            return errors

        try:
            content = self._decoder.decode(content_bytes)
            rows = self._parser.parse(content)
            self._mapper.map(rows)
            return []
        except UnicodeDecodeError:
            return [InputError(
                type=InputErrorType.FILE,
                code="invalid_encoding",
                message="Uploaded file must be valid UTF-8",
                field="file",
            )]
        except ValueError as exc:
            return [InputError(
                type=InputErrorType.FILE,
                code="invalid_csv",
                message=str(exc),
                field="file",
            )]

    def build_ingestion_request(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        content_bytes: bytes,
    ) -> dict[str, list[dict[str, str]]]:
        content = self._decoder.decode(content_bytes)
        rows = self._parser.parse(content)
        return self._mapper.map(rows)