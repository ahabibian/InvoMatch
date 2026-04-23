import os
from pathlib import Path

from .defaults import (
    default_allowed_input_formats,
    environment_root,
    log_root,
    temp_root,
)
from .environment import EnvironmentName
from .models import (
    ApplicationSettings,
    FeatureFlagSettings,
    ObservabilitySettings,
    PersistenceSettings,
    RuntimeSettings,
    SchedulerSettings,
    SecuritySettings,
    StorageSettings,
    UploadSettings,
)


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _get_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return Path(value)


def _get_environment() -> EnvironmentName:
    raw_value = os.getenv("INVOMATCH_ENV", EnvironmentName.LOCAL.value).strip().lower()
    return EnvironmentName(raw_value)


def load_settings_from_environment() -> ApplicationSettings:
    environment = _get_environment()
    root = environment_root(environment)
    logs = log_root(environment)
    temp = temp_root(environment)

    persistence = PersistenceSettings(
        run_store_backend=os.getenv("INVOMATCH_RUN_STORE_BACKEND", "sqlite"),
        run_store_path=_get_path("INVOMATCH_RUN_STORE_PATH", root / "reconciliation_runs.sqlite3"),
        review_store_backend=os.getenv("INVOMATCH_REVIEW_STORE_BACKEND", "sqlite"),
        review_store_path=_get_path("INVOMATCH_REVIEW_STORE_PATH", root / "review_store.sqlite3"),
        feedback_store_backend=os.getenv("INVOMATCH_FEEDBACK_STORE_BACKEND", "sqlite"),
        feedback_store_path=_get_path("INVOMATCH_FEEDBACK_STORE_PATH", root / "feedback_store.sqlite3"),
        match_record_store_backend=os.getenv("INVOMATCH_MATCH_RECORD_STORE_BACKEND", "sqlite"),
        match_record_store_path=_get_path("INVOMATCH_MATCH_RECORD_STORE_PATH", root / "match_records.sqlite3"),
        export_artifact_db_path=_get_path("INVOMATCH_EXPORT_ARTIFACT_DB_PATH", root / "export_artifacts.sqlite3"),
        input_session_db_path=_get_path("INVOMATCH_INPUT_SESSION_DB_PATH", root / "input_sessions.sqlite3"),
        ingestion_batch_root=_get_path("INVOMATCH_INGESTION_BATCH_ROOT", root / "ingestion_batches"),
    )

    storage = StorageSettings(
        artifact_root_path=_get_path("INVOMATCH_ARTIFACT_ROOT_PATH", root / "artifacts"),
        export_directory=_get_path("INVOMATCH_EXPORT_DIRECTORY", root / "exports"),
        upload_root_path=_get_path("INVOMATCH_UPLOAD_ROOT_PATH", root / "uploads"),
        temp_directory=_get_path("INVOMATCH_TEMP_DIRECTORY", temp),
        log_directory=_get_path("INVOMATCH_LOG_DIRECTORY", logs),
    )

    runtime = RuntimeSettings(
        lease_seconds=_get_int("INVOMATCH_LEASE_SECONDS", 60),
        retry_budget=_get_int("INVOMATCH_RETRY_BUDGET", 3),
        stuck_run_timeout_seconds=_get_int("INVOMATCH_STUCK_RUN_TIMEOUT_SECONDS", 600),
        recovery_scan_interval_seconds=_get_int("INVOMATCH_RECOVERY_SCAN_INTERVAL_SECONDS", 60),
        runtime_recovery_enabled=_get_bool("INVOMATCH_RUNTIME_RECOVERY_ENABLED", True),
        startup_repair_enabled=_get_bool("INVOMATCH_STARTUP_REPAIR_ENABLED", True),
        startup_validation_enabled=_get_bool("INVOMATCH_STARTUP_VALIDATION_ENABLED", True),
    )

    observability = ObservabilitySettings(
        log_level=os.getenv("INVOMATCH_LOG_LEVEL", "INFO"),
        structured_logging_enabled=_get_bool("INVOMATCH_STRUCTURED_LOGGING_ENABLED", environment == EnvironmentName.PRODUCTION),
        metrics_enabled=_get_bool("INVOMATCH_METRICS_ENABLED", True),
        runtime_event_logging_enabled=_get_bool("INVOMATCH_RUNTIME_EVENT_LOGGING_ENABLED", True),
        startup_report_logging_enabled=_get_bool("INVOMATCH_STARTUP_REPORT_LOGGING_ENABLED", True),
    )

    upload = UploadSettings(
        upload_max_file_size_mb=_get_int("INVOMATCH_UPLOAD_MAX_FILE_SIZE_MB", 25),
        upload_temp_retention_hours=_get_int("INVOMATCH_UPLOAD_TEMP_RETENTION_HOURS", 24),
        allowed_input_formats=default_allowed_input_formats(),
    )

    scheduler = SchedulerSettings(
        scheduler_enabled=_get_bool("INVOMATCH_SCHEDULER_ENABLED", environment in {EnvironmentName.STAGING, EnvironmentName.PRODUCTION}),
        default_scan_limit=_get_int("INVOMATCH_SCHEDULER_DEFAULT_SCAN_LIMIT", 100),
        tick_interval_seconds=_get_int("INVOMATCH_SCHEDULER_TICK_INTERVAL_SECONDS", 60),
    )

    feature_flags = FeatureFlagSettings(
        enable_review_persistence=_get_bool("INVOMATCH_ENABLE_REVIEW_PERSISTENCE", True),
        enable_feedback_learning=_get_bool("INVOMATCH_ENABLE_FEEDBACK_LEARNING", True),
        enable_export_artifacts=_get_bool("INVOMATCH_ENABLE_EXPORT_ARTIFACTS", True),
        enable_runtime_recovery=_get_bool("INVOMATCH_ENABLE_RUNTIME_RECOVERY", True),
        enable_startup_repair=_get_bool("INVOMATCH_ENABLE_STARTUP_REPAIR", True),
    )

    security = SecuritySettings(
        auth_enabled=_get_bool("INVOMATCH_AUTH_ENABLED", True),
        public_health_enabled=_get_bool("INVOMATCH_PUBLIC_HEALTH_ENABLED", True),
        public_readiness_enabled=_get_bool("INVOMATCH_PUBLIC_READINESS_ENABLED", True),
        seed_tokens_json=os.getenv(
            "INVOMATCH_SECURITY_SEED_TOKENS_JSON",
            '[{"token":"viewer-token","user_id":"viewer-1","username":"viewer","role":"viewer","status":"active"},{"token":"operator-token","user_id":"operator-1","username":"operator","role":"operator","status":"active"},{"token":"admin-token","user_id":"admin-1","username":"admin","role":"admin","status":"active"},{"token":"inactive-token","user_id":"inactive-1","username":"inactive-user","role":"viewer","status":"inactive"}]',
        ),
        security_audit_enabled=_get_bool("INVOMATCH_SECURITY_AUDIT_ENABLED", True),
    )

    return ApplicationSettings(
        environment=environment,
        persistence=persistence,
        storage=storage,
        runtime=runtime,
        observability=observability,
        upload=upload,
        scheduler=scheduler,
        feature_flags=feature_flags,
        security=security,
    )