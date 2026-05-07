# Release Candidate Evidence Record Finalization Gate

## Status

This document defines the internal finalization gate for release candidate evidence records.

It is a documentation and policy artifact only.

It does not create a release candidate, create a package, publish artifacts, introduce automation, deploy software, approve staging promotion, approve production promotion, or claim production readiness.

## Purpose

Release candidate evidence records must not become authoritative simply because they exist.

A record may only be treated as internally acceptable evidence after it satisfies a defined finalization gate.

The purpose of this gate is to ensure that each evidence record is:

- tied to a clear repository identity
- supported by explicit validation evidence
- bounded by clean repository-state checks
- clear about generated-output tracking
- explicit about non-deployment boundaries
- reviewed with documented signoff notes
- assigned a final status that accurately reflects what the record proves

## Evidence Record Finalization States

### draft

The evidence record is incomplete, unreviewed, partially populated, or not yet audited.

Draft records must not be used as authoritative evidence for future release-candidate workflows.

### internally reviewed

The evidence record has been reviewed for structure, consistency, and boundary language, but has not yet been accepted as finalized evidence.

This state may be used when review has occurred but one or more finalization requirements remain open.

### finalized-local-dry-run

The evidence record is acceptable as local dry-run evidence only.

This state means the record has satisfied the finalization gate for local dry-run evidence, including repository identity, validation evidence, clean-state checks, generated-output tracking checks, non-deployment boundary confirmation, reviewer notes, and final status.

This state does not mean release approval.

### rejected

The evidence record failed a required consistency, validation, identity, generated-output, wording, or boundary check.

Rejected records must not be used as authoritative evidence except as examples of failed or invalid evidence.

### superseded

The evidence record has been replaced by a newer evidence record.

Superseded records may remain useful for historical traceability, but future release-candidate workflows should reference the newer record instead.

## Finalization Gate Requirements

A release candidate evidence record may only be finalized when all required checks below are satisfied.

### 1. Repository Identity

The record must include repository identity fields sufficient to trace the evidence back to a specific source state.

Required fields:

- repository path or repository name
- branch
- commit SHA
- working tree state at the time evidence was captured
- evidence record path
- evidence record identifier or title

The commit SHA must be concrete. Placeholder values such as `unknown`, `pending`, `TBD`, or empty values are not acceptable for finalized evidence.

The branch must be concrete. Empty or placeholder branch values are not acceptable for finalized evidence.

### 2. Clean-State Verification

The record must include explicit clean-state verification.

Required clean-state checks:

- clean working tree before evidence capture or before audit changes
- clean working tree after relevant documentation changes are committed and pushed, where applicable
- explanation for any non-clean state if the record is not finalized

A dirty working tree blocks finalization unless the record is explicitly marked `draft`, `internally reviewed`, `rejected`, or `superseded` with a documented explanation.

A dirty working tree must not be hidden or normalized away.

### 3. Validation Evidence

The record must include validation evidence relevant to the evidence type.

For local dry-run release manifest evidence, the required targeted validation is:

~~~powershell
$env:PYTHONPATH = "src"
pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp
~~~

A finalized evidence record must include:

- validation command
- validation result
- pass/fail status
- test count or meaningful result summary, where available
- failure details if validation failed
- explicit statement of whether the failure blocks finalization

Failed required validation blocks finalization unless the record is intentionally marked `rejected` or kept as `draft` / `internally reviewed` with the failure documented.

### 4. Dry-Run Manifest Evidence

Where the evidence record concerns release manifest dry-run behavior, it must reference the applicable dry-run manifest evidence.

Required items, where applicable:

- dry-run manifest contract reference
- generated preview path, if a preview was written
- confirmation that the preview is non-release output
- confirmation that the preview was not treated as a package
- confirmation that dry-run output was not published
- confirmation that dry-run output was not tracked under git

A finalized local dry-run evidence record must not imply that the dry-run preview is a release artifact.

### 5. Generated-Output Tracking Check

The record must include explicit generated-output tracking verification.

Required checks:

~~~powershell
git status --short output
git ls-files output
~~~

Finalization is blocked if generated output under `output/` is tracked, unless a future policy explicitly permits a specific generated artifact class.

For Mini-EPIC 32 local dry-run evidence, generated output under `output/` must remain untracked.

### 6. Non-Deployment Boundary Confirmation

The record must explicitly confirm that finalization does not perform or approve deployment-related actions.

Required confirmations:

- no real release candidate was created
- no package was created
- no ZIP or tar archive was produced as a release package
- no Docker image was built or published
- no artifact was published
- no semantic version tag was created
- no GitHub Release was created
- no staging promotion was approved
- no production promotion was approved
- no deployment was performed
- no release automation was introduced
- no runtime release registry was introduced
- no database release state was persisted
- no environment promotion occurred
- no production readiness was claimed

