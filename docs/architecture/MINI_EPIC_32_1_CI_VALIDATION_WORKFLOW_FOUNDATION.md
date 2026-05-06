# Mini-EPIC 32.1 - CI Validation Workflow Foundation

## Status

Implemented pending CI re-run after GitHub runner temp-root repair.

## Context

Mini-EPIC 32.0 established the EPIC 32 release validation contract manually and repaired release-blocking test drift.

Mini-EPIC 32.1 moves that validation contract into GitHub Actions without changing its meaning and without introducing deployment automation.

This mini-epic is intentionally limited to CI validation. It does not introduce staging, production deployment, rollback automation, Docker packaging, release artifact publishing, environment promotion, or cloud infrastructure.

## Objective

Create the first CI validation foundation for InvoMatch so the EPIC 32 release baseline runs automatically on every relevant repository change.

The workflow must execute the agreed release validation layers in a deterministic order and fail clearly when regressions occur.

## Implemented Workflow

Workflow file:

- .github/workflows/ci.yml

Workflow name:

- CI Validation

Workflow trigger:

- push to main
- pull request targeting main

Workflow job:

- release-validation

Runner:

- ubuntu-latest

Environment:

- PYTHONPATH=src

## Existing Repository CI State

Before this mini-epic, the repository already contained:

- .github/workflows/ci.yml

Mini-EPIC 32.1 updates this workflow to represent the EPIC 32 release validation contract more explicitly.

## Explicit Setup Steps

The CI workflow uses explicit setup and validation steps:

1. Checkout repository
2. Set up Python
3. Install backend dependencies
4. Prepare pytest temp root
5. Run backend full test baseline
6. Run contract tests
7. Run operational tests
8. Run required scenario regression pack
9. Set up Node
10. Install frontend dependencies
11. Run frontend lint
12. Run frontend build

This structure makes failures visible at the correct release validation layer instead of hiding all failures behind one generic command.

## Backend Validation Layers

### 1. Backend Full Test Baseline

The backend full baseline is represented in CI with:

pytest -q tests --basetemp=.pytest_tmp/backend_full

Local validation result observed during this mini-epic:

- 688 passed

### 2. Contract Tests

The explicit executable contract validation layer includes:

- tests/contracts
- tests/sqlite_contract
- tests/test_artifact_storage_contract.py
- tests/test_export_artifact_repository_contract.py
- tests/test_run_store_core_contract.py
- tests/test_run_view_contract.py
- tests/domain/test_feedback_time_contract.py

The CI command is:

pytest -q tests/contracts tests/sqlite_contract tests/test_artifact_storage_contract.py tests/test_export_artifact_repository_contract.py tests/test_run_store_core_contract.py tests/test_run_view_contract.py tests/domain/test_feedback_time_contract.py --basetemp=.pytest_tmp/contracts

Important note:

- tests/test_run_store_contract.py is intentionally not executed directly in this CI layer.
- That file is a backend-implementation contract template requiring a concrete RunStore fixture.
- Direct execution raises NotImplementedError by design.
- The concrete executable implementation coverage is represented through tests/sqlite_contract and related executable store contract tests.

This correction preserves the contract meaning while preventing CI from executing an abstract contract template as if it were a concrete test suite.

### 3. Operational Tests

The operational validation layer is represented in CI with:

pytest -q tests/operational --basetemp=.pytest_tmp/operational

Local validation result observed during this mini-epic:

- 78 passed

This preserves the operational visibility and reliability validation layer established before EPIC 32.

### 4. Required Scenario Regression Pack

The required scenario regression pack is explicitly represented in CI.

Included scenario files:

- tests/system/test_happy_path_full_flow.py
- tests/system/test_review_resolution_flow.py
- tests/system/test_runtime_failure_terminalization.py
- tests/system/test_startup_repair_visibility_recovery_alignment.py

The CI command is:

pytest -q tests/system/test_happy_path_full_flow.py tests/system/test_review_resolution_flow.py tests/system/test_runtime_failure_terminalization.py tests/system/test_startup_repair_visibility_recovery_alignment.py --basetemp=.pytest_tmp/scenario_pack

Local validation result observed during this mini-epic:

- 4 passed

This protects the release-critical product flow and restart/failure behavior.

## Frontend Validation Layers

Frontend working directory:

- ui/invomatch-ui

