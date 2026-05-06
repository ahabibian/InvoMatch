# Mini-EPIC 32.4 Closure - First Release Candidate Dry Run & Evidence Capture

## Status

Closed.

## Context

Mini-EPIC 32.3 defined the release-candidate validation pack and manual release checklist for InvoMatch.

Mini-EPIC 32.4 executed the first real release-candidate dry run against the documented validation pack and captured auditable evidence.

The initial dry-run target was:

- `b895d48 docs: define release candidate validation checklist`

This mini-epic did not deploy, package, tag, publish, promote to staging, promote to production, introduce Docker packaging, generate changelogs, or change release workflow behavior.

## Confirmed Starting State

- Commit pushed to GitHub:
  - `b895d48 docs: define release candidate validation checklist`
- Previous EPIC 32 commits:
  - `eadfc41 docs: define CI release gate evidence model`
  - `6e0cce0 ci: prepare pytest temp root in validation workflow`
  - `9ddc8b0 ci: add release validation workflow foundation`
  - `b8c59fc docs: define release pipeline baseline and repair validation drift`
- Mini-EPIC 32.3 closure document existed:
  - `docs/architecture/MINI_EPIC_32_3_CLOSURE.md`
- EPIC 32 release pipeline document existed:
  - `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`
- Branch `main` was up to date with `origin/main`.
- Working tree was clean.

## Scope Completed

Mini-EPIC 32.4 completed the following work:

1. Inspected the EPIC 32 release pipeline documentation.
2. Inspected the Mini-EPIC 32.3 closure document.
3. Executed the documented local release-candidate validation pack.
4. Captured local validation evidence in:
   - `docs/architecture/evidence/mini_epic_32_4/backend_full_test_baseline.log`
   - `docs/architecture/evidence/mini_epic_32_4/contract_api_validation.log`
   - `docs/architecture/evidence/mini_epic_32_4/contract_api_validation_corrected.log`
   - `docs/architecture/evidence/mini_epic_32_4/operational_validation.log`
   - `docs/architecture/evidence/mini_epic_32_4/scenario_regression_pack.log`
   - `docs/architecture/evidence/mini_epic_32_4/frontend_lint.log`
   - `docs/architecture/evidence/mini_epic_32_4/frontend_build.log`
5. Reviewed GitHub Actions evidence for the initial dry-run target.
6. Recorded the documentation defect exposed by the dry run.
7. Repaired the RC contract/API validation command path in:
   - `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`
8. Re-ran the corrected contract/API validation command.
9. Reviewed final GitHub Actions evidence for the repair commit.
10. Recorded the final release-candidate readiness decision.

## Initial Local Release Candidate Dry Run

Initial target:

- `b895d48 docs: define release candidate validation checklist`

### Backend Full Test Baseline

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q --basetemp=.pytest_tmp

Result:

    688 passed in 86.64s (0:01:26)

Status:

    Passed

Evidence log:

    docs/architecture/evidence/mini_epic_32_4/backend_full_test_baseline.log

### Contract/API Validation - Initial Documented Command

The release-candidate validation pack contained a stale/non-current command reference.

Initial executed command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\api tests\contracts --basetemp=.pytest_tmp

Result:

    ERROR: file or directory not found: tests\api
    no tests ran in 0.01s

Exit code:

    4

Status:

    Failed

Evidence log:

    docs/architecture/evidence/mini_epic_32_4/contract_api_validation.log

Finding:

The repository contains `tests\contracts`, but does not contain `tests\api`.

The EPIC 32 release pipeline document already listed the correct contract validation command in the earlier Contract Validation Pack section:

    pytest -q tests\contracts --basetemp=.pytest_tmp

However, the later Release Candidate Validation Pack section incorrectly listed:

    pytest -q tests\api tests\contract --basetemp=.pytest_tmp

This was a documentation defect inside the release validation boundary.

### Operational Validation

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\operational --basetemp=.pytest_tmp

Result:

    78 passed in 41.89s

Status:

    Passed

Evidence log:

    docs/architecture/evidence/mini_epic_32_4/operational_validation.log

### Scenario Regression Pack

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\system\test_happy_path_full_flow.py tests\system\test_review_resolution_flow.py tests\system\test_runtime_failure_terminalization.py tests\system\test_startup_repair_visibility_recovery_alignment.py --basetemp=.pytest_tmp

Result:

    4 passed in 4.91s

Status:

    Passed

Evidence log:

    docs/architecture/evidence/mini_epic_32_4/scenario_regression_pack.log

### Frontend Lint

Command:

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run lint

Result:

    eslint completed with no reported errors.

Exit code:

    0

Status:

    Passed

Evidence log:

    docs/architecture/evidence/mini_epic_32_4/frontend_lint.log

### Frontend Build

Command:

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run build

Result:

    tsc -b and vite build completed successfully.
    Vite transformed 28 modules.
    Build completed in 501ms.

Exit code:

    0

Status:

    Passed

Evidence log:

    docs/architecture/evidence/mini_epic_32_4/frontend_build.log

