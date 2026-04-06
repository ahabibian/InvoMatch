from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from invomatch.api.product_models.action import ProductActionRequest
from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)
from invomatch.services.actions.action_guard import (
    InvalidActionForStateError,
    UnknownRunStateError,
    validate_action_for_state,
)
from invomatch.services.actions.command import ActionCommand
from invomatch.services.actions.dispatcher import ActionDispatcher
from invomatch.services.actions.execution_service import ActionExecutionService
from invomatch.services.actions.handlers.export_run import ExportRunActionHandler
from invomatch.services.actions.handlers.resolve_review import ResolveReviewActionHandler
from invomatch.services.actions.result import ActionExecutionStatus
from invomatch.services.export.export_service import ExportService
from invomatch.services.export.run_finalized_result_reader import RunFinalizedResultReader
from invomatch.services.export_delivery_service import ExportDeliveryService
from invomatch.services.review_store import InMemoryReviewStore
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
        review_store: InMemoryReviewStore | None = None,
        export_base_dir: Path | None = None,
    ) -> None:
        self._run_store = run_store

        dispatcher = ActionDispatcher()
        dispatcher.register("resolve_review", ResolveReviewActionHandler)

        export_root = Path(export_base_dir or (Path("output") / "exports"))
        export_root.mkdir(parents=True, exist_ok=True)

        export_repository = SqliteExportArtifactRepository(
            str(export_root / "export_artifacts.sqlite3")
        )
        export_storage = LocalArtifactStorage(export_root)

        export_reader = RunFinalizedResultReader(
            run_store=run_store,
            review_store=review_store or InMemoryReviewStore(),
        )

        export_service = ExportService(
            run_store=run_store,
            reader=export_reader,
        )

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

        if self._run_store is not None:
            try:
                run_state = self._get_run_state(run_id)
                validate_action_for_state(run_state=run_state, action_type=action_type)
            except InvalidActionForStateError as exc:
                return ActionExecutionResult(
                    run_id=run_id,
                    action_type=action_type,
                    accepted=False,
                    status="conflict",
                    message=str(exc),
                )
            except UnknownRunStateError as exc:
                return ActionExecutionResult(
                    run_id=run_id,
                    action_type=action_type,
                    accepted=False,
                    status="failed",
                    message=str(exc),
                )
            except RuntimeError as exc:
                message = str(exc)
                if "was not found" in message:
                    return ActionExecutionResult(
                        run_id=run_id,
                        action_type=action_type,
                        accepted=False,
                        status="not_found",
                        message=message,
                    )
                return ActionExecutionResult(
                    run_id=run_id,
                    action_type=action_type,
                    accepted=False,
                    status="failed",
                    message=message,
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

    def _get_run_state(self, run_id: str) -> str:
        run = self._load_run(run_id)

        status = getattr(run, "status", None)
        if not isinstance(status, str) or not status.strip():
            raise RuntimeError(f"Run '{run_id}' does not expose a valid status.")

        return status

    def _load_run(self, run_id: str) -> Any:
        if self._run_store is None:
            raise RuntimeError("ActionService requires run_store for action guard enforcement.")

        get_run = getattr(self._run_store, "get_run", None)
        if callable(get_run):
            run = get_run(run_id)
            if run is None:
                raise RuntimeError(f"Run '{run_id}' was not found.")
            return run

        get_method = getattr(self._run_store, "get", None)
        if callable(get_method):
            run = get_method(run_id)
            if run is None:
                raise RuntimeError(f"Run '{run_id}' was not found.")
            return run

        raise RuntimeError("Run store does not expose a supported run lookup method.")


def format_enum(value: str):
    from invomatch.domain.export import ExportFormat

    return ExportFormat(value)