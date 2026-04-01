from pathlib import Path

from invomatch.api.product_models.action import ProductActionRequest
from invomatch.domain.models import ReconciliationReport
from invomatch.services.action_service import ActionService
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.handlers.export_run import ExportRunActionHandler
from invomatch.services.actions.result import ActionExecutionStatus
from invomatch.services.export.export_workflow import ExportWorkflowService
from invomatch.services.export.export_writer import ExportWriter
from invomatch.services.reconciliation_runs import (
    create_reconciliation_run,
    update_reconciliation_run,
)
from invomatch.services.run_store import JsonRunStore


def _completed_run_store(tmp_path: Path) -> tuple[JsonRunStore, str]:
    run_store = JsonRunStore(tmp_path / "runs.json")

    invoice_path = tmp_path / "invoices.csv"
    payment_path = tmp_path / "payments.csv"
    invoice_path.write_text("invoice_id,amount\ninv-1,100\n", encoding="utf-8")
    payment_path.write_text("payment_id,amount\npay-1,100\n", encoding="utf-8")

    run = create_reconciliation_run(
        invoice_csv_path=invoice_path,
        payment_csv_path=payment_path,
        run_store=run_store,
    )
    update_reconciliation_run(run.run_id, status="running", run_store=run_store)

    report = ReconciliationReport(
        total_invoices=1,
        matched=1,
        unmatched=0,
        duplicate_detected=0,
        partial_match=0,
        results=[],
    )
    completed = update_reconciliation_run(
        run.run_id,
        status="completed",
        report=report,
        run_store=run_store,
    )
    return run_store, completed.run_id


def test_export_run_handler_creates_real_json_artifact(tmp_path: Path):
    run_store, run_id = _completed_run_store(tmp_path)
    workflow = ExportWorkflowService(
        run_store=run_store,
        writer=ExportWriter(tmp_path / "exports"),
    )
    handler = ExportRunActionHandler(workflow=workflow)

    command = ActionCommand(
        action_type="export_run",
        run_id=run_id,
        payload={"format": "json"},
    )

    result = handler.handle(command)

    assert result.status == ActionExecutionStatus.SUCCESS
    assert result.response_payload["export_status"] == "completed"
    assert result.response_payload["export_format"] == "json"

    artifact_path = Path(result.response_payload["artifact_path"])
    assert artifact_path.exists()
    assert artifact_path.name == f"run_{run_id}_export.json"


def test_export_run_handler_is_deterministic_for_repeated_requests(tmp_path: Path):
    run_store, run_id = _completed_run_store(tmp_path)
    workflow = ExportWorkflowService(
        run_store=run_store,
        writer=ExportWriter(tmp_path / "exports"),
    )
    handler = ExportRunActionHandler(workflow=workflow)

    command = ActionCommand(
        action_type="export_run",
        run_id=run_id,
        payload={"format": "json"},
    )

    first = handler.handle(command)
    second = handler.handle(command)

    assert first.response_payload["artifact_path"] == second.response_payload["artifact_path"]


def test_action_service_rejects_export_without_format():
    service = ActionService()

    result = service.execute(
        run_id="run-123",
        request=ProductActionRequest(
            action_type="export_run",
            target_id=None,
            payload={},
            note="missing format",
        ),
    )

    assert result.accepted is False
    assert result.status == "invalid_request"