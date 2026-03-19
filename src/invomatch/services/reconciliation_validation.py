from __future__ import annotations

from pathlib import Path

from invomatch.services.reconciliation_errors import ReconciliationInputValidationError


_ALLOWED_SUFFIX = ".csv"


def validate_reconciliation_execution_paths(invoice_csv_path: Path, payment_csv_path: Path) -> None:
    _validate_csv_path("invoice_csv_path", invoice_csv_path)
    _validate_csv_path("payment_csv_path", payment_csv_path)


def _display_path(path: Path) -> str:
    return path.as_posix()


def _validate_csv_path(field_name: str, path: Path) -> None:
    raw_path = str(path).strip()
    if not raw_path:
        raise ReconciliationInputValidationError(f"{field_name} must not be empty")

    if path.suffix.lower() != _ALLOWED_SUFFIX:
        raise ReconciliationInputValidationError(f"{field_name} must point to a .csv file")

    if not path.exists() or not path.is_file():
        raise ReconciliationInputValidationError(f"{field_name} does not exist: {_display_path(path)}")

    try:
        with path.open("r", encoding="utf-8", newline=""):
            return
    except OSError as exc:
        raise ReconciliationInputValidationError(f"{field_name} is not readable: {_display_path(path)}") from exc
