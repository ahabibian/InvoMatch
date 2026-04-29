from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from invomatch.domain.export import ExportFormat, FinalizedResult
from invomatch.domain.tenant import TenantContext
from invomatch.services.export.errors import (
    ExportDataIncompleteError,
    InconsistentProjectionStateError,
    RunNotExportableError,
    RunNotFoundError,
    UnsupportedExportFormatError,
)
from invomatch.services.export.finalized_projection_store import FinalizedProjectionStore
from invomatch.services.export.mapper import ExportMapper
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
        projection_store: FinalizedProjectionStore | None = None,
        mapper: ExportMapper | None = None,
        run_store: RunStore | None = None,
        csv_exporter: CsvExporter | None = None,
        json_exporter: JsonExporter | None = None,
    ) -> None:
        self._run_store = run_store
        self._projection_store = projection_store
        self._mapper = mapper or ExportMapper()
        self._csv = csv_exporter or CsvExporter()
        self._json = json_exporter or JsonExporter()

    def export(
        self,
        *,
        run_id: str,
        export_format: ExportFormat,
        tenant_id: str | None = None,
        tenant_context: TenantContext | None = None,
    ) -> ExportResult:
        effective_tenant_id = tenant_context.tenant_id if tenant_context is not None else tenant_id
        if not effective_tenant_id:
            raise ExportDataIncompleteError("tenant_id is required for finalized projection export")

        run = self._load_run(run_id, tenant_id=effective_tenant_id)

        if str(run.status) != "completed":
            raise RunNotExportableError(f"run is not exportable in status={run.status}")

        results = self._load_finalized_projection_results(
            tenant_id=effective_tenant_id,
            run_id=run_id,
        )

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

    def _load_run(self, run_id: str, tenant_id: str | None = None):
        try:
            if self._run_store is None:
                return load_reconciliation_run(run_id)
            run = self._run_store.get_run(run_id, tenant_id=tenant_id)
            if run is None:
                raise KeyError(f"Reconciliation run not found: {run_id}")
            return run
        except KeyError as exc:
            raise RunNotFoundError(f"Reconciliation run not found: {run_id}") from exc

    def _load_finalized_projection_results(
        self,
        *,
        tenant_id: str,
        run_id: str,
    ) -> list[FinalizedResult]:
        if self._projection_store is None:
            raise ExportDataIncompleteError("finalized projection store is required for export")

        results = self._projection_store.get_results(
            tenant_id=tenant_id,
            run_id=run_id,
        )
        if results is None:
            raise InconsistentProjectionStateError(
                f"completed run has no finalized projection: tenant_id={tenant_id}, run_id={run_id}"
            )

        return results

    def _infer_currency(self, results) -> str:
        if not results:
            raise ValueError("cannot export empty finalized result set")

        currency = results[0].invoice.currency

        for result in results:
            if result.invoice.currency != currency:
                raise ValueError("mixed currencies are not supported for export")

        return currency
