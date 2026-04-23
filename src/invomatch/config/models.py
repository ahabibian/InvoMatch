from dataclasses import dataclass
from pathlib import Path

from .environment import EnvironmentName


@dataclass(frozen=True)
class PersistenceSettings:
    run_store_backend: str
    run_store_path: Path
    review_store_backend: str
    review_store_path: Path
    feedback_store_backend: str
    feedback_store_path: Path
    match_record_store_backend: str
    match_record_store_path: Path
    export_artifact_db_path: Path
    input_session_db_path: Path
    ingestion_batch_root: Path


@dataclass(frozen=True)
class StorageSettings:
    artifact_root_path: Path
    export_directory: Path
    upload_root_path: Path
    temp_directory: Path
    log_directory: Path


@dataclass(frozen=True)
class RuntimeSettings:
    lease_seconds: int
    retry_budget: int
    stuck_run_timeout_seconds: int
    recovery_scan_interval_seconds: int
    runtime_recovery_enabled: bool
    startup_repair_enabled: bool
    startup_validation_enabled: bool


@dataclass(frozen=True)
class ObservabilitySettings:
    log_level: str
    structured_logging_enabled: bool
    metrics_enabled: bool
    runtime_event_logging_enabled: bool
    startup_report_logging_enabled: bool


@dataclass(frozen=True)
class UploadSettings:
    upload_max_file_size_mb: int
    upload_temp_retention_hours: int
    allowed_input_formats: tuple[str, ...]


@dataclass(frozen=True)
class SchedulerSettings:
    scheduler_enabled: bool
    default_scan_limit: int
    tick_interval_seconds: int


@dataclass(frozen=True)
class FeatureFlagSettings:
    enable_review_persistence: bool
    enable_feedback_learning: bool
    enable_export_artifacts: bool
    enable_runtime_recovery: bool
    enable_startup_repair: bool


@dataclass(frozen=True)
class SecuritySettings:
    auth_enabled: bool
    public_health_enabled: bool
    public_readiness_enabled: bool
    seed_tokens_json: str
    security_audit_enabled: bool


@dataclass(frozen=True)
class ApplicationSettings:
    environment: EnvironmentName
    persistence: PersistenceSettings
    storage: StorageSettings
    runtime: RuntimeSettings
    observability: ObservabilitySettings
    upload: UploadSettings
    scheduler: SchedulerSettings
    feature_flags: FeatureFlagSettings
    security: SecuritySettings