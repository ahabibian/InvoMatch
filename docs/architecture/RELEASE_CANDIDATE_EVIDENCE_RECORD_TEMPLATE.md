# Release Candidate Evidence Record Template

Status: Template only  
Scope: Release-candidate evidence capture scaffold  
Boundary: Documentation scaffold only; not a release package, not a generated artifact, not deployment evidence

## Purpose

This template is a reusable evidence record scaffold for future InvoMatch release-candidate dry-run validation activities.

Each future release-candidate evidence record must copy this template and replace placeholders with actual observed results from the validation run.

This template does not create a release candidate.  
This template does not create a release package.  
This template does not publish artifacts.  
This template does not replace validation execution.  
This template must not be used to claim release readiness without observed command results.

## Evidence Record Identity

| Field | Value |
|---|---|
| Release candidate identifier | `<RC_IDENTIFIER>` |
| Evidence record file | `<EVIDENCE_RECORD_PATH>` |
| Validation timestamp UTC | `<VALIDATION_TIMESTAMP_UTC>` |
| Validation actor | `<VALIDATION_ACTOR>` |
| Validation location | `<LOCAL_MACHINE_OR_CI_CONTEXT>` |
| Evidence status | `<draft / complete / blocked>` |

## Source Identity

| Field | Observed Value |
|---|---|
| Repository | `<REPOSITORY_URL_OR_NAME>` |
| Branch | `<BRANCH>` |
| Commit SHA | `<COMMIT_SHA>` |
| Commit subject | `<COMMIT_SUBJECT>` |
| Commit pushed to origin | `<yes / no / not checked>` |
| Local branch up to date with origin | `<yes / no / not checked>` |

Observed command:

~~~powershell
git branch --show-current
git status
git --no-pager log --oneline -1
~~~

Observed output:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

## Repository Cleanliness

| Check | Observed Result |
|---|---|
| Working tree clean before validation | `<yes / no>` |
| Working tree clean after validation | `<yes / no>` |
| No generated output files tracked | `<yes / no>` |
| No package/archive artifacts tracked | `<yes / no>` |

Observed command:

~~~powershell
git status --short
~~~

Observed output:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

## Local Validation Evidence

This section must contain actual observed command results.

Do not paste expected results.  
Do not copy results from a previous release-candidate record.  
Do not claim success unless the command was executed for this candidate.

### Required Scenario Regression Pack

Command:

