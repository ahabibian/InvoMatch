# EPIC 24 — Deployment Environment, Configuration Architecture & Environment Isolation

## 1. Objective

The objective of EPIC 24 is to make InvoMatch deployable across multiple environments with deterministic, validated, and centralized runtime configuration.

The platform must support:

- local development
- isolated test execution
- staging deployment
- production deployment
- Docker-based packaging

without requiring manual code changes or scattered startup overrides.

The system must behave consistently across environments while still allowing safe environment-specific differences.

---

## 2. Problem Statement

The current platform contains several production weaknesses:

- storage paths are partially hardcoded
- runtime defaults are scattered across service modules
- lease values and retry settings are not centrally managed
- dependency creation is performed directly inside startup code
- environment selection is implicit
- startup validation is incomplete
- relative output paths are used directly in runtime code
- Docker packaging boundaries are not formally defined

This creates several risks:

- environment drift
- accidental path overlap between test/local/prod
- unsafe startup behavior
- inconsistent runtime defaults
- difficult deployment reproducibility
- fragile main.py wiring
- future scaling limitations

EPIC 24 addresses these risks by introducing a formal configuration and environment model.

---

## 3. Architecture Goals

The system must provide:

- centralized runtime configuration
- typed and validated settings
- deterministic environment selection
- safe environment-specific defaults
- centralized dependency construction
- deterministic startup initialization
- fail-fast startup validation
- reproducible Docker packaging
- isolated storage and persistence paths
- explicit runtime feature toggles where necessary

---

## 4. Configuration Architecture

A dedicated configuration module will be introduced.

Proposed structure:

src/invomatch/config/

- __init__.py
- settings.py
- models.py
- defaults.py
- environment.py
- validation.py
- loaders.py

The configuration layer becomes the single source of truth for all runtime configuration.

No service module should directly define production runtime paths, lease values, retry budgets, or backend selection rules.

---

## 5. Configuration Model

A root ApplicationSettings model will be introduced.

ApplicationSettings

- environment
- persistence
- storage
- runtime
- recovery
- observability
- upload
- scheduler
- feature_flags

### PersistenceSettings

Responsible for persistence backend selection and persistence path configuration.

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

### StorageSettings

Responsible for filesystem-based storage.

Fields:

- artifact_root_path
- export_directory
- temp_directory
- log_directory

### RuntimeSettings

Responsible for execution lifecycle settings.

Fields:

- lease_seconds
- retry_budget
- recovery_scan_interval_seconds
- stuck_run_timeout_seconds
- scheduler_enabled
- startup_repair_enabled
- startup_validation_enabled

### ObservabilitySettings

Fields:

- log_level
- structured_logging_enabled
- metrics_enabled
- runtime_event_logging_enabled

### UploadSettings

Fields:

- upload_root_path
- upload_max_file_size_mb
- upload_temp_retention_hours

### FeatureFlagSettings

Fields:

- enable_review_persistence
- enable_feedback_learning
- enable_export_artifacts
- enable_runtime_recovery
- enable_startup_repair

---

## 6. Environment Profiles

The system must support the following environments:

- local
- development
- test
- staging
- production

Each environment profile must define deterministic defaults.

### Local

- local file storage allowed
- sqlite allowed
- relative paths allowed
- verbose logging allowed
- scheduler optional
- startup repair optional

### Development

- sqlite allowed
- environment-isolated directories required
- scheduler optional
- startup repair enabled by default
- debug logging allowed

### Test

- temporary directories only
- isolated sqlite files only
- deterministic clock support allowed
- scheduler disabled
- startup repair optional
- aggressive cleanup rules enabled

### Staging

- scheduler enabled
- startup repair enabled
- debug disabled
- isolated persistence directories required
- isolated artifact directories required

### Production

- scheduler enabled
- startup repair enabled
- debug disabled
- fail-fast startup validation required
- no relative output paths allowed
- no shared local persistence paths allowed
- no unsafe temp directory usage allowed
- structured logging enabled by default

---

## 7. Environment Isolation Rules

Environment isolation is mandatory.

Each environment must use separate paths for:

- run persistence
- review persistence
- feedback persistence
- match record persistence
- export artifacts
- uploads
- temp files
- logs

