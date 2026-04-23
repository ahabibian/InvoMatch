from dataclasses import dataclass
from pathlib import Path

from .environment import EnvironmentName
from .models import ApplicationSettings


@dataclass(frozen=True)
class StartupValidationResult:
    is_valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    selected_environment: str
    resolved_paths: tuple[str, ...]
    enabled_features: tuple[str, ...]


def _path_strings(settings: ApplicationSettings) -> tuple[str, ...]:
    paths = [
        settings.persistence.run_store_path,
        settings.persistence.review_store_path,
        settings.persistence.feedback_store_path,
        settings.persistence.match_record_store_path,
        settings.persistence.export_artifact_db_path,
        settings.persistence.input_session_db_path,
        settings.persistence.ingestion_batch_root,
        settings.storage.artifact_root_path,
        settings.storage.export_directory,
        settings.storage.upload_root_path,
        settings.storage.temp_directory,
        settings.storage.log_directory,
    ]
    return tuple(str(path) for path in paths)


def validate_application_settings(settings: ApplicationSettings) -> StartupValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if settings.runtime.lease_seconds <= 0:
        errors.append("runtime.lease_seconds must be greater than zero")
    if settings.runtime.retry_budget < 0:
        errors.append("runtime.retry_budget must be zero or greater")
    if settings.runtime.stuck_run_timeout_seconds <= 0:
        errors.append("runtime.stuck_run_timeout_seconds must be greater than zero")
    if settings.runtime.recovery_scan_interval_seconds <= 0:
        errors.append("runtime.recovery_scan_interval_seconds must be greater than zero")
    if settings.scheduler.default_scan_limit <= 0:
        errors.append("scheduler.default_scan_limit must be greater than zero")
    if settings.scheduler.tick_interval_seconds <= 0:
        errors.append("scheduler.tick_interval_seconds must be greater than zero")
    if settings.upload.upload_max_file_size_mb <= 0:
        errors.append("upload.upload_max_file_size_mb must be greater than zero")
    if settings.upload.upload_temp_retention_hours < 0:
        errors.append("upload.upload_temp_retention_hours must be zero or greater")

    if settings.security.auth_enabled and not settings.security.seed_tokens_json.strip():
        errors.append("security.seed_tokens_json must not be empty when auth is enabled")

    if settings.environment == EnvironmentName.TEST and settings.scheduler.scheduler_enabled:
        errors.append("scheduler must be disabled in test environment by default")

    if settings.environment == EnvironmentName.PRODUCTION:
        for path in _path_strings(settings):
            if path.startswith("output/") or path.startswith("output\\"):
                errors.append("production paths must not use relative output directories")
                break

        if settings.observability.log_level.strip().upper() == "DEBUG":
            errors.append("production log level must not default to DEBUG")

        if not settings.security.auth_enabled:
            errors.append("production environment must not run with auth disabled")

    enabled_features = []
    if settings.feature_flags.enable_review_persistence:
        enabled_features.append("review_persistence")
    if settings.feature_flags.enable_feedback_learning:
        enabled_features.append("feedback_learning")
    if settings.feature_flags.enable_export_artifacts:
        enabled_features.append("export_artifacts")
    if settings.feature_flags.enable_runtime_recovery:
        enabled_features.append("runtime_recovery")
    if settings.feature_flags.enable_startup_repair:
        enabled_features.append("startup_repair")
    if settings.security.auth_enabled:
        enabled_features.append("auth_boundary")
    if settings.security.security_audit_enabled:
        enabled_features.append("security_audit")

    return StartupValidationResult(
        is_valid=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
        selected_environment=settings.environment.value,
        resolved_paths=_path_strings(settings),
        enabled_features=tuple(enabled_features),
    )