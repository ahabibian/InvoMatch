from __future__ import annotations


class ExportError(Exception):
    """Base error for export-layer failures."""


class RunNotFoundError(ExportError):
    """Raised when the requested run does not exist."""


class RunNotExportableError(ExportError):
    """Raised when the run exists but is not in an exportable state."""


class UnsupportedExportFormatError(ExportError):
    """Raised when the requested export format is not supported."""


class ExportDataIncompleteError(ExportError):
    """Raised when finalized export data is missing required information."""


class FinalizedResultIntegrityError(ExportError):
    """Raised when finalized result data violates export integrity rules."""

class InconsistentProjectionStateError(ExportError):
    """Raised when finalized system state is completed but projection is missing."""