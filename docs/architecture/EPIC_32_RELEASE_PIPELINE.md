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


---

## Release Identity and Version Metadata Foundation

Mini-EPIC 32.5 introduces the first minimal release identity foundation for InvoMatch.

This foundation does not create a public release, deployment, tag, package, artifact, staging promotion, production promotion, changelog, or rollback implementation.

Its purpose is narrower and stricter:

- every future validated release candidate must be traceable to a stable runtime identity;
- runtime identity must be product-safe and operationally visible;
- missing release metadata must be explicit instead of silently fabricated;
- release validation status must not be claimed by runtime unless release tooling explicitly provides it.

### Release Identity Model

The release identity model contains the following fields:

| Field | Meaning |
|---|---|
| `application_name` | Stable application identifier. Current default: `invomatch`. |
| `application_version` | Application/internal release version. Current default: `0.1.0` from the backend project baseline. |
| `git_commit_sha` | Commit SHA associated with the runtime when provided by release/build tooling. Falls back to `unknown`. |
| `git_branch` | Branch or ref associated with the runtime when provided by release/build tooling. Falls back to `unknown`. |
| `build_timestamp_utc` | UTC build timestamp when provided by release/build tooling. Falls back to `null`. |
| `environment` | Configured InvoMatch runtime environment. |
| `validation_status` | Explicit validation status from release tooling. Falls back to `not_declared`. |
| `metadata_available` | `true` only when concrete commit and branch metadata are both available. |

### Runtime Boundary

Release identity is exposed as operational metadata through:

    GET /api/operations/release-identity

This endpoint is protected by the existing operational permission boundary:

    operations.view_metrics

The endpoint is intentionally placed under `/api/operations` instead of `/health` or `/readiness`.

Health and readiness endpoints must remain runtime state checks. They must not become release audit surfaces.

### Environment Variable Boundary

The release identity service reads only the following allow-listed environment variables:

| Environment Variable | Purpose |
|---|---|
| `INVOMATCH_APPLICATION_NAME` | Optional application name override. |
| `INVOMATCH_APPLICATION_VERSION` | Optional application version override. |
| `INVOMATCH_RELEASE_COMMIT_SHA` | Optional release/build commit SHA. |
| `INVOMATCH_RELEASE_BRANCH` | Optional release/build branch or ref. |
| `INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC` | Optional UTC build timestamp. |
| `INVOMATCH_RELEASE_VALIDATION_STATUS` | Optional validation status explicitly injected by release tooling. |

No arbitrary environment variables are exposed.

Secrets, token configuration, persistence paths, storage paths, seed token JSON, and CI internals must not appear in release identity output.

### Validation Status Boundary

`validation_status` is not proof that CI passed unless release tooling explicitly injects a value after validation.

The default value is:

    not_declared

This is intentional.

Runtime must not infer release-candidate readiness merely because the application starts, health passes, readiness passes, or local tests previously passed.

A release-candidate-ready decision still requires the release validation pack and GitHub Actions evidence defined elsewhere in this document.

### Missing Metadata Behavior

When release metadata is absent, the service must fall back safely:

| Missing Input | Runtime Output |
|---|---|
| missing commit SHA | `git_commit_sha = "unknown"` |
| missing branch/ref | `git_branch = "unknown"` |
| missing build timestamp | `build_timestamp_utc = null` |
| missing validation status | `validation_status = "not_declared"` |
| missing commit or branch | `metadata_available = false` |

This prevents the system from lying about release traceability.

### Non-Goals

Mini-EPIC 32.5 does not introduce:

- Docker packaging
- deployment
- staging environment
- production environment
- semantic version tag creation
- GitHub Release creation
- changelog generation
- artifact publishing
- rollback implementation
- environment promotion automation
- CI matrix expansion
- frontend UI changes
- release validation gate changes

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

## CI Release-Gate Evidence Model

EPIC 32 treats GitHub Actions CI validation as release-gate evidence, not merely as a convenience check.

A green CI run means that the configured release validation baseline passed on a specific commit. A red CI run blocks release-related closure until the failure is understood, repaired if necessary, and followed by a final passing CI run.

### Release-Blocking CI Steps

The following CI steps are release-blocking:

