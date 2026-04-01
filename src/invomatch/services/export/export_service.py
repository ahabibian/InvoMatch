from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from invomatch.domain.export import ExportFormat
from invomatch.services.export.errors import (
    RunNotFoundError,
    UnsupportedExportFormatError,
)
from invomatch.services.export.mapper import ExportMapper
from invomatch.services.export.run_finalized_result_reader import RunFinalizedResultReader
from invomatch.services.export.serializers import CsvExporter, JsonExporter
from invomatch.services.reconciliation_runs import load_reconciliation_run
from invomatch.services.run_store import RunStore


@dataclass(slots=True)
class ExportResult:
    content: bytes
    content_type: str
    filename: str


class ExportService:
    def __init__(
        self,
        *,
        reader: RunFinalizedResultReader | None = None,
        mapper: ExportMapper | None = None,
        run_store: RunStore | None = None,
        csv_exporter: CsvExporter | None = None,
        json_exporter: JsonExporter | None = None,
    ) -> None:
        self._run_store = run_store
        self._reader = reader or RunFinalizedResultReader(run_store=run_store)
        self._mapper = mapper or ExportMapper()
        self._csv = csv_exporter or CsvExporter()
        self._json = json_exporter or JsonExporter()

    def export(self, *, run_id: str, export_format: ExportFormat) -> ExportResult:
        run = self._load_run(run_id)
        results = self._reader.read(run_id=run_id)

        bundle = self._mapper.build_bundle(
            run_id=str(run.run_id),
            status=str(run.status),
            currency=self._infer_currency(results),
            exported_at=datetime.now(timezone.utc),
            results=results,
        )

        if export_format is ExportFormat.JSON:
            body = self._json.export(bundle)
            return ExportResult(
                content=body,
                content_type="application/json",
                filename=f"run_{run_id}.json",
            )

        if export_format is ExportFormat.CSV:
            body = self._csv.export(bundle)
            return ExportResult(
                content=body,
                content_type="text/csv",
                filename=f"run_{run_id}.csv",
            )

        raise UnsupportedExportFormatError(f"Unsupported format: {export_format}")

    def _load_run(self, run_id: str):
        try:
            if self._run_store is None:
                return load_reconciliation_run(run_id)
            return load_reconciliation_run(run_id, run_store=self._run_store)
        except KeyError as exc:
            raise RunNotFoundError(f"Reconciliation run not found: {run_id}") from exc

    def _infer_currency(self, results) -> str:
        if not results:
            raise ValueError("cannot export empty finalized result set")

        currency = results[0].invoice.currency

        for result in results:
            if result.invoice.currency != currency:
                raise ValueError("mixed currencies are not supported for export")

        return currency
