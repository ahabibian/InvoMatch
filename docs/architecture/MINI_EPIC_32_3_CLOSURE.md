# Mini-EPIC 32.3 Closure - Release Candidate Validation Pack & Manual Release Checklist

## Status

Closed.

## Context

Mini-EPIC 32.2 defined the CI release gate evidence model for EPIC 32.

Mini-EPIC 32.3 extends that release pipeline documentation by defining the local release-candidate validation pack and the manual checklist that must be completed before a commit can be called release-candidate-ready.

This mini-epic intentionally does not introduce deployment, Docker packaging, release tagging, staging promotion, production promotion, changelog generation, artifact publishing, rollback procedures, or workflow behavior changes.

## Confirmed Starting State

- Mini-EPIC 32.2 was closed.
- Commit pushed to GitHub:
  - `eadfc41 docs: define CI release gate evidence model`
- Previous CI workflow repair commit:
  - `6e0cce0 ci: prepare pytest temp root in validation workflow`
- EPIC 32 release pipeline documentation already defined:
  - green CI run meaning
  - red CI run blocking behavior
  - release-blocking CI steps
  - CI/local drift handling
  - required CI evidence model
- Mini-EPIC 32.1 CI evidence was recorded:
  - initial failed CI run `#153` on commit `9ddc8b0`
  - repair commit `6e0cce0`
  - final passing CI run `#154` on commit `6e0cce0`
- Mini-EPIC 32.2 closure document existed:
  - `docs/architecture/MINI_EPIC_32_2_CLOSURE.md`
- EPIC 32 release pipeline document existed:
  - `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`
- Local sanity validation previously passed:
  - `pytest --collect-only -q --basetemp=.pytest_tmp`
  - `688 tests collected in 5.75s`
- Branch `main` was up to date with `origin/main`.
- Working tree was clean.

## Goal

Define the release-candidate validation pack and manual release checklist for InvoMatch before any deployment, Docker packaging, environment promotion, tagging, or publishing is introduced.

The objective is to make release-candidate validation repeatable, auditable, and operationally clear.

## Scope Completed

Mini-EPIC 32.3 completed the following documentation work:

1. Reviewed the current EPIC 32 release pipeline documentation.
2. Reviewed the current GitHub Actions workflow boundary.
3. Defined the required local validation pack for a release candidate:
   - backend full test baseline
   - contract/API validation
   - operational validation
   - required scenario regression pack
   - frontend lint
   - frontend build
4. Defined required GitHub Actions validation evidence:
   - workflow name
   - run number
   - commit SHA
   - branch
   - status
   - failed step if any
   - repair commit if any
   - final passing run
5. Defined a manual release-candidate checklist for operators.
6. Clearly separated release-candidate-ready from:
   - deployed
   - packaged
   - tagged
   - published
   - promoted to staging
   - promoted to production
7. Updated EPIC 32 documentation.
8. Created this Mini-EPIC 32.3 closure document.
9. Did not change CI workflow behavior.

## Files Changed

- `docs/architecture/EPIC_32_RELEASE_PIPELINE.md`
- `docs/architecture/MINI_EPIC_32_3_CLOSURE.md`

## Required Local Release Candidate Validation Commands

The release-candidate validation pack is documented as the following command set.

### Backend Full Test Baseline

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q --basetemp=.pytest_tmp

### Contract/API Validation

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\api tests\contract --basetemp=.pytest_tmp

If either directory does not exist in the repository state being validated, the operator must record that explicitly rather than silently treating the category as passed.

### Operational Validation

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\operational --basetemp=.pytest_tmp

### Scenario Regression Pack

Command:

    cd C:\dev\InvoMatch
    $env:PYTHONPATH = "src"
    pytest -q tests\system\test_happy_path_full_flow.py tests\system\test_review_resolution_flow.py tests\system\test_runtime_failure_terminalization.py tests\system\test_startup_repair_visibility_recovery_alignment.py --basetemp=.pytest_tmp

### Frontend Lint

Command:

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run lint

### Frontend Build

Command:

    cd C:\dev\InvoMatch\ui\invomatch-ui
    npm run build

## Required GitHub Actions Evidence

A commit cannot be called release-candidate-ready unless the GitHub Actions evidence has been reviewed and recorded.

Required evidence:

| Evidence Field | Required |
|---|---|
| Workflow name | Yes |
| Run number | Yes |
| Commit SHA | Yes |
| Branch | Yes |
| Status | Yes |
| Failed step if any | Yes, when applicable |
| Repair commit if any | Yes, when applicable |
| Final passing run | Yes |
| Final passing commit SHA | Yes |

A red CI run blocks release-candidate readiness. A local green run does not override a red CI run.

## Manual Release Candidate Checklist

The operator must confirm all items below before declaring a commit release-candidate-ready:

| Check | Status |
|---|---|
| Working tree clean before final validation | Required |
| Branch aligned with origin | Required |
| Backend full test baseline passed | Required |
| Contract/API validation passed or absence recorded | Required |
| Operational validation passed | Required |
| Scenario regression pack passed | Required |
| Frontend lint passed | Required |
| Frontend build passed | Required |
| GitHub Actions evidence reviewed | Required |
| Any red CI run repaired and revalidated | Required when applicable |
| Release-candidate-ready not described as deployed/released | Required |
| Closure document created | Required |
| Documentation committed | Required |
| Documentation pushed | Required |

## Release Candidate Boundary

Release-candidate-ready means:

- the commit passed the documented validation gate
- required local evidence was recorded
- required GitHub Actions evidence was reviewed
- no known release-blocking validation failure remains open

Release-candidate-ready does not mean:

- deployed
- packaged
- Dockerized
- tagged
- published
- promoted to staging
- promoted to production
- rollback-ready
- changelog-published

Those activities are intentionally deferred to later release/deployment work.

## Workflow Behavior

No GitHub Actions workflow behavior was changed in this mini-epic.

This was intentional. Mini-EPIC 32.3 defines the release-candidate validation contract and manual checklist only.

## Closure Criteria Review

| Closure Criteria | Status |
|---|---|
| Release candidate validation pack documented | Complete |
| Manual release checklist documented | Complete |
| Local validation commands explicitly listed | Complete |
| GitHub Actions validation evidence requirements referenced | Complete |
| Release-candidate-ready clearly separated from deployed/released | Complete |
| EPIC 32 documentation updated | Complete |
| Mini-EPIC 32.3 closure document created | Complete |
| No workflow behavior changed unless a real defect was found | Complete |
| Local sanity check passes | To be recorded during final validation |
| Working tree clean | To be recorded after commit |
| Documentation committed and pushed | To be recorded after commit/push |

## Final Validation Commands

Before commit:

    cd C:\dev\InvoMatch
    git diff -- docs\architecture\EPIC_32_RELEASE_PIPELINE.md docs\architecture\MINI_EPIC_32_3_CLOSURE.md
    $env:PYTHONPATH = "src"
    pytest --collect-only -q --basetemp=.pytest_tmp

After commit and push:

    cd C:\dev\InvoMatch
    git status
    git --no-pager log --oneline -5

## Suggested Commit Message

    docs: define release candidate validation checklist