| CI Step | Release-Gate Meaning |
|---|---|
| Backend full test baseline | Backend regression surface must pass on GitHub Actions. |
| Contract tests | API and boundary contracts must remain stable. |
| Operational tests | Operational visibility and repair behavior must remain valid. |
| Required scenario regression pack | Critical end-to-end product scenarios must remain valid. |
| Frontend lint | Frontend code must pass configured lint rules. |
| Frontend build | Frontend production build must compile successfully. |

Any failed release-blocking step blocks release closure.

Warnings do not block release closure unless they affect runtime behavior, security, future compatibility, deployment safety, validation reliability, or evidence trustworthiness.

### Required CI Evidence For Release-Related EPIC Closure

Release-related EPIC closure must capture:

| Evidence Field | Required |
|---|---|
| Workflow name | Yes |
| GitHub Actions run number | Yes |
| Commit SHA | Yes |
| Branch | Yes |
| Status | Yes |
| Duration | Yes, if available |
| Failed step | Required for failed runs |
| Failure reason | Required for failed runs |
| Repair commit | Required if a repair was made |
| Final passing run | Required after any failed run |
| Local validation command(s) | Required when local validation is used as supporting evidence |
| CI/local drift note | Required if CI and local behavior differed |

### Mini-EPIC 32.1 CI Evidence Captured

| Evidence | Value |
|---|---|
| Initial CI run | #153 |
| Initial commit | 9ddc8b0 |
| Initial status | Failed |
| Failure reason | Missing `.pytest_tmp` parent directory on a clean GitHub Actions runner. |
| Release-gate result | Blocked until repaired. |
| Repair commit | 6e0cce0 |
| Repair commit message | ci: prepare pytest temp root in validation workflow |
| Final CI run | #154 |
| Final commit | 6e0cce0 |
| Final status | Passed |
| Release-gate result | CI validation baseline became usable as release evidence. |

### CI/Local Drift Rule

If local validation passes but CI fails, CI is treated as the release-gate source of truth for closure.

The drift must be investigated, repaired, committed, pushed, and validated by a final passing GitHub Actions run before release-related closure.

---

## Release Candidate Validation Pack

A commit may be considered **release-candidate-ready** only after both local validation and GitHub Actions validation evidence have been reviewed and recorded.

Release-candidate-ready does not mean deployed, packaged, tagged, published, promoted to staging, or promoted to production. It only means the commit has passed the agreed validation gate and is eligible for a later release/deployment process.

### Required Local Validation Pack

The local validation pack must be run from a clean working tree unless the operator is explicitly validating uncommitted documentation changes before commit.

Required commands:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q --basetemp=.pytest_tmp

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\contracts --basetemp=.pytest_tmp

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\operational --basetemp=.pytest_tmp

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\system\test_happy_path_full_flow.py tests\system\test_review_resolution_flow.py tests\system\test_runtime_failure_terminalization.py tests\system\test_startup_repair_visibility_recovery_alignment.py --basetemp=.pytest_tmp

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run lint
    npm run build

If a listed test directory does not exist in the current repository state, the operator must record that fact explicitly instead of silently skipping the validation category. The current repository contract validation path is tests\contracts.

### Required Local Evidence

For each local validation command, the release candidate evidence must include:

- command
- result
- pass/fail status
- test count or build/lint result when available
- failure summary if failed
- repair commit if a repair was needed
- final passing command result after repair

### Required GitHub Actions Evidence

The GitHub Actions validation evidence must include:

- workflow name
- run number
- commit SHA
- branch
- status
- failed step, if any
- repair commit, if any
- final passing run number
- final passing commit SHA

A red GitHub Actions run blocks release-candidate readiness. A later local pass does not override a red CI run. The defect or drift must be repaired, pushed, and validated again by GitHub Actions.

### Manual Release Candidate Checklist

Before declaring a commit release-candidate-ready, the operator must confirm:

| Check | Required Evidence |
|---|---|
| Working tree clean before final validation | `git status` output |
| Branch aligned with origin | `git status` output |
| Backend full test baseline passed | `pytest -q --basetemp=.pytest_tmp` result |
| Contract/API validation passed or absence recorded | command result |
| Operational validation passed | `pytest -q tests\operational --basetemp=.pytest_tmp` result |
| Scenario regression pack passed | listed system test command result |
| Frontend lint passed | `npm run lint` result |
| Frontend build passed | `npm run build` result |
| GitHub Actions run reviewed | workflow name, run number, commit SHA, branch, status |
| Any red CI run repaired | repair commit and final passing run |
| Release-candidate-ready is not described as deployed/released | documentation wording review |
| Closure document created | Mini-EPIC closure file path |
| Documentation committed | commit SHA |
| Documentation pushed | `git push origin main` result |