### 7. Reviewer Signoff Notes

The record must include reviewer signoff notes.

The notes must identify what was reviewed, including at minimum:

- repository identity
- validation evidence
- dry-run manifest evidence, where applicable
- generated-output tracking
- documentation alignment
- non-deployment boundary language
- final status

Reviewer notes do not need to represent external approval.

Reviewer notes are internal acceptance notes only.

### 8. Required Final Status

The record must end with a final status.

Allowed final statuses:

- `draft`
- `internally reviewed`
- `finalized-local-dry-run`
- `rejected`
- `superseded`

A record must not use ambiguous final statuses such as:

- `done`
- `approved`
- `released`
- `production-ready`
- `ready for deployment`
- `package complete`
- `release candidate approved`

## Blocking Conditions

Any condition below blocks finalization as `finalized-local-dry-run`.

- missing repository identity
- missing commit SHA
- missing branch
- placeholder commit SHA
- placeholder branch
- dirty working tree without explicit explanation
- missing validation command
- missing validation result
- failed required validation without documented failed status
- missing generated-output tracking result
- tracked generated output under `output/`
- missing dry-run manifest evidence when the record concerns manifest dry-run behavior
- ambiguous release wording
- ambiguous package wording
- ambiguous deployment wording
- any claim of production readiness
- any claim that local dry-run output is a release artifact
- any undocumented change to the package manifest dry-run contract
- any evidence record claiming more than it proves
- any evidence record implying staging or production promotion approval
- any evidence record implying CI release automation when no such automation exists
- any evidence record implying artifact publishing when no artifact was published

## Non-Deployment Boundary Rules

Finalized evidence is not release approval.

Finalized local dry-run evidence does not mean a package was created.

Finalized local dry-run evidence does not mean an artifact was published.

Finalized local dry-run evidence does not mean CI release automation exists.

Finalized local dry-run evidence does not mean staging deployment is approved.

Finalized local dry-run evidence does not mean production deployment is approved.

Finalized local dry-run evidence does not mean deployment readiness.

Finalized local dry-run evidence does not mean production readiness.

Finalized local dry-run evidence only means that a specific local dry-run evidence record satisfied this internal evidence-record finalization gate.

## Cross-Reference Rules

### RELEASE_CANDIDATE_EVIDENCE_INDEX.md

An evidence record may be referenced from the evidence index when:

- the record exists in the repository
- the record has a clear status
- the record has a clear evidence type
- the record does not claim more than it proves
- the index entry remains focused on evidence traceability rather than process instructions

The evidence index may reference this finalization gate as governing policy.

The index must not become a process manual.

### EPIC_32_RELEASE_PIPELINE.md

An evidence record may be referenced from the EPIC 32 release pipeline document when it affects the release pipeline evidence model, release-candidate traceability, or documented validation discipline.

References from the EPIC document must remain concise.

The EPIC document must not duplicate the full finalization gate.

### Closure Documents

A Mini-EPIC closure document should reference an evidence record when that record was created, audited, finalized, rejected, or superseded as part of the Mini-EPIC.

The closure document must describe what changed and what did not change.

A closure document must not claim release, package, deployment, or production readiness unless those actions actually occurred under a future approved release process.

### Superseded Records

An evidence record should be marked `superseded` when a newer record replaces it for the same evidence purpose.

A superseded record should retain historical traceability but must direct future workflows toward the newer record.

### Rejected Records

An evidence record should be marked `rejected` when it fails consistency, validation, generated-output tracking, or non-deployment boundary checks.

Rejected records may remain in the repository only if they are useful for audit traceability.

Rejected records must not be referenced as acceptable evidence.

## Package Manifest Dry-Run Contract Boundary

This finalization gate does not modify the package manifest dry-run contract.

If a future evidence review discovers a real inconsistency in the package manifest dry-run contract, that inconsistency must be handled in a separate Mini-EPIC with explicit scope.

Mini-EPIC 32 local dry-run evidence must continue to treat dry-run previews as non-release, non-package, non-published output.

## Summary

A release candidate evidence record is finalized only when it has concrete repository identity, clean-state evidence, validation evidence, generated-output tracking checks, non-deployment boundary confirmation, reviewer signoff notes, and an allowed final status.

For local dry-run evidence, `finalized-local-dry-run` means internally acceptable local dry-run evidence only.

It does not mean release approval, package creation, artifact publishing, CI release automation, deployment readiness, staging promotion, production promotion, or production readiness.