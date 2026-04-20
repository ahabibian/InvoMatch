# Configuration Model

## 1. Purpose

This document defines the canonical runtime configuration model for InvoMatch.

The goal is to ensure that all runtime-critical configuration is:

- centralized
- typed
- validated
- environment-aware
- startup-safe

No runtime-critical behavior should depend on scattered module defaults.

---

## 2. Root Settings Model

A root ApplicationSettings model will be introduced.

ApplicationSettings contains:

- environment
- persistence
- storage
- runtime
- observability
- upload
- scheduler
- feature_flags

---

## 3. Environment

Environment is a required first-class runtime input.

Allowed values:

- local
- development
- test
- staging
- production

Environment selection must be explicit and validated.

---

## 4. Persistence Settings

PersistenceSettings defines where durable platform state is stored and which persistence backends are active.

Fields:

- run_store_backend
- run_store_path
- review_store_backend
- review_store_path
- feedback_store_backend
- feedback_store_path
- match_record_store_backend
- match_record_store_path
- export_artifact_db_path
- input_session_db_path
- ingestion_batch_root

Rules:

- paths must be environment-isolated
- production paths must not rely on implicit relative defaults
- unsupported backend values must fail validation
- writable directory requirements must be validated at startup

---

## 5. Storage Settings

StorageSettings defines file-based artifact and temporary storage.

Fields:

- artifact_root_path
- export_directory
- upload_root_path
- temp_directory
- log_directory

Rules:

- artifact storage and temp storage must be separated
- upload temp files must not share export artifact directories
- production storage directories must be explicit
- directories must be creatable or already writable

---

## 6. Runtime Settings

RuntimeSettings defines execution and lifecycle parameters.

Fields:

- lease_seconds
- retry_budget
- stuck_run_timeout_seconds
- recovery_scan_interval_seconds
- runtime_recovery_enabled
- startup_repair_enabled
- startup_validation_enabled

Rules:

- lease_seconds must be positive
- retry_budget must be bounded
- timeout values must be positive
- production defaults must be conservative and deterministic

---

## 7. Observability Settings

ObservabilitySettings defines logging and metrics behavior.

Fields:

- log_level
- structured_logging_enabled
- metrics_enabled
- runtime_event_logging_enabled
- startup_report_logging_enabled

Rules:

- production must default to non-debug logging
- structured logging should be enabled in production
- observability features must not silently change application behavior

---

## 8. Upload Settings

UploadSettings defines upload processing boundaries.

Fields:

- upload_max_file_size_mb
- upload_temp_retention_hours
- allowed_input_formats

Rules:

- upload size limits must be validated
- upload retention must be bounded
- upload temp handling must not leak across environments

---

## 9. Scheduler Settings

SchedulerSettings defines operational scheduler startup behavior.

Fields:

- scheduler_enabled
- default_scan_limit
- tick_interval_seconds

Rules:

- scheduler must be disableable in test
- invalid scan limits must fail validation
- production defaults must be predictable

---

## 10. Feature Flags

FeatureFlagSettings defines explicit behavior toggles.

Fields:

- enable_review_persistence
- enable_feedback_learning
- enable_export_artifacts
- enable_runtime_recovery
- enable_startup_repair

Rules:

- flags must be explicit
- flags must not create invalid dependency graphs
- incompatible flag combinations must fail validation

---

## 11. Loading Rules

Settings should be loaded through a dedicated loader layer.

Order of resolution:

1. code defaults
2. environment profile defaults
3. environment variables
4. explicit test overrides

This order must be deterministic.

---

## 12. Validation Rules

Settings validation must happen before app startup completes.

Validation must verify:

- required values are present
- enum values are valid
- numeric bounds are valid
- path structure is valid
- environment isolation rules are satisfied
- enabled features are dependency-compatible

Invalid configuration must fail fast.

---

## 13. Design Constraint

Service modules must not define runtime ownership over:

- production paths
- backend selection rules
- startup policy values
- scheduler policy values
- environment-specific defaults

Those belong to the configuration system.