Example:

local
- output/local/

development
- output/development/

test
- output/test/

staging
- output/staging/

production
- /var/lib/invomatch/
- /var/log/invomatch/
- /tmp/invomatch/

No environment may reuse another environment's persistence path.

---

## 8. Dependency Construction Rules

Direct dependency creation inside service modules must be minimized.

The following startup factories will be introduced:

src/invomatch/bootstrap/

- app_factory.py
- persistence_factory.py
- storage_factory.py
- runtime_factory.py
- validation_factory.py

main.py should become a thin startup boundary.

Example flow:

1. Load settings
2. Validate settings
3. Build persistence dependencies
4. Build storage dependencies
5. Build runtime dependencies
6. Run startup validation
7. Start repair coordination if enabled
8. Create app
9. Register routes
10. Start scheduler if enabled

No runtime-critical dependency should be created directly inside unrelated service modules.

---

## 9. Startup Validation Model

Startup validation must run before the application becomes available.

Validation must verify:

- persistence directories exist or can be created
- configured sqlite paths are writable
- storage directories are writable
- temp directories exist
- required backends are supported
- retry and lease values are valid
- scheduler settings are valid
- startup repair configuration is compatible
- environment profile is valid

Validation result model:

StartupValidationResult

- is_valid
- errors
- warnings
- selected_environment
- resolved_paths
- enabled_features

If validation fails, startup must fail immediately and clearly.

Partial startup is not allowed.

---

## 10. Docker Packaging Model

A minimal Docker packaging boundary will be introduced.

Required files:

- Dockerfile
- .dockerignore
- .env.example

The Docker image must:

- use deterministic dependency installation
- use explicit working directories
- expose environment selection through environment variables
- use production-safe defaults
- support mounted persistence volumes

Example runtime directories inside container:

- /app/data
- /app/storage
- /app/logs
- /app/tmp

Docker must not rely on implicit relative output directories.

---

## 11. Production-Safe Defaults

Production must enforce safe runtime defaults.

Required defaults:

- debug disabled
- scheduler enabled
- startup validation enabled
- startup repair enabled
- structured logging enabled
- relative output paths disallowed
- temp cleanup enabled
- retry budget bounded
- lease duration bounded
- storage directories isolated

---

## 12. Test Strategy

New tests must cover:

### Configuration Tests

- settings loading
- environment selection
- invalid configuration rejection
- missing required configuration handling
- production-safe default enforcement

### Factory Tests

- persistence factory
- storage factory
- runtime factory
- startup validation factory

### Startup Tests

- startup validation success
- startup validation failure
- missing directory behavior
- invalid sqlite path behavior
- invalid environment behavior
- scheduler enable/disable behavior
- startup repair enable/disable behavior

### Environment Isolation Tests

- separate paths across environments
- no accidental shared persistence
- no accidental shared storage
- test environment cleanup behavior

### Regression Scenario Re-Runs

The following permanent scenarios must be re-run:

- Scenario 1 — Happy Path Full Flow
- Scenario 4 — Runtime Failure Terminalization
- Scenario 6 — Restart Recovery Consistency
- Scenario 7 — Startup Repair Visibility & Recovery Alignment

---

## 13. Deliverables

Required documentation:

- EPIC_24_DEPLOYMENT_ENVIRONMENT.md
- CONFIGURATION_MODEL.md
- ENVIRONMENT_PROFILE_RULES.md
- STARTUP_VALIDATION_POLICY.md
- DOCKER_PACKAGING_GUIDE.md
- DEPLOYMENT_CHECKLIST.md
- EPIC_24_IMPLEMENTATION_PLAN.md
- EPIC_24_TEST_STRATEGY.md

Required implementation:

- centralized config layer
- environment model
- dependency factories
- startup validation
- environment-isolated paths
- Docker packaging files
- production-safe defaults
- deployment-oriented tests

---

## 14. Closure Criteria

EPIC 24 is complete only if:

- configuration is centralized
- environment selection is deterministic
- environment isolation is enforced
- dependency wiring is centralized
- startup validation is fail-fast
- Docker packaging works
- production-safe defaults are enforced
- deployment documentation is complete
- required regression scenarios remain green