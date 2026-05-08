
Mini-EPIC 32.36 Closure - Release Candidate Evidence Record Lifecycle State Transition Rules
Status

Closed as documentation and governance only.

Mini-EPIC 32.36 defines lifecycle state transition rules for future release-candidate evidence records.

It does not create a release candidate, does not create an actual release-candidate evidence record instance, does not execute validation packs, does not run CI, does not capture CI evidence, does not generate packages, does not publish artifacts, does not deploy anything, does not change runtime behavior, does not change CLI behavior, does not change CI configuration, does not change manifest schema, does not change release identity behavior, and does not claim release-candidate or production readiness.

Starting State

Branch before work:

main

Repository alignment before work:

HEAD: 9cfbf2f540019391538f04df9ed98bbd9d6f7253
origin/main: 9cfbf2f540019391538f04df9ed98bbd9d6f7253

Working tree before work:

clean
Creation Gate Dependency

Mini-EPIC 32.36 builds directly on the Mini-EPIC 32.35 creation gate:

docs\architecture\MINI_EPIC_32_35_CLOSURE.md

The Mini-EPIC 32.35 creation gate remains the entry point into the evidence record lifecycle.

A future evidence record may not enter the lifecycle unless it has passed the creation gate.

Goal

Define the lifecycle state transition model for future release-candidate evidence records.

The goal is to define:

allowed lifecycle states;
allowed lifecycle state transitions;
blocked lifecycle state transitions;
required evidence before transition;
representation rules for pending, incomplete, failed, repaired, superseded, finalized, and voided records;
finalization blocking rules;
separation between evidence lifecycle governance and release/package/deployment/production claims.
Scope Completed

Mini-EPIC 32.36 completed the following documentation-governance scope:

defined allowed lifecycle states for future release-candidate evidence records;
defined allowed lifecycle state transitions;
defined blocked lifecycle state transitions;
defined required evidence before state changes;
defined representation rules for pending records;
defined representation rules for incomplete records;
defined representation rules for failed records;
defined representation rules for repair-required records;
defined representation rules for repaired records;
defined representation rules for superseded records;
defined representation rules for finalized records;
defined representation rules for voided records;
explicitly blocked finalization without real validation evidence;
explicitly separated lifecycle state changes from release, package, deployment, and production-readiness claims;
preserved Mini-EPIC 32.35 as the lifecycle entry point;
updated docs\architecture\EPIC_32_RELEASE_PIPELINE.md with a concise Mini-EPIC 32.36 summary.
Allowed Lifecycle States

Future release-candidate evidence records may use these states:

StateStatus
createdDocumented
pending_validationDocumented
validation_recordedDocumented
failedDocumented
repair_requiredDocumented
repairedDocumented
supersededDocumented
finalizedDocumented
voidedDocumented
Allowed Lifecycle Transitions

Allowed lifecycle transitions were documented in docs\architecture\EPIC_32_RELEASE_PIPELINE.md.

The transition model requires explicit evidence for movement between lifecycle states and preserves the Mini-EPIC 32.35 creation gate as the only lifecycle entry point.

Blocked Lifecycle Transitions

Blocked lifecycle transitions were documented in docs\architecture\EPIC_32_RELEASE_PIPELINE.md.

The most important blocked transition is:

created -> finalized

This is blocked because record creation is not validation evidence.

Finalization requires real validation evidence and cannot occur merely because a file exists.

Required Transition Evidence

A future lifecycle transition must identify:

previous lifecycle state;
new lifecycle state;
reason for transition;
actor or process responsible for the transition;
timestamp or run reference when applicable;
evidence source or document reference;
validation command or CI run reference when validation is involved;
explicit pass, fail, blocked, repaired, superseded, or voided result;
statement that the transition does not imply release, package, deployment, or production readiness.
Finalization Rule

A future evidence record may enter finalized only after real validation evidence has been recorded and checked.

The following are not sufficient for finalization:

file existence;
template completion;
manually checked boxes without real evidence;
creation gate passage alone;
repair completion without revalidation;
superseded record references;
unsupported release-readiness language.
Non-Release Boundary

Mini-EPIC 32.36 is documentation and governance only.

It does not create or validate a release candidate.

It does not generate, publish, deploy, promote, or release anything.

It does not alter runtime, CLI, CI, package manifest schema, or release identity behavior.

Validation Evidence

Only the targeted release manifest dry-run test is required for this mini-epic as a non-release baseline.

Command:

 = "src"
pytest -q tests\test_release_manifest_dry_run.py --basetemp=.pytest_tmp

Expected result:

targeted dry-run test passes
Closure Criteria Review
CriteriaStatus
main and origin/main aligned before work beganPassed
Working tree clean before documentation updatePassed
Mini-EPIC 32.35 creation gate referencedPassed
Allowed lifecycle states documentedPassed
Allowed lifecycle state transitions documentedPassed
Blocked lifecycle state transitions documentedPassed
Required transition evidence definedPassed
Finalization blocked without real validation evidencePassed
Lifecycle state changes separated from release/package/deployment/production claimsPassed
EPIC 32 document updatedPassed
Closure document createdPassed
Targeted release manifest dry-run test required as non-release baselinePending command result
Final Status

Mini-EPIC 32.36 is closed as documentation and governance only. Targeted validation passed.

It defines a controlled lifecycle state transition model for future release-candidate evidence records while preserving the non-release, non-package, non-deployment, and non-production-readiness boundary.