## Initial Local RC Dry Run Decision For b895d48

Decision:

    Not release-candidate-ready.

Reason:

The first release-candidate dry run exposed a documentation defect in the required RC contract/API validation command. The documented command referenced a missing/non-current test path and therefore failed.

This failure was not ignored and was not reclassified as success. It was repaired inside the release validation documentation boundary.

## Documentation Gap Repair

Repair commit:

    6cb5493 docs: repair release candidate contract validation path

File changed:

    docs/architecture/EPIC_32_RELEASE_PIPELINE.md

Repair summary:

- Replaced stale RC contract/API command:
  - from `pytest -q tests\api tests\contract --basetemp=.pytest_tmp`
  - to `pytest -q tests\contracts --basetemp=.pytest_tmp`
- Added an explicit note that the current repository contract validation path is:
  - `tests\contracts`

No workflow behavior was changed.

No backend behavior was changed.

No frontend behavior was changed.

## Corrected Contract/API Validation

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\contracts --basetemp=.pytest_tmp

Result:

    10 passed in 2.71s

Exit code:

    0

Status:

    Passed

Evidence log:

    docs/architecture/evidence/mini_epic_32_4/contract_api_validation_corrected.log

## GitHub Actions Evidence

### Initial Target CI Evidence

| Evidence Field | Value |
|---|---|
| Workflow name | CI Validation |
| Run number | #156 |
| Commit SHA | b895d48 |
| Branch | main |
| Status | Success |
| Duration | 57s |
| Failed step | None |
| Failure reason | None |
| Repair commit | 6cb5493 |
| Final passing run after repair | #157 |
| Final passing commit SHA | 6cb5493 |

### Final Repair Commit CI Evidence

| Evidence Field | Value |
|---|---|
| Workflow name | CI Validation |
| Run number | #157 |
| Commit SHA | 6cb5493 |
| Branch | main |
| Status | Success |
| Duration | 45s in workflow list; release validation job log showed 43s |
| Job | Release validation baseline |
| Failed step | None |
| Failure reason | None |
| Repair commit | 6cb5493 |
| Final passing run | #157 |
| Final passing commit SHA | 6cb5493 |

## Final Release Candidate Readiness Decision

Initial commit:

    b895d48 docs: define release candidate validation checklist

Decision:

    Not release-candidate-ready after first dry run.

Reason:

    The dry run exposed a documentation defect in the release-candidate validation command for contract/API validation.

Final candidate commit:

    6cb5493 docs: repair release candidate contract validation path

Decision:

    Release-candidate-ready.

Reason:

- The local backend full test baseline passed.
- The corrected contract/API validation passed.
- The operational validation pack passed.
- The required scenario regression pack passed.
- Frontend lint passed.
- Frontend build passed.
- GitHub Actions `CI Validation` run `#157` passed on commit `6cb5493`.
- No release-blocking local or CI failure remains open.

## Release Candidate Boundary Reminder

Release-candidate-ready means only that commit `6cb5493` passed the agreed validation gate and is eligible for later release or deployment work.

Release-candidate-ready does not mean:

- deployed
- released
- packaged
- Dockerized
- tagged
- published
- promoted to staging
- promoted to production
- rollback-ready
- changelog-published

Those activities remain outside Mini-EPIC 32.4.

## Closure Criteria Review

| Closure Criteria | Status |
|---|---|
| Documented local RC validation pack executed or failures recorded truthfully | Complete |
| Backend full test baseline result recorded | Complete |
| Contract/API validation result recorded | Complete |
| Operational validation result recorded | Complete |
| Scenario regression pack result recorded | Complete |
| Frontend lint result recorded | Complete |
| Frontend build result recorded | Complete |
| GitHub Actions evidence for commit b895d48 recorded | Complete |
| Release-candidate-ready decision explicitly stated | Complete |
| Release-candidate-ready separated from deployed/released/tagged/packaged/promoted | Complete |
| Mini-EPIC 32.4 closure document created | Complete |
| EPIC 32 documentation updated only because dry run exposed a documentation gap | Complete |
| No workflow behavior changed unless a real defect was found | Complete |
| Working tree clean | To be confirmed after commit |
| Documentation committed and pushed | To be confirmed after commit and push |

## Files Changed In Mini-EPIC 32.4

- `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`
- `docs/architecture/MINI_EPIC_32_4_CLOSURE.md`
- `docs/architecture/evidence/mini_epic_32_4/backend_full_test_baseline.log`
- `docs/architecture/evidence/mini_epic_32_4/contract_api_validation.log`
- `docs/architecture/evidence/mini_epic_32_4/contract_api_validation_corrected.log`
- `docs/architecture/evidence/mini_epic_32_4/operational_validation.log`
- `docs/architecture/evidence/mini_epic_32_4/scenario_regression_pack.log`
- `docs/architecture/evidence/mini_epic_32_4/frontend_lint.log`
- `docs/architecture/evidence/mini_epic_32_4/frontend_build.log`

## Suggested Closure Commit Message

    docs: capture first release candidate dry run evidence