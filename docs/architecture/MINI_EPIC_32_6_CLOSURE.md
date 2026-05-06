# Mini-EPIC 32.6 Closure - CI Release Metadata Injection & Validation Evidence Alignment

## Status

Closed.

## Context

Mini-EPIC 32.5 introduced the release identity metadata foundation:

- `ReleaseIdentity`
- `ReleaseIdentityService`
- `GET /api/operations/release-identity`
- product-safe allow-listed release metadata
- safe fallback behavior when commit or branch metadata is missing
- default `validation_status = "not_declared"`

Mini-EPIC 32.6 connects that foundation to the CI release validation workflow without creating a release artifact, deployment, package, semantic version tag, GitHub Release, or environment promotion.

## Goal

Inject deterministic, product-safe release identity metadata during CI validation so the runtime release identity endpoint can reflect the commit and branch under validation.

The runtime must not claim release readiness. CI evidence remains the actual release gate.

## Architecture Decision

CI may inject release identity context, but not release readiness.

The workflow injects:

| Variable | Value | Reason |
|---|---|---|
| `INVOMATCH_RELEASE_COMMIT_SHA` | `${{ github.sha }}` | Exact commit under validation. |
| `INVOMATCH_RELEASE_BRANCH` | `${{ github.ref_name }}` | Branch/ref under validation. |
| `INVOMATCH_RELEASE_VALIDATION_STATUS` | `not_declared` | Explicitly prevents runtime overclaiming validation success. |

The workflow intentionally does not inject:

| Variable | Reason |
|---|---|
| `INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC` | No deterministic release build timestamp exists yet because Mini-EPIC 32.6 does not create packages, artifacts, deployments, or releases. |

## Validation Status Boundary

`validation_status` remains `not_declared` during CI validation.

This is intentional.

The runtime endpoint is allowed to report the identity of the commit and branch being validated. It is not allowed to report that the build is release-candidate-ready merely because a workflow has started.

Release readiness remains proven by external validation evidence:

- backend full validation;
- contract/API validation;
- operational validation;
- required scenario regression pack;
- frontend lint;
- frontend build.

A future release promotion or artifact packaging mini-epic may introduce a stronger validation status only after all release validation evidence is complete and captured.

## Files Changed

- `.github/workflows/ci.yml`
- `tests/test_release_identity_service.py`
- `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`
- `docs/architecture/MINI_EPIC_32_6_CLOSURE.md`

## Implementation Summary

### CI Workflow

The `release-validation` job now injects safe release identity metadata at the job environment level.

This ensures every backend validation step has access to the same bounded release identity context.

### Release Identity Test Coverage

A CI-like service-level test verifies that:

- injected commit SHA is read;
- injected branch is read;
- missing build timestamp remains `None`;
- `validation_status` remains `not_declared`;
- metadata is considered available when commit and branch are present.

### Documentation

The EPIC 32 release pipeline documentation now defines the CI metadata injection boundary and explicitly documents that CI metadata injection is not release promotion.

## Commands Executed

### Patch / Inspection

- `git status`
- `git --no-pager diff --stat`
- `git --no-pager diff -- .github/workflows/ci.yml tests/test_release_identity_service.py`
- `git diff --check`

### Targeted Release Identity + Operational Validation

- `pytest -q tests\test_release_identity_service.py tests\operational\test_operations_metrics_api.py --basetemp=.pytest_tmp\mini_epic_32_6_targeted`

### Contract/API Validation

- `pytest -q tests\contracts tests\sqlite_contract tests\test_artifact_storage_contract.py tests\test_export_artifact_repository_contract.py tests\test_run_store_core_contract.py tests\test_run_view_contract.py tests\domain\test_feedback_time_contract.py --basetemp=.pytest_tmp\mini_epic_32_6_contracts`

### Backend Full Validation

- `pytest -q tests --basetemp=.pytest_tmp\mini_epic_32_6_backend_full`

### Operational Validation

- `pytest -q tests\operational --basetemp=.pytest_tmp\mini_epic_32_6_operational`

### Scenario Regression Pack

- `pytest -q tests\system\test_happy_path_full_flow.py tests\system\test_review_resolution_flow.py tests\system\test_runtime_failure_terminalization.py tests\system\test_startup_repair_visibility_recovery_alignment.py --basetemp=.pytest_tmp\mini_epic_32_6_scenario_pack`

### Frontend Validation

- `npm run lint`
- `npm run build`

## Validation Results

| Validation | Result |
|---|---|
| `git diff --check` | Passed; no whitespace errors reported |
| Targeted release identity + operational validation | 33 passed in 58.64s |
| Contract/API validation | 47 passed in 3.92s |
| Backend full validation | 699 passed in 119.43s |
| Operational validation | 85 passed in 75.25s |
| Scenario regression pack | 4 passed in 6.04s |
| Frontend lint | Passed; eslint completed with no reported errors |
| Frontend build | Passed; `tsc -b && vite build`; 28 modules transformed; built in 376ms |

## CI Metadata Boundary

Mini-EPIC 32.6 is limited to metadata injection during validation.

It does not perform:

- Docker packaging;
- deployment;
- staging environment creation;
- production environment creation;
- semantic version tag creation;
- GitHub Release creation;
- changelog generation;
- artifact publishing;
- rollback implementation;
- environment promotion automation;
- frontend UI changes.

## Closure Criteria Review

| Closure Criteria | Status |
|---|---|
| CI metadata injection boundary is defined | Complete |
| Workflow metadata variables are safe and deterministic | Complete |
| Release identity endpoint can reflect injected metadata in validation context | Complete |
| `validation_status` does not overclaim release readiness | Complete |
| EPIC 32 documentation is updated | Complete |
| Mini-EPIC 32.6 closure document is created | Complete |
| Required validation commands pass | Complete |
| Working tree is clean | Pending final commit/push verification |
| Changes are committed and pushed | Pending final commit/push verification |

## Final Decision

Mini-EPIC 32.6 aligns release identity metadata with CI validation without crossing into release creation or deployment.

The system can identify what commit/ref is under validation, but it still relies on captured validation evidence as the real release gate.