### Release Candidate Boundary

The following states are explicitly outside release-candidate validation:

- deployed
- packaged
- Dockerized
- tagged
- published
- promoted to staging
- promoted to production
- rollback-ready
- changelog-published

Those activities require later EPIC 32 mini-epics or a dedicated release/deployment epic.

## Mini-EPIC 32.6 - CI Release Metadata Injection Boundary

Mini-EPIC 32.6 connects the release identity metadata foundation to the CI validation workflow without creating a release, tag, package, deployment, or promotion mechanism.

### CI Metadata Injection

The CI validation workflow may inject only bounded, product-safe release identity metadata:

| Environment variable | CI value | Purpose |
|---|---|---|
| `INVOMATCH_RELEASE_COMMIT_SHA` | `${{ github.sha }}` | Identifies the exact commit being validated. |
| `INVOMATCH_RELEASE_BRANCH` | `${{ github.ref_name }}` | Identifies the branch or ref name under validation. |
| `INVOMATCH_RELEASE_VALIDATION_STATUS` | `not_declared` | Prevents runtime from claiming release readiness. |

### Intentionally Not Injected

`INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC` is intentionally not injected by the current CI workflow.

The current workflow does not provide a deterministic UTC build timestamp value that should be treated as release identity. A future release packaging or artifact creation step may inject a real build timestamp when packaging exists.

### Validation Status Boundary

Runtime release identity must not claim that a build is release-candidate-ready merely because CI is currently running.

`validation_status` remains `not_declared` during CI validation. The actual release gate remains the external CI evidence:

- backend full validation;
- contract/API validation;
- operational validation;
- required scenario regression pack;
- frontend lint;
- frontend build.

A future release promotion step may set a stronger validation status only after validation evidence has completed and been captured. Mini-EPIC 32.6 does not add that promotion step.

### Non-Release Boundary

Mini-EPIC 32.6 does not create or modify:

- semantic version tags;
- GitHub Releases;
- Docker images;
- release packages;
- deployment environments;
- staging or production promotion;
- changelog generation;
- rollback automation;
- frontend release UI.

## Mini-EPIC 32.7 - Release Candidate Evidence Index & Validation Run Traceability

Mini-EPIC 32.7 defines a documentation-first release candidate evidence index boundary.

The purpose is to record which validation evidence belongs to a given release candidate validation run without creating a package, deployment, semantic version tag, GitHub Release, public artifact, promotion event, rollback point, changelog, or runtime release registry.

### Architecture Decision

Release candidate validation evidence is represented as a documentation artifact.

The evidence index records:

- commit SHA
- branch/ref
- validation date/time as documented evidence
- validation source (`local`, `ci`, `mixed`, or `documented`)
- validation command groups
- result summaries
- related closure documents
- related evidence files or logs

The validation date/time is not runtime truth.

It is not a build timestamp unless a future build process explicitly produces it.

The evidence index does not claim production release readiness.

### Evidence Index Boundary

The format is defined in:

    docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md

Recommended future index location:

    docs/architecture/evidence/release_candidates/

Recommended future naming pattern:

    RC_EVIDENCE_INDEX_<YYYYMMDD>_<short_commit_sha>.md

### Non-Release Boundary

Mini-EPIC 32.7 intentionally does not introduce:

- Docker packaging
- deployment
- staging environment
- production environment
- semantic version tag creation
- GitHub Release creation
- changelog generation
- artifact publishing
- rollback implementation
- environment promotion automation
- frontend UI changes
- runtime release registry
- database persistence for release evidence

### Relationship To Prior Mini-EPICs

Mini-EPIC 32.5 introduced bounded runtime release identity metadata.

Mini-EPIC 32.6 allowed CI validation jobs to inject safe release identity metadata.

Mini-EPIC 32.7 keeps validation evidence traceability separate from runtime identity and release publication.

This preserves a clean boundary:

    runtime release identity != validation evidence index != release publication
