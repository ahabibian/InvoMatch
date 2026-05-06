# EPIC 32 - DevOps & Release Pipeline

## Status

In progress.

## Context

EPIC 31 is closed.

The system now provides:

- deterministic end-to-end execution
- tenant-aware isolation
- security-hardened trust boundaries
- restart-safe persistence and recovery
- operational monitoring and visibility
- auditability and traceability
- deployment-ready runtime behavior
- usable operator-facing workflows

The system is operationally mature, but release management is still manual and fragile.

A production-grade system is not ready because it can be deployed once. It is ready when it can be deployed safely, repeatedly, and predictably.

EPIC 32 introduces release discipline, validation gates, deployment verification rules, promotion safety, rollback awareness, and release traceability without introducing unnecessary infrastructure complexity.

## Objective

Introduce a repeatable and reliable release pipeline so InvoMatch can move safely through:

development -> validation -> staging -> production

After this EPIC, the system must support:

- automated validation before release
- reproducible builds
- environment-aware deployment flow
- controlled release discipline
- deployment verification
- rollback-aware failure handling
- release traceability

## Non-Goals

EPIC 32 does not include:

- Kubernetes orchestration
- autoscaling
- multi-region deployment
- infrastructure-as-code platforms
- advanced cloud-native tooling
- enterprise CI/CD complexity

This EPIC is about reliable release execution, not infrastructure overengineering.

## Mini-EPIC 32.0 Baseline Finding

Before formalizing release gates, the backend full test baseline exposed test drift caused by newer finalized projection invariants.

Initial backend full baseline result:

8 failed, 680 passed

The failures were caused by older tests that still constructed completed runs without finalized projection stores or readable finalized projections.

This violated the current production invariant:

A completed run must have a finalized projection that can be read back safely.

The product scenario pack was already green, but the full backend test baseline was not.

Mini-EPIC 32.0 therefore included release-baseline test drift repair before documenting the release contract.

After repair:

688 passed

This confirms that the release baseline must include the full backend test pack, not only selected scenario tests.

## Release Validation Layers

Every release candidate must pass the following validation layers.

### 1. Required Scenario Regression Pack

Purpose:

Protect the most important production flows touched by release, startup, recovery, health, monitoring, and deployment behavior.

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"

    pytest -q `
      tests\system\test_happy_path_full_flow.py `
      tests\system\test_runtime_failure_terminalization.py `
      tests\system\test_restart_recovery_consistency.py `
      tests\system\test_startup_repair_visibility_recovery_alignment.py `
      tests\test_health.py `
      tests\test_health_readiness.py `
      tests\operational\test_operations_metrics_api.py `
      --basetemp=.pytest_tmp

Current baseline result:

29 passed

### 2. Operational Validation Pack

Purpose:

Validate operational metrics, health summaries, alerts, recovery loop observability, startup repair observability, scheduler behavior, condition detection, and retry/recovery policies.

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"

    pytest -q tests\operational --basetemp=.pytest_tmp

Current baseline result:

78 passed

### 3. Contract Validation Pack

Purpose:

Protect product-facing API response shapes and prevent internal field leakage.

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"

    pytest -q tests\contracts --basetemp=.pytest_tmp

Current baseline result:

10 passed

### 4. Full Backend Validation Pack

Purpose:

Validate the full backend regression baseline.

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"

    pytest -q tests --basetemp=.pytest_tmp

Current baseline result:

688 passed

### 5. Frontend Lint

Purpose:

Validate frontend source quality and static lint rules.

Command:

    cd C:\dev\InvoMatch\ui\invomatch-ui

    npm run lint

Current baseline result:

eslint completed with no reported errors.

### 6. Frontend Build

Purpose:

Validate TypeScript compilation and production bundle creation.

Command:

    cd C:\dev\InvoMatch\ui\invomatch-ui

    npm run build

Current baseline result:

tsc -b and vite build completed successfully.
Vite transformed 28 modules.
Build completed in 549ms.

## Required Scenario Mapping

| Scenario | Purpose | Test Coverage |
|---|---|---|
| Scenario 1 - Happy Path Full Flow | Validates upload/run/review/export-ready product flow | tests\system\test_happy_path_full_flow.py |
| Scenario 4 - Runtime Failure Terminalization | Validates failed runtime terminalization and blocked export readiness | tests\system\test_runtime_failure_terminalization.py |
| Scenario 6 - Restart Recovery Consistency | Validates restart-safe persisted state recovery | tests\system\test_restart_recovery_consistency.py |
| Scenario 7 - Startup Repair Visibility & Recovery Alignment | Validates startup repair, readiness, health, and recovery alignment | tests\system\test_startup_repair_visibility_recovery_alignment.py |
| Scenario 13 - Monitoring & Health Visibility Integrity | Validates health/readiness and operational monitoring surfaces | tests\test_health.py, tests\test_health_readiness.py, tests\operational\test_operations_metrics_api.py, tests\operational |

