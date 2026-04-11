from __future__ import annotations

from invomatch.domain.input_boundary.models import InputError, InputErrorType


class FileValidator:
    MAX_FILE_SIZE_BYTES = 1024 * 1024

    def validate(
        self,
        *,
        filename: str | None,
        content_type: str | None,
        content_bytes: bytes,
    ) -> list[InputError]:
        errors: list[InputError] = []

        if not filename:
            errors.append(InputError(
                type=InputErrorType.FILE,
                code="missing_filename",
                message="Uploaded file must have a filename",
                field="file",
            ))
            return errors

        if not filename.lower().endswith(".csv"):
            errors.append(InputError(
                type=InputErrorType.FILE,
                code="unsupported_file_extension",
                message="Only CSV files are supported",
                field="file",
            ))

        if len(content_bytes) <= 0:
            errors.append(InputError(
                type=InputErrorType.FILE,
                code="empty_file",
                message="Uploaded file must not be empty",
                field="file",
            ))

        if len(content_bytes) > self.MAX_FILE_SIZE_BYTES:
            errors.append(InputError(
                type=InputErrorType.FILE,
                code="file_too_large",
                message="Uploaded file exceeds maximum allowed size",
                field="file",
            ))

        allowed_content_types = {
            None,
            "",
            "text/csv",
            "application/csv",
            "application/vnd.ms-excel",
            "application/octet-stream",
        }

        if content_type not in allowed_content_types:
            errors.append(InputError(
                type=InputErrorType.FILE,
                code="unsupported_content_type",
                message="Unsupported file content type",
                field="file",
            ))

        return errors