# Operational Visibility Closure

## Status

Closed.

This closure records the operational visibility work added after projection integrity enforcement.

## Objective

Expose admin-only operational visibility for runtime, startup repair, terminal failure, and recovery signals without exposing privileged repair execution capabilities.

## Implemented Scope

### 1. Operational Metrics API

Added:

- GET /api/operations/metrics

This endpoint exposes:

- normalized operational health status
- generated timestamp
- normalized operator-facing signals
- raw operational counters
- operational decision counts
- operational reason counts

Access is protected by:

- authentication
- authorization
- operations.view_metrics capability

### 2. Operational Health Summary API

Added:

- GET /api/operations/health-summary

This endpoint exposes:

- operational status
- generated timestamp
- human-readable summary
- normalized signals
- recommended operator action

### 3. Operational Alerts API

Added:

- GET /api/operations/alerts

This endpoint exposes machine-readable operational alerts derived from normalized operational signals.

Alert policy covers:

- startup repair failures
- unresolved startup repair mismatches
- confirmed terminal failures
- recovery automation activity

### 4. Operational Condition Detector

Added:

- src/invomatch/services/operational/condition_detector.py

Responsibilities:

- convert low-level counters into operator-facing health status
- normalize operational signals
- generate health summaries
- recommend safe operator action
- remain framework-independent and deterministic when a clock is injected

### 5. Operational Alert Policy

Added:

- src/invomatch/services/operational/alert_policy.py

Responsibilities:

- convert operational signals into structured alerts
- classify alert severity
- expose alert code, signal, value, message, and recommended action
- remain framework-independent and deterministic when a clock is injected

### 6. Application Wiring

Updated:

- src/invomatch/main.py

Application state now exposes:

- operational_metrics_store
- operational_metrics_service
- operational_condition_detector
- operational_alert_policy

The operations router is registered in the FastAPI app.

### 7. Security Documentation Alignment

Updated:

- docs/architecture/ENDPOINT_PROTECTION_MAP.md
- docs/architecture/AUTHORIZATION_RULE_MATRIX.md

The documentation now explicitly records that:

- operational visibility routes are exposed under /api/operations
- operations.view_metrics protects metrics, health-summary, and alerts
- the capability is read-only
- it does not grant recovery execution, startup repair execution, restart repair execution, or admin configuration permission
- current access is admin-only

## Validation Evidence

Executed command:

cd C:\dev\InvoMatch
$env:PYTHONPATH = "src"

pytest -q `
  tests\test_health_readiness.py `
  tests\audit\test_audit_api.py `
  tests\test_startup_repair_app_wiring.py `
  tests\operational `
  tests\system\test_startup_repair_visibility_recovery_alignment.py `
  --basetemp=.pytest_tmp

Result:

81 passed in 19.81s

## Commits

Implementation commits:

- 7284c09 feat: add operational metrics visibility API
- f88f7f4 feat: add operational alert visibility policy

Documentation commit:

- 28e28be docs: document operational visibility endpoint protection

## Final Assessment

Operational visibility is now productized enough for the current backend architecture layer.

The system does not merely collect operational data internally. It now exposes protected, admin-only read surfaces that translate raw operational counters into usable operator-facing status, summaries, and alerts.

This is not a cosmetic change. It closes an important SaaS-readiness gap:

- operators can inspect system condition
- security boundaries protect operational visibility
- alert semantics are explicit and test-covered
- operational read surfaces are separated from privileged repair execution

## Remaining Out of Scope

The following are intentionally not implemented in this closure:

- executing recovery from API
- executing startup repair from API
- dashboard UI rendering
- persistent external metrics backend
- Prometheus/OpenTelemetry integration
- notification delivery
- alert acknowledgement lifecycle

These should be handled in later EPICs.