## Scenario 13 Status

Scenario 13 is currently represented by health, readiness, operational API, and operational visibility tests rather than a single dedicated system scenario file.

This is acceptable for Mini-EPIC 32.0 because the coverage exists and is release-blocking.

A later Mini-EPIC may consolidate this into a dedicated system scenario file:

tests\system\test_monitoring_health_visibility_integrity.py

## Release Gate Rules

A release candidate is valid only if all mandatory validation layers pass.

A release candidate must be rejected if:

- any required scenario regression fails
- any contract test fails
- any operational validation test fails
- the full backend test pack fails
- frontend lint fails
- frontend build fails
- environment configuration is incomplete or unsafe
- startup validation fails
- release identity cannot be traced to a commit
- deployment verification cannot confirm health/readiness

No release may be promoted based only on partial test success.

## Current Reproducibility Risk

The backend dependency model is not fully reproducible yet.

Current pyproject.toml uses unpinned dependencies:

- fastapi
- uvicorn
- pydantic
- pytest
- python-multipart

This means dependency resolution may change over time.

This is acceptable as a documented limitation for Mini-EPIC 32.0, but later EPIC 32 work must introduce dependency locking or pinned release constraints before production release discipline can be considered complete.

The frontend has npm-based installation behavior, but release packaging still needs to define deterministic install rules.

## Environment Promotion Model

The intended promotion flow is:

development -> validation -> staging -> production

Promotion rules:

1. Development may run partial checks during local work.
2. Validation must run the full release validation pack.
3. Staging must use production-like configuration without production data.
4. Production promotion must occur only after staging validation succeeds.
5. No environment may share mutable runtime state with another environment.
6. Production debug behavior must remain disabled.
7. Startup validation must pass after deployment.
8. Release identity must be recorded.

## Deployment Verification Rules

After deployment, the system must verify:

- application startup succeeds
- /health responds correctly
- /readiness responds correctly
- startup repair result is visible
- operational health summary is available to authorized admin users
- persistence paths are available
- finalized projection store is available
- recovery loop startup does not silently fail
- monitoring and operational visibility surfaces are not broken

## Rollback and Failure Handling Rules

A failed deployment must not remain hidden.

Rollback-safe behavior requires:

- failed startup prevents promotion
- invalid configuration rejects deployment
- failed migrations or persistence initialization block release
- readiness failure prevents production promotion
- operational visibility exposes failure state
- release metadata identifies the failed version
- rollback restores the last known valid release state

Mini-EPIC 32.0 documents these rules but does not yet automate rollback.

## Release Traceability Model

Every release must be traceable to:

- release version
- deployed git commit
- deployment timestamp
- target environment
- validation result
- operator or automation identity
- rollback status if applicable

This model must align with the existing audit and operational visibility direction.

## Build and Packaging Rules

Release packaging must eventually ensure:

- deterministic backend dependency installation
- deterministic frontend dependency installation
- versioned build artifacts
- stable startup behavior across environments
- explicit environment configuration
- no hidden local-only runtime assumptions

Mini-EPIC 32.0 does not implement packaging automation. It defines the validation baseline that packaging work must obey.

## Implementation Plan

### Phase 1 - Baseline Inspection

- inspect repository test surface
- identify scenario files
- identify operational tests
- identify contract tests
- inspect frontend scripts
- inspect dependency model

### Phase 2 - Test Drift Repair

- run full backend baseline
- identify release-blocking failures
- repair old tests to respect finalized projection invariants
- ensure no production invariant is weakened

### Phase 3 - Validation Baseline

- run required scenario regression pack
- run operational validation pack
- run contract validation pack
- run full backend validation pack
- run frontend lint
- run frontend build

### Phase 4 - Documentation

- document release gate rules
- document validation commands
- document scenario mapping
- document reproducibility risks
- document closure evidence

### Phase 5 - Future CI Migration

- convert manual validation pack into CI workflow
- preserve the same gates
- fail clearly on any regression
- avoid adding CI steps that are not already locally reproducible

## Test Strategy

EPIC 32 validation starts with manual PowerShell-first commands.

This is intentional.

The release contract must be clear and locally reproducible before automation is introduced.

CI should automate this contract later; it should not define the contract implicitly.

## Closure Criteria for Mini-EPIC 32.0

Mini-EPIC 32.0 is complete only if:

- EPIC 32 release pipeline architecture document exists
- release validation layers are documented
- required scenario regression pack is mapped to concrete test files
- release gate rules are documented
- environment promotion model is documented
- deployment verification rules are documented
- rollback/failure handling rules are documented
- release traceability model is documented
- current reproducibility limitations are documented
- backend full baseline passes
- operational validation passes
- contract validation passes
- frontend lint passes
- frontend build passes
- closure document is created
- all changes are committed