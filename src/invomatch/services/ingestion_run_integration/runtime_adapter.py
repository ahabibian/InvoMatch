from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from invomatch.domain.models import ReconciliationRun
from invomatch.services.ingestion_run_integration.service import (
    IngestionRunIntegrationService,
)


DEFAULT_INGESTION_BATCH_ROOT = Path("output") / "ingestion_batches"


def _to_jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    return value


def _canonicalize_records(records: list[object]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        jsonable = _to_jsonable(record)
        if not isinstance(jsonable, dict):
            raise TypeError("Accepted ingestion entities must be dict-like or model_dump-capable")
        normalized.append({str(k): _to_jsonable(v) for k, v in jsonable.items()})
    return normalized


def _compute_fingerprint(*, invoices: list[dict[str, Any]], payments: list[dict[str, Any]]) -> str:
    payload = {
        "invoices": invoices,
        "payments": payments,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames: list[str] = sorted({key for row in rows for key in row.keys()})

    with path.open("w", encoding="utf-8", newline="") as handle:
        if not fieldnames:
            handle.write("")
            return

        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: "" if row.get(key) is None else str(row.get(key))
                    for key in fieldnames
                }
            )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class IngestionRunRuntimeAdapter:
    def __init__(
        self,
        *,
        reconcile_and_save: Callable[[Path, Path], ReconciliationRun],
        integration_service: IngestionRunIntegrationService | None = None,
        batch_root: Path | None = None,
    ) -> None:
        self._reconcile_and_save = reconcile_and_save
        self._integration_service = integration_service or IngestionRunIntegrationService()
        self._batch_root = batch_root or DEFAULT_INGESTION_BATCH_ROOT

    def create_run_from_ingestion(
        self,
        *,
        ingestion_batch_id: str,
        ingestion_succeeded: bool,
        accepted_invoices: list[object],
        accepted_payments: list[object],
        rejected_count: int,
        conflict_count: int,
        blocking_conflict: bool,
    ):
        invoices = _canonicalize_records(accepted_invoices)
        payments = _canonicalize_records(accepted_payments)
        fingerprint = _compute_fingerprint(invoices=invoices, payments=payments)

        batch_dir = self._batch_root / ingestion_batch_id
        result_path = batch_dir / "run_result.json"

        existing_run_id: str | None = None
        same_batch_identity = False
        same_normalized_fingerprint = False

        if result_path.exists():
            existing_result = _read_json(result_path)
            existing_run_id = existing_result.get("run_id")
            same_batch_identity = True
            same_normalized_fingerprint = (
                existing_result.get("normalized_fingerprint") == fingerprint
            )

        def _create_run(*, run_input, traceability):
            invoice_rows = _canonicalize_records(run_input["invoices"])
            payment_rows = _canonicalize_records(run_input["payments"])

            invoice_csv_path = batch_dir / "invoices.csv"
            payment_csv_path = batch_dir / "payments.csv"
            traceability_path = batch_dir / "traceability.json"

            _write_csv(invoice_csv_path, invoice_rows)
            _write_csv(payment_csv_path, payment_rows)
            _write_json(
                traceability_path,
                {
                    **traceability,
                    "normalized_fingerprint": fingerprint,
                },
            )

            run = self._reconcile_and_save(invoice_csv_path, payment_csv_path)

            _write_json(
                result_path,
                {
                    "run_id": run.run_id,
                    "normalized_fingerprint": fingerprint,
                    "invoice_csv_path": invoice_csv_path.as_posix(),
                    "payment_csv_path": payment_csv_path.as_posix(),
                    "traceability_path": traceability_path.as_posix(),
                },
            )
            return run.run_id

        return self._integration_service.create_run_from_ingestion(
            ingestion_batch_id=ingestion_batch_id,
            ingestion_succeeded=ingestion_succeeded,
            accepted_invoices=invoices,
            accepted_payments=payments,
            rejected_count=rejected_count,
            conflict_count=conflict_count,
            blocking_conflict=blocking_conflict,
            existing_run_id=existing_run_id,
            same_batch_identity=same_batch_identity,
            same_normalized_fingerprint=same_normalized_fingerprint,
            create_run=_create_run,
        )