Frontend dependency installation:

npm ci

Frontend lint:

npm run lint

Frontend production build:

npm run build

Local validation result observed during this mini-epic:

- npm run lint completed with no reported errors
- npm run build completed successfully
- Vite transformed 28 modules and built successfully

The CI workflow validates that the frontend remains buildable and lint-clean before changes are accepted into the release baseline.


## GitHub Actions Drift Repair

The first GitHub Actions run for commit 9ddc8b0 failed during the backend full baseline.

Failure:

- Backend full baseline failed before validating product behavior.
- The error was FileNotFoundError for .pytest_tmp/backend_full.
- The GitHub runner starts from a clean workspace where .pytest_tmp does not exist.
- Local validation had passed because .pytest_tmp already existed locally from previous test runs.

Correction:

- Added an explicit Prepare pytest temp root step before pytest execution.
- The step runs mkdir -p .pytest_tmp.
- This preserves the validation contract and only repairs CI workspace preparation.

This is a CI environment preparation fix, not a product code change and not a weakening of the validation baseline.
## Failure Clarity

Each release validation layer is represented as a separate GitHub Actions step:

- Backend full test baseline
- Contract tests
- Operational tests
- Required scenario regression pack
- Frontend lint
- Frontend build

This is intentional.

The goal of Mini-EPIC 32.1 is not to optimize runtime. The goal is to make release validation deterministic, visible, and trustworthy.

If one layer fails, GitHub Actions should show which release gate failed.

## Non-Goals

Mini-EPIC 32.1 does not include:

- staging deployment
- production deployment
- rollback automation
- Docker packaging
- release artifact publishing
- environment promotion
- cloud infrastructure
- test parallelization
- release artifact signing
- version tagging
- automatic release notes

Those belong to later release-pipeline work, not this CI foundation.

## Local Validation Commands

The local backend validation command set mirrors the CI validation layers.

Backend full baseline:

pytest -q tests --basetemp=.pytest_tmp\backend_full

Contract tests:

pytest -q tests\contracts tests\sqlite_contract tests\test_artifact_storage_contract.py tests\test_export_artifact_repository_contract.py tests\test_run_store_core_contract.py tests\test_run_view_contract.py tests\domain\test_feedback_time_contract.py --basetemp=.pytest_tmp\contracts

Operational tests:

pytest -q tests\operational --basetemp=.pytest_tmp\operational

Required scenario regression pack:

pytest -q tests\system\test_happy_path_full_flow.py tests\system\test_review_resolution_flow.py tests\system\test_runtime_failure_terminalization.py tests\system\test_startup_repair_visibility_recovery_alignment.py --basetemp=.pytest_tmp\scenario_pack

Frontend validation:

cd C:\dev\InvoMatch\ui\invomatch-ui
npm run lint
npm run build

## Validation Evidence So Far

Observed local validation during implementation:

- Backend full baseline: 688 passed
- First expanded contract attempt: 47 passed, 14 errors
- Cause of contract errors: direct execution of abstract tests/test_run_store_contract.py template
- Operational tests: 78 passed
- Required scenario regression pack: 4 passed
- Frontend lint: passed
- Frontend build: passed

The contract layer was corrected to exclude direct execution of the abstract RunStore contract template.

## Closure Criteria Review

| Closure Criteria | Status |
|---|---|
| CI workflow exists | Complete |
| Backend validation runs in CI | Complete |
| Frontend lint/build runs in CI | Complete |
| Required scenario pack is represented | Complete |
| Workflow is documented | Complete |
| Local validation remains green | Pending corrected contract validation |
| CI configuration is committed and pushed | Pending commit/push |
| GitHub Actions execution result checked | First run failed on missing pytest temp root; re-run pending after repair |

## Implementation Files

Expected changed files:

- .github/workflows/ci.yml
- docs/architecture/MINI_EPIC_32_1_CI_VALIDATION_WORKFLOW_FOUNDATION.md

## Suggested Commit Message

ci: add release validation workflow foundation

## Closure Note

Mini-EPIC 32.1 should only be closed after:

1. The CI workflow file exists.
2. The workflow represents backend, executable contract, operational, scenario, lint, and build validation layers.
3. Local validation remains green.
4. The CI configuration is committed and pushed.
5. GitHub Actions runs the workflow successfully or any CI/local drift is repaired and revalidated.