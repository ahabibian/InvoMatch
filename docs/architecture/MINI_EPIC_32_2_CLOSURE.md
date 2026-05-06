# Mini-EPIC 32.2 Closure - CI Failure Evidence & Release Gate Documentation

## Status

Closed.

## Context

Mini-EPIC 32.1 established the first GitHub Actions CI validation workflow for the EPIC 32 release validation baseline.

That workflow proved that InvoMatch validation can run automatically on GitHub Actions, but the first clean-runner execution also exposed an important operational truth: CI evidence is only useful as a release gate when failures, repairs, and final passing runs are documented with enough precision to support release decisions.

Mini-EPIC 32.2 defines how CI validation results are interpreted, what they block, what evidence must be captured, and how CI/local drift is handled before closing release-related EPICs.

## Objective

Define the release-gate meaning of CI validation results for InvoMatch.

This Mini-EPIC does not add new validation layers. It documents how existing CI results are used as release evidence.

## Current CI Validation Boundary

The current CI workflow represents the release validation baseline introduced in EPIC 32.

The validation boundary includes:

| CI Step | Release-Gate Meaning |
|---|---|
| Backend full test baseline | Confirms the backend regression surface still passes under GitHub Actions. |
| Contract tests | Confirms API and boundary contracts have not drifted from documented expectations. |
| Operational tests | Confirms operational visibility and repair-related behavior remains valid. |
| Required scenario regression pack | Confirms critical product scenarios still work end-to-end. |
| Frontend lint | Confirms the frontend codebase has no lint violations under the configured lint rules. |
| Frontend build | Confirms the frontend TypeScript/Vite production build remains valid. |

## Green CI Run Meaning

A green CI run means:

1. The release validation workflow completed successfully on GitHub Actions.
2. All release-blocking CI steps passed on the referenced commit.
3. The referenced commit is eligible to be used as release validation evidence.
4. The repository state represented by that commit is not known to have CI/local drift.
5. Release-related EPIC closure can use the run as supporting evidence, provided the evidence metadata is captured.

A green CI run does not mean:

1. The product is production-deployed.
2. Docker packaging exists.
3. A staging or production promotion has happened.
4. A release artifact has been published.
5. Version tagging or changelog generation has occurred.
6. Future runtime environments are automatically guaranteed.

The meaning is intentionally narrow: green CI proves the validation baseline passed for a specific commit on GitHub Actions.

## Red CI Run Meaning

A red CI run means:

1. At least one release-blocking validation step failed.
2. Release-related EPIC closure is blocked until the failure is understood.
3. The failure must be classified as either:
   - product/test regression,
   - CI environment defect,
   - configuration defect,
   - dependency/tooling drift,
   - or invalid workflow assumption.
4. A repair commit is required if the failure reflects a real defect in code, tests, configuration, or workflow setup.
5. A final passing CI run after repair is required before closure.

A red CI run must not be ignored simply because local tests pass.

## Release-Blocking Behavior

Any failed release validation step blocks release closure.

The following are release-blocking:

| Failure Type | Blocks Release Closure |
|---|---|
| Backend full test failure | Yes |
| Contract test failure | Yes |
| Operational test failure | Yes |
| Required scenario regression failure | Yes |
| Frontend lint failure | Yes |
| Frontend build failure | Yes |
| CI setup failure that prevents validation from running | Yes |
| Missing dependency/configuration required by CI | Yes |
| Clean-runner path or environment assumption failure | Yes |

Warnings do not block release closure unless they affect:

1. runtime behavior,
2. security posture,
3. future compatibility,
4. deployment safety,
5. validation reliability,
6. or evidence trustworthiness.

Warnings that may become blocking must be documented and either repaired or explicitly deferred with a reason.

## CI/Local Drift Handling

CI/local drift exists when local validation and GitHub Actions validation do not produce equivalent release confidence.

Examples include:

1. tests pass locally but fail on GitHub Actions,
2. GitHub Actions fails because a local-only directory or file exists,
3. environment variables are present locally but missing in CI,
4. local caches hide dependency or path problems,
5. frontend builds locally but fails under the CI Node/npm environment,
6. backend tests rely on local residue under output or temporary directories.

CI/local drift must be repaired before release-related closure.

The correct handling is:

1. Identify the failed CI step.
2. Identify whether the failure is product behavior, test behavior, or CI environment setup.
3. Repair the cause in code, tests, documentation, or workflow configuration.
4. Commit the repair.
5. Push the repair commit.
6. Confirm a final passing GitHub Actions run.
7. Record both the failed run and the final passing run in release evidence.

Local success alone is not sufficient after a CI failure.

## CI Evidence Model

Every release-related EPIC closure must capture the following CI evidence when CI is part of the release gate:

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

## Captured Evidence From Mini-EPIC 32.1

### Initial CI Run

| Field | Value |
|---|---|
| Workflow | Release validation workflow |
| Run number | #153 |
| Branch | main |
| Commit | 9ddc8b0 |
| Status | Failed |
| Failed area | Backend pytest temp-root setup |
| Failure reason | `.pytest_tmp` parent directory was missing on the clean GitHub Actions runner. |
| Interpretation | CI revealed a clean-runner environment assumption that local validation did not expose. |
| Release impact | Release closure blocked until repaired. |

### Repair Commit

| Field | Value |
|---|---|
| Commit | 6e0cce0 |
| Commit message | ci: prepare pytest temp root in validation workflow |
| Repair type | CI workflow environment setup repair |
| Reason | Ensure pytest temporary root exists before validation commands run on a clean GitHub Actions runner. |

### Final CI Run

| Field | Value |
|---|---|
| Workflow | Release validation workflow |
| Run number | #154 |
| Branch | main |
| Commit | 6e0cce0 |
| Status | Passed |
| Interpretation | Final release validation baseline passed after repair. |
| Release impact | Mini-EPIC 32.1 CI evidence became usable as release-gate evidence. |

## Operational Meaning For Future Release EPICs

For future release-related EPICs, the release evidence must show:

1. the exact commit being validated,
2. the final passing CI run,
3. any failed CI run that occurred during the EPIC,
4. the reason for failure,
5. the repair commit,
6. and confirmation that no unresolved CI/local drift remains.

A closure document that only says "tests passed" is not enough for release-related EPICs.

The required evidence must be specific enough that another operator can understand:

1. what was validated,
2. where it was validated,
3. what failed,
4. why it failed,
5. what repaired it,
6. and which final run made the release gate green.

## Non-Goals Confirmed

Mini-EPIC 32.2 did not add:

1. new tests,
2. test optimization,
3. parallel CI,
4. matrix builds,
5. Docker packaging,
6. release artifact publishing,
7. staging deployment,
8. production deployment,
9. rollback,
10. version tagging,
11. automatic changelog generation.

## Closure Criteria Review

| Closure Criteria | Status |
|---|---|
| CI release-gate meaning is documented | Complete |
| CI evidence requirements are documented | Complete |
| CI/local drift handling is documented | Complete |
| EPIC 32 docs include the 32.1 CI evidence | Complete after EPIC 32 document update |
| No workflow behavior changed unless documentation revealed a real defect | Complete |
| Working tree is clean | To be confirmed before commit |
| Documentation is committed and pushed | To be completed |

## Final Assessment

Mini-EPIC 32.2 converts the initial GitHub Actions validation from a simple pass/fail signal into usable release evidence.

The important standard is strict:

A release-related EPIC cannot close on a failed CI run, cannot ignore CI/local drift, and cannot rely on vague test-passed claims. It must capture the workflow, run number, commit, status, failure, repair, and final passing run.