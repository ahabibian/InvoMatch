from enum import StrEnum


class Permission(StrEnum):
    INPUT_SUBMIT = "input.submit"
    INPUT_VIEW = "input.view"

    RUNS_CREATE = "runs.create"
    RUNS_CREATE_FROM_INGESTION = "runs.create_from_ingestion"
    RUNS_LIST = "runs.list"
    RUNS_READ = "runs.read"
    RUNS_READ_VIEW = "runs.read_view"
    RUNS_READ_REVIEW = "runs.read_review"

    ACTIONS_RESOLVE_REVIEW = "actions.resolve_review"
    ACTIONS_EXPORT_RUN = "actions.export_run"

    EXPORTS_DOWNLOAD_DIRECT = "exports.download_direct"

    ARTIFACTS_LIST = "artifacts.list"
    ARTIFACTS_READ_METADATA = "artifacts.read_metadata"
    ARTIFACTS_DOWNLOAD = "artifacts.download"

    OPERATIONS_VIEW_METRICS = "operations.view_metrics"
    OPERATIONS_EXECUTE_RECOVERY = "operations.execute_recovery"
    OPERATIONS_EXECUTE_STARTUP_REPAIR = "operations.execute_startup_repair"
    OPERATIONS_MANAGE_ADMIN_SURFACE = "operations.manage_admin_surface"