~~~powershell
$env:PYTHONPATH = "src"
pytest -q `
  tests\system\test_happy_path_full_flow.py `
  tests\system\test_review_resolution_flow.py `
  tests\system\test_runtime_failure_terminalization.py `
  tests\system\test_startup_repair_visibility_recovery_alignment.py `
  --basetemp=.pytest_tmp
~~~

Observed result:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

Status: `<pass / fail / not run>`

### Operational Validation Pack

Command:

~~~powershell
$env:PYTHONPATH = "src"
pytest -q tests\operational --basetemp=.pytest_tmp
~~~

Observed result:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

Status: `<pass / fail / not run>`

### Contract Validation Pack

Command:

~~~powershell
$env:PYTHONPATH = "src"
pytest -q tests\contracts --basetemp=.pytest_tmp
~~~

Observed result:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

Status: `<pass / fail / not run>`

### Full Backend Validation Pack

Command:

~~~powershell
$env:PYTHONPATH = "src"
pytest -q tests --basetemp=.pytest_tmp
~~~

Observed result:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

Status: `<pass / fail / not run>`

### Frontend Lint

Command:

~~~powershell
cd C:\dev\InvoMatch\ui\invomatch-ui
npm run lint
~~~

Observed result:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

Status: `<pass / fail / not run>`

### Frontend Build

Command:

~~~powershell
cd C:\dev\InvoMatch\ui\invomatch-ui
npm run build
~~~

Observed result:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

Status: `<pass / fail / not run>`

## CI Validation Evidence

CI evidence is optional only when the release-candidate process explicitly permits local-only validation.

If CI is available, this section must reference the actual CI run.

| Field | Observed Value |
|---|---|
| CI provider | `<GitHub Actions / other / not available>` |
| Workflow name | `<WORKFLOW_NAME>` |
| Run number | `<RUN_NUMBER>` |
| Run URL | `<RUN_URL>` |
| Branch | `<BRANCH>` |
| Commit SHA | `<COMMIT_SHA>` |
| Final CI status | `<pass / fail / cancelled / not run>` |
| Failed step, if any | `<FAILED_STEP_OR_NONE>` |

Notes:

~~~text
<PASTE_CI_NOTES_HERE>
~~~

## Release Identity Metadata Check

This check confirms that release identity is bounded and operationally visible where applicable.

It does not declare release readiness by itself.

Command:

~~~powershell
<PASTE_RELEASE_IDENTITY_CHECK_COMMAND_HERE>
~~~

Observed result:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

Status: `<pass / fail / not run>`

## Release Manifest Dry-Run Evidence

Release manifest dry-run evidence is local-only evidence unless explicitly promoted by a future release process.

It is not a package.  
It is not an artifact publication.  
It is not a deployment.  
It is not a release registry write.

### Success Path: stdout JSON Mode

Command:

~~~powershell
$env:PYTHONPATH = "src"
python scripts\release_manifest_dry_run.py
~~~

Observed stdout:

~~~json
<PASTE_OBSERVED_STDOUT_JSON_HERE>
~~~

Observed stderr:

~~~text
<PASTE_OBSERVED_STDERR_HERE>
~~~

Exit code: `<EXIT_CODE>`  
Status: `<pass / fail / not run>`

### Success Path: write-preview Mode

Command:

~~~powershell
$env:PYTHONPATH = "src"
python scripts\release_manifest_dry_run.py --write-preview
~~~

Observed stdout:

~~~text
<PASTE_OBSERVED_STDOUT_HERE>
~~~

Observed stderr:

~~~text
<PASTE_OBSERVED_STDERR_HERE>
~~~

Expected preview path, if generated locally:

~~~text
output/local/release_manifest_dry_run/package_manifest_preview.json
~~~

Exit code: `<EXIT_CODE>`  
Status: `<pass / fail / not run>`

### Failure Path Reference

Failure-path evidence must reference an actual observed failure run or a documented prior failure-path verification.

| Field | Value |
|---|---|
| Failure-path source | `<CURRENT_RC_RUN / PRIOR_VERIFIED_EVIDENCE>` |
| Referenced evidence file | `<PATH>` |
| Referenced commit | `<COMMIT_SHA>` |
| Failure condition | `<DESCRIPTION>` |
| Confirmed behavior | `<NONZERO_EXIT / STDERR_ONLY / NO_FILE_WRITE / OTHER>` |

Observed or referenced failure output:

~~~text
<PASTE_OUTPUT_OR_REFERENCE_SUMMARY_HERE>
~~~

## Success-Path Evidence References

Reference actual observed success-path evidence.

| Evidence Area | Reference |
|---|---|
| Scenario regression pack | `<PATH_OR_CI_RUN>` |
| Operational validation pack | `<PATH_OR_CI_RUN>` |
| Contract validation pack | `<PATH_OR_CI_RUN>` |
| Full backend validation pack | `<PATH_OR_CI_RUN>` |
| Frontend lint | `<PATH_OR_CI_RUN>` |
| Frontend build | `<PATH_OR_CI_RUN>` |
| Release manifest dry-run stdout JSON mode | `<PATH_OR_COMMAND_OUTPUT>` |
| Release manifest dry-run write-preview mode | `<PATH_OR_COMMAND_OUTPUT>` |

## Failure-Path Evidence References

Reference actual observed failure-path evidence where applicable.

| Evidence Area | Reference |
|---|---|
| Release manifest schema validation failure | `<PATH_OR_PRIOR_EVIDENCE_REFERENCE>` |
| Release manifest CLI failure contract | `<PATH_OR_PRIOR_EVIDENCE_REFERENCE>` |
| Release gate blocking behavior | `<PATH_OR_CI_RUN>` |
| Repair validation, if applicable | `<PATH_OR_CI_RUN>` |

## Generated Output Tracking Check

Generated local outputs must not be tracked as release artifacts unless a future release process explicitly defines that boundary.

Command:

~~~powershell
git status --short
git ls-files output
~~~

Observed output:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

Result:

~~~text
<CONFIRM WHETHER ANY GENERATED OUTPUT FILES ARE TRACKED>
~~~

## Local-Only Evidence Boundary

The following are local-only evidence unless explicitly promoted by a future release process:

- command output pasted into an evidence record
- local pytest output
- local frontend lint/build output
- local release manifest dry-run stdout
- local release manifest dry-run preview JSON
- local generated files under `output/local`

Local-only evidence must not be described as:

- release artifact
- published package
- deployment artifact
- production verification
- staging promotion
- GitHub Release asset
- runtime release registry entry

## Non-Deployment Boundary

For this evidence record, confirm the following:

| Boundary | Confirmed |
|---|---|
| No real package created | `<yes / no>` |
| No ZIP or tar archive created | `<yes / no>` |
| No Docker image created | `<yes / no>` |
| No artifact published | `<yes / no>` |
| No Git tag created | `<yes / no>` |
| No GitHub Release created | `<yes / no>` |
| No deployment performed | `<yes / no>` |
| No staging promotion performed | `<yes / no>` |
| No production promotion performed | `<yes / no>` |
| No runtime release registry write performed | `<yes / no>` |
| No database release-state persistence introduced | `<yes / no>` |
| No rollback behavior introduced | `<yes / no>` |

## Final Clean Working Tree Check

Command:

~~~powershell
git status
git status --short
~~~

Observed output:

~~~text
<PASTE_OBSERVED_OUTPUT_HERE>
~~~

Status: `<clean / not clean>`

## Reviewer / Signoff Notes

Reviewer:

~~~text
<REVIEWER_NAME_OR_ROLE>
~~~

Decision:

~~~text
<accepted / blocked / needs repair / not reviewed>
~~~

Notes:

~~~text
<PASTE_REVIEW_NOTES_HERE>
~~~

## Final Statement

This evidence record is valid only when populated with actual observed command results for the referenced release candidate.

This evidence record does not create a release package, does not publish artifacts, does not deploy, and does not independently claim release readiness.