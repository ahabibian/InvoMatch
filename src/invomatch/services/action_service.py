from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from invomatch.api.product_models.action import ProductActionRequest
from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.dispatcher import ActionDispatcher
from invomatch.services.actions.execution_service import ActionExecutionService
from invomatch.services.actions.handlers.export_run import ExportRunActionHandler
from invomatch.services.actions.handlers.resolve_review import ResolveReviewActionHandler
from invomatch.services.actions.result import ActionExecutionStatus
from invomatch.services.export.export_service import ExportService
from invomatch.services.export_delivery_service import ExportDeliveryService
from invomatch.services.run_store import RunStore
from invomatch.services.storage.local_storage import LocalArtifactStorage


@dataclass(slots=True)
class ActionExecutionResult:
    run_id: str
    action_type: str
    accepted: bool
    status: str
    message: str | None = None


class ActionService:
    SUPPORTED_ACTIONS = {
        "resolve_review",
        "export_run",
    }

    def __init__(
        self,
        *,
        run_store: RunStore | None = None,
        export_base_dir: Path | None = None,
    ) -> None:
        dispatcher = ActionDispatcher()
        dispatcher.register("resolve_review", ResolveReviewActionHandler)

        export_root = Path(export_base_dir or (Path("output") / "exports"))
        export_root.mkdir(parents=True, exist_ok=True)

        export_repository = SqliteExportArtifactRepository(
            str(export_root / "export_artifacts.sqlite3")
        )
        export_storage = LocalArtifactStorage(export_root)

        export_service = ExportService(run_store=run_store)

        def export_generator(run_id: str, format: str) -> bytes:
            return export_service.export(
                run_id=run_id,
                export_format=format_enum(format),
            ).content

        delivery_service = ExportDeliveryService(
            repository=export_repository,
            storage=export_storage,
            export_generator=export_generator,
        )

        dispatcher.register(
            "export_run",
            lambda: ExportRunActionHandler(delivery_service=delivery_service),
        )

        self._execution_service = ActionExecutionService(dispatcher)

    def execute(self, *, run_id: str, request: ProductActionRequest) -> ActionExecutionResult:
        action_type = str(request.action_type)

        if action_type not in self.SUPPORTED_ACTIONS:
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=False,
                status="unsupported_action",
                message=f"Unsupported action type: {action_type}",
            )

        command = ActionCommand(
            action_type=action_type,
            run_id=run_id,
            target_id=request.target_id,
            payload=request.payload or {},
            note=request.note,
        )

        try:
            result = self._execution_service.execute(command)
        except (ValueError, KeyError) as exc:
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=False,
                status="invalid_request",
                message=str(exc),
            )

        if result.status == ActionExecutionStatus.SUCCESS:
            message = "Action executed successfully."
            if action_type == "resolve_review":
                message = "Review decision applied."
            elif action_type == "export_run":
                message = f"Export artifact created (format={request.payload.get('format')})."
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=True,
                status="accepted",
                message=message,
            )

        if result.status == ActionExecutionStatus.NO_OP:
            message = "Action already applied."
            if action_type == "resolve_review":
                message = "Review decision already applied."
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=True,
                status="accepted",
                message=message,
            )

        if result.status == ActionExecutionStatus.CONFLICT:
            message = "Action conflicts with current state."
            if action_type == "resolve_review":
                message = "Review decision conflicts with current state."
            return ActionExecutionResult(
                run_id=run_id,
                action_type=action_type,
                accepted=False,
                status="conflict",
                message=message,
            )

        return ActionExecutionResult(
            run_id=run_id,
            action_type=action_type,
            accepted=False,
            status="failed",
            message="Action could not be completed.",
        )


def format_enum(value: str):
    from invomatch.domain.export import ExportFormat

    return ExportFormat(value)