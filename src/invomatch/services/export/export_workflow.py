from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from invomatch.services.export.export_writer import ExportWriter
from invomatch.services.reconciliation_runs import load_reconciliation_run
from invomatch.services.run_store import RunStore


@dataclass(slots=True)
class ExportWorkflowResult:
    run_id: str
    export_format: str
    export_status: str
    artifact_path: str


class ExportWorkflowService:
    def __init__(
        self,
        *,
        run_store: RunStore | None = None,
        writer: ExportWriter | None = None,
    ) -> None:
        self._run_store = run_store
        self._writer = writer or ExportWriter()

    def execute(self, *, run_id: str, export_format: str) -> ExportWorkflowResult:
        normalized_format = str(export_format).lower().strip()

        if normalized_format != "json":
            raise ValueError(f"Unsupported export format: {normalized_format}")

        if self._run_store is None:
            run = load_reconciliation_run(run_id)
        else:
            run = load_reconciliation_run(run_id, run_store=self._run_store)

        if str(run.status) != "completed":
            raise ValueError(f"Run is not exportable in status={run.status}")

        payload = {
            "run_id": str(run.run_id),
            "status": str(run.status),
            "created_at": run.created_at.isoformat(),
            "updated_at": run.updated_at.isoformat() if run.updated_at else None,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "invoice_csv_path": str(run.invoice_csv_path),
            "payment_csv_path": str(run.payment_csv_path),
            "error_message": run.error_message,
            "report": run.report.model_dump(mode="json") if run.report is not None else None,
        }

        artifact_path = self._writer.write_json(run_id=str(run.run_id), payload=payload)

        return ExportWorkflowResult(
            run_id=str(run.run_id),
            export_format=normalized_format,
            export_status="completed",
            artifact_path=artifact_path.as_posix(),
        )