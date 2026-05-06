# Mini-EPIC 32.5 Closure - Release Identity & Version Metadata Foundation

## Status

Implementation complete. Final commit/push validation pending at the time this closure document is created.

## Context

Mini-EPIC 32.4 executed the first release-candidate dry run and captured evidence for the release validation process.

That dry run confirmed that release-candidate readiness must be traceable to a concrete commit and validation record.

However, before Mini-EPIC 32.5, InvoMatch did not have a runtime release identity model. The project metadata existed in `pyproject.toml`, and release evidence existed in documentation, but the backend runtime did not expose a bounded, deterministic release identity surface.

Mini-EPIC 32.5 closes that gap without introducing deployment, packaging, tagging, publishing, promotion, or rollback implementation.

## Goal

Introduce a minimal, deterministic release identity and version metadata foundation so every future validated release candidate can be traced to a concrete commit and version identity.

The objective is not to create a public release.

The objective is to define and expose release identity metadata consistently and safely so future packaging, staging, production promotion, rollback, and audit work can reference a stable release identity.

## Non-Goals

Mini-EPIC 32.5 did not introduce:

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

## Confirmed Starting State

Before implementation:

- Branch: `main`
- Working tree: clean
- Branch aligned with `origin/main`
- Latest confirmed commit:
  - `df5b255 docs: capture first release candidate dry run evidence`
- Previous repair commit:
  - `6cb5493 docs: repair release candidate contract validation path`
- Backend project metadata:
  - `pyproject.toml`
  - project name: `invomatch`
  - version: `0.1.0`
- Frontend project metadata:
  - `ui/invomatch-ui/package.json`
  - package name: `invomatch-ui`
  - version: `0.0.0`
- Existing operational endpoints:
  - `GET /api/operations/metrics`
  - `GET /api/operations/health-summary`
  - `GET /api/operations/alerts`
- Existing public runtime endpoints:
  - `GET /health`
  - `GET /readiness`
- Existing operational permission:
  - `operations.view_metrics`

## Architecture Decision

Release identity is treated as operational metadata, not product business data and not public health/readiness state.

The selected implementation boundary is:

    GET /api/operations/release-identity

The endpoint is protected by the existing permission:

    operations.view_metrics

No new permission was introduced.

This is intentional. Release identity is operational visibility metadata and fits the existing admin/operations surface. Adding a new permission would create unnecessary security-contract churn without improving the boundary for this stage.

## Release Identity Model

The release identity model contains:

| Field | Description |
|---|---|
| `application_name` | Stable application identifier. |
| `application_version` | Application/internal release version. |
| `git_commit_sha` | Commit SHA associated with the runtime, or `unknown`. |
| `git_branch` | Branch/ref associated with the runtime, or `unknown`. |
| `build_timestamp_utc` | UTC build timestamp when provided, or `null`. |
| `environment` | Configured InvoMatch runtime environment. |
| `validation_status` | Explicit validation status from release tooling, or `not_declared`. |
| `metadata_available` | `true` only when commit and branch metadata are both present. |

## Runtime Safety Boundary

The release identity service reads only an explicit allow-list of environment variables:

| Environment Variable | Purpose |
|---|---|
| `INVOMATCH_APPLICATION_NAME` | Optional application name override. |
| `INVOMATCH_APPLICATION_VERSION` | Optional application version override. |
| `INVOMATCH_RELEASE_COMMIT_SHA` | Optional release/build commit SHA. |
| `INVOMATCH_RELEASE_BRANCH` | Optional release/build branch or ref. |
| `INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC` | Optional UTC build timestamp. |
| `INVOMATCH_RELEASE_VALIDATION_STATUS` | Optional validation status from release tooling. |

The implementation does not expose arbitrary environment variables.

The endpoint must not expose:

- security seed token JSON
- bearer tokens
- secrets
- persistence paths
- storage paths
- CI internals
- arbitrary environment data

## Validation Status Boundary

The runtime does not infer validation success.

The default validation status is:

    not_declared

This prevents the system from claiming release-candidate readiness simply because the application started or because tests passed in a previous local or CI run.

Release-candidate-ready remains a documentation/evidence decision governed by the EPIC 32 validation pack and GitHub Actions evidence.

## Health and Readiness Boundary

Mini-EPIC 32.5 intentionally did not add release identity fields to:

- `GET /health`
- `GET /readiness`

Those endpoints remain runtime health/readiness surfaces.

Release identity belongs to the protected operational API surface.

## Files Changed

Implementation files:

- `.env.example`
- `src/invomatch/domain/release_identity.py`
- `src/invomatch/services/release_identity_service.py`
- `src/invomatch/api/operations_models.py`
- `src/invomatch/api/operations.py`
- `src/invomatch/main.py`

Test files:

- `tests/test_release_identity_service.py`
- `tests/operational/test_operations_metrics_api.py`

Documentation files:

- `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`
- `docs/architecture/MINI_EPIC_32_5_CLOSURE.md`

## Implementation Summary

Added a release identity domain model:

- `ReleaseIdentity`
- safe default constants:
  - `invomatch`
  - `0.1.0`
  - `unknown`
  - `not_declared`

Added `ReleaseIdentityService`:

- reads only explicit release metadata environment variables;
- trims blank values;
- safely falls back when metadata is absent;
- computes `metadata_available` only when commit and branch are both concrete;
- avoids leaking unrelated environment data.

Added operational response model:

- `OperationalReleaseIdentityResponse`

Added operational endpoint:

    GET /api/operations/release-identity

The endpoint:

- requires authentication;
- requires `operations.view_metrics`;
- returns release identity metadata;
- returns HTTP 500 if the service is not configured;
- uses a stable typed OpenAPI response model.

Wired service into application state:

    app.state.release_identity_service

Updated `.env.example` with optional release metadata variables.

## Tests Added

Added service-level tests for:

- safe fallback when metadata is missing;
- explicit metadata loading from allow-listed environment variables;
- constructor override behavior;
- non-leakage of unrelated environment data.

Added operational API tests for:

- authentication requirement;
- viewer role rejection;
- admin access;
- safe fallback metadata shape;
- explicit metadata output;
- non-leakage of unrelated secret-like environment data;
- service missing behavior;
- stable response shape;
- typed OpenAPI response contract.

Existing health/readiness tests remain unchanged and confirm that release identity was not mixed into public health/readiness behavior.

## Targeted Validation Evidence

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q `
      tests\test_release_identity_service.py `
      tests\operational\test_operations_metrics_api.py `
      tests\test_health_readiness.py `
      --basetemp=.pytest_tmp\mini_epic_32_5_targeted

Result:

    34 passed in 60.79s

## Full Validation Evidence

### Backend Full Validation

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests --basetemp=.pytest_tmp\mini_epic_32_5_backend_full

Result:

    698 passed in 118.66s

### Contract/API Validation

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q `
      tests\contracts `
      tests\sqlite_contract `
      tests\test_artifact_storage_contract.py `
      tests\test_export_artifact_repository_contract.py `
      tests\test_run_store_core_contract.py `
      tests\test_run_view_contract.py `
      tests\domain\test_feedback_time_contract.py `
      --basetemp=.pytest_tmp\mini_epic_32_5_contracts

Result:

    47 passed in 4.27s

### Operational Validation

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\operational --basetemp=.pytest_tmp\mini_epic_32_5_operational

Result:

    85 passed in 55.03s

### Scenario Regression Pack

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q `
      tests\system\test_happy_path_full_flow.py `
      tests\system\test_review_resolution_flow.py `
      tests\system\test_runtime_failure_terminalization.py `
      tests\system\test_startup_repair_visibility_recovery_alignment.py `
      --basetemp=.pytest_tmp\mini_epic_32_5_scenario_pack

Result:

    4 passed in 5.01s

### Frontend Lint

Command:

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run lint

Result:

    eslint completed with no reported errors.

### Frontend Build

Command:

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run build

Result:

    tsc -b and vite build completed successfully.
    Vite transformed 28 modules and built successfully in 590ms.

## Closure Criteria Review

| Closure Criteria | Status |
|---|---|
| Release identity model is defined | Complete |
| Implementation boundary is explicit | Complete |
| Release metadata is deterministic or safely absent | Complete |
| Tests cover release metadata behavior | Complete |
| No sensitive information is exposed | Covered by tests and allow-list design |
| EPIC 32 documentation is updated | Complete |
| Mini-EPIC 32.5 closure document is created | Complete |
| Required validation commands pass | Complete |
| Working tree is clean | Pending commit/push |
| Changes are committed and pushed | Pending |

## Release Boundary Statement

Mini-EPIC 32.5 creates release identity infrastructure only.

It does not create a release.

It does not make the current commit deployed, packaged, tagged, published, promoted to staging, promoted to production, rollback-ready, or changelog-published.

It gives future release work a stable metadata foundation.

## Final Decision

Mini-EPIC 32.5 is implementation-complete. Full validation passed.

Final closure requires:

1. full validation results recorded,
2. commit created,
3. push completed,
4. final clean working tree confirmed.