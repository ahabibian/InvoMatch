
# Release Candidate Evidence Record Pre-Creation Checklist
Status

Active governance checklist for future release-candidate evidence records.

This document defines the checks that must be satisfied before any real release-candidate evidence record instance is created.

It is introduced by Mini-EPIC 32.34 and builds on the preparation boundary established in Mini-EPIC 32.33.

Purpose

The purpose of this checklist is to prevent premature creation of release-candidate evidence records.

A future release-candidate evidence record may only be created after the required repository state, metadata, references, validation plan, CI expectations, release identity expectations, artifact/package/deployment boundaries, and finalization prerequisites are explicitly known.

This checklist does not create a release candidate and does not create a release-candidate evidence record instance.

Required Governance References

Before creating any future release-candidate evidence record, the record owner must review and reference:

docs/architecture/EPIC_32_RELEASE_PIPELINE.md
docs/architecture/RELEASE_CANDIDATE_EVIDENCE_INDEX.md
docs/architecture/RELEASE_CANDIDATE_EVIDENCE_PRE_CREATION_CHECKLIST.md
docs/architecture/MINI_EPIC_32_33_CLOSURE.md
Existing release manifest dry-run contract and evidence boundary documentation under docs/architecture
Repository State Checklist

Before any future release-candidate evidence record file may be created, the following checks are required:

Branch must be main unless a documented release branch policy exists.
Local branch and remote tracking branch must be aligned before evidence creation.
Working tree must be clean before evidence creation.
Working tree must remain clean until the actual evidence record creation change begins.
Untracked generated output must not be present in tracked release evidence paths.
Mini-EPIC 32.33 preparation boundary must be referenced.
The release candidate evidence index must be reviewed.
Current EPIC 32 validation and evidence rules must be reviewed.
## Required Metadata Before Evidence Creation

The following metadata must be known before creating a future release-candidate evidence record:

Evidence record owner
Evidence record purpose
Candidate scope
Source branch
Source commit SHA
Working tree state
Intended validation packs
CI evidence expectation
Release identity capture expectation
Artifact expectation
Package expectation
Deployment expectation
Finalization owner or reviewer
## Required Future Record References

A future release-candidate evidence record must include references to:

The source commit under evaluation
The source branch under evaluation
The evidence index entry or intended evidence index location
The EPIC 32 release pipeline rules in effect at the time of evidence creation
The validation-pack plan
The CI evidence plan, if CI is expected to become release evidence
The release identity capture expectation
Any generated artifact or package boundary, if applicable
The non-release and non-deployment declarations that remain active until explicitly superseded
## Validation-Pack Plan Readiness

Before evidence record creation, the intended validation-pack plan must identify whether each validation area is planned, deferred, blocked, or out of scope for the specific record.

The required validation areas are:

Required scenario regression pack
Operational validation pack
Contract validation pack
Full backend validation pack
Frontend lint
Frontend build
CI validation

No validation result may be claimed before actual execution.

## CI Evidence Expectations

Before creating a future release-candidate evidence record, the intended CI evidence expectations must be clear.

At minimum, the future record must be prepared to capture:

CI provider or execution location
Branch
Commit SHA
Run identifier
Run status
Failed step, if any
Repair commit, if applicable
Final passing run, if applicable
Whether CI is being treated as release-gate evidence

A future record must not imply CI success before CI has run and produced evidence.

## Release Identity Capture Expectations

Before creating a future release-candidate evidence record, the release identity capture expectation must be defined.

The future record must be prepared to capture:

Application name, if declared
Application version, if declared
Release commit SHA
Release branch
Build timestamp, if declared
Validation status
Whether metadata is available
Whether the runtime release identity endpoint was used as evidence

A future record must not imply runtime release identity verification before that verification has actually occurred.

## Non-Release Boundary

Before any future release-candidate evidence record is created, the following declarations must remain explicit unless a later approved release process supersedes them:

This checklist does not create a release candidate.
This checklist does not create a release-candidate evidence record instance.
This checklist does not generate a package.
This checklist does not publish an artifact.
This checklist does not deploy anything.
This checklist does not perform staging promotion.
This checklist does not perform production promotion.
This checklist does not introduce release automation.
This checklist does not change CI workflow behavior.
This checklist does not change runtime behavior.
This checklist does not change CLI behavior.
This checklist does not change the manifest schema.
This checklist does not claim production readiness.
This checklist does not claim release-candidate readiness.
## Blocked Until Actual Validation Execution

The following must remain blocked until actual validation execution occurs:

Claiming release-candidate readiness
Claiming production readiness
Claiming CI pass evidence
Claiming validation-pack pass evidence
Claiming generated package readiness
Claiming artifact publication
Claiming deployment readiness
Claiming staging or production promotion
Marking a future evidence record finalized
Updating any release status based on unexecuted validation
## Finalization Prerequisites For Future Evidence Records

A future release-candidate evidence record may only be finalized after:

Validation evidence is captured.
CI evidence is captured, if in scope.
Release identity is captured, if in scope.
Failed steps are documented, if any failure occurred.
Repair commit is documented, if repair was needed.
Final clean working tree state is verified.
Evidence index is updated.
Non-release or release boundary is stated.
Reviewer or owner confirmation is captured.
Mini-EPIC 32.34 Boundary

Mini-EPIC 32.34 defines this checklist only.

It does not create a release candidate, does not create a release-candidate evidence record instance, does not execute validation packs, does not run CI, does not generate packages, does not publish artifacts, does not change runtime behavior, does not change CLI behavior, does not change CI configuration, does not deploy anything, and does not claim release-candidate or production readiness.

Targeted Baseline

The only validation allowed for Mini-EPIC 32.34 closure is the targeted release manifest dry-run test as a non-release baseline:

src = "src"
pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp

This baseline confirms that the documentation-only change did not affect release manifest dry-run behavior.