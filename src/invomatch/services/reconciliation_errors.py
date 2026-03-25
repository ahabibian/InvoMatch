from __future__ import annotations


class ReconciliationServiceError(Exception):
    def __init__(self, *, error_code: str, message: str, run_id: str | None = None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.run_id = run_id


class ReconciliationInputValidationError(ReconciliationServiceError):
    def __init__(self, message: str):
        super().__init__(error_code="input_validation_failed", message=message)


class ReconciliationExecutionError(ReconciliationServiceError):
    def __init__(self, message: str, *, run_id: str | None = None):
        super().__init__(error_code="execution_failed", message=message, run_id=run_id)


class RunStorageError(ReconciliationServiceError):
    def __init__(self, message: str, *, run_id: str | None = None):
        super().__init__(error_code="run_storage_failed", message=message, run_id=run_id)


class ConcurrencyConflictError(RunStorageError):
    def __init__(self, message: str, *, run_id: str | None = None):
        super().__init__(message, run_id=run_id)


class RunLeaseConflictError(RunStorageError):
    def __init__(self, message: str, *, run_id: str | None = None):
        super().__init__(message, run_id=run_id)
