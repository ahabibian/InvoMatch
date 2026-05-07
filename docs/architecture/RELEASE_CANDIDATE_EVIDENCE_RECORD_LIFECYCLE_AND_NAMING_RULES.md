
Release Candidate Evidence Record Lifecycle and Naming Rules
Status

Documentation-only governance rules.

This document defines future lifecycle and naming rules for release-candidate evidence execution records.

It does not create a real release candidate, does not create a real release-candidate evidence record instance, does not execute validation, does not generate a package, does not publish artifacts, does not introduce automation, does not modify runtime or CI behavior, and does not claim release-candidate or production readiness.

Relationship to the Reusable Template

These rules build on the reusable evidence execution record template introduced in Mini-EPIC 32.26.

Template reference:

Reusable evidence execution record template introduced in Mini-EPIC 32.26

The template defines the expected structure of a future evidence execution record.

This lifecycle document defines how such future records are named, opened, updated, superseded, abandoned, repaired, closed, and referenced.

Record Naming Convention

Future release-candidate evidence execution records must use a deterministic, auditable filename.

Required filename pattern:

RELEASE_CANDIDATE_EVIDENCE_RECORD_<RECORD_ID>.md

Required record identifier pattern:

RCER-YYYYMMDD-NNN

Where:

RCER means Release Candidate Evidence Record.
YYYYMMDD is the date the record is opened.
NNN is a three-digit sequence number for that date, starting at 001.

Example future filename:

RELEASE_CANDIDATE_EVIDENCE_RECORD_RCER-20260507-001.md

Filename rules:

The filename must include the full record identifier.
The filename must not be reused after closure, abandonment, or supersession.
The filename must not imply release approval, package publication, deployment, or production readiness.
The filename must not use ambiguous words such as final, approved, production, deployed, or released unless those words are part of an explicitly documented non-claiming historical note.
Record Identifier Rules

Every future evidence record must include a stable record identifier inside the document body.

Required field:

Evidence Record ID: RCER-YYYYMMDD-NNN

The record identifier is immutable after the record is opened.

The identifier must be used consistently in:

the record filename
the evidence record body
the release candidate evidence index
supersession references
abandonment references
repair references
closure references
Lifecycle States

Future evidence records must use one explicit lifecycle state at a time.

Allowed lifecycle states:

Opened
In Progress
Blocked
Repair In Progress
Superseded
Abandoned
Closed - Passed
Closed - Failed
Closed - Not Executed

Lifecycle state rules:

Opened means the record has been created but evidence capture has not yet started.
In Progress means evidence capture or validation documentation is actively being recorded.
Blocked means the record cannot currently proceed because of a known issue, missing prerequisite, failed gate, missing evidence, or unresolved ambiguity.
Repair In Progress means the same record is still valid and is being updated after a repair that remains within the same validation attempt boundary.
Superseded means a newer evidence record replaces this record for the same intended validation purpose.
Abandoned means the record will not be completed and will not be used as release-candidate evidence.
Closed - Passed means all explicitly required evidence for that record passed within its declared scope.
Closed - Failed means the record is historically closed with one or more failed checks, failed gates, or unresolved blocking outcomes.
Closed - Not Executed means the record was closed without executing the intended validation attempt.
Opening a Future Record

A future evidence record may be opened only when there is a clear intended validation purpose.

When opened, the record must declare:

evidence record ID
opened date
intended validation scope
source commit or declared source identity expectation
expected validation gates
non-release boundary
evidence index reference expectation

Opening a record does not imply validation has started.

Opening a record does not imply release-candidate readiness.

Opening a record does not imply package creation, artifact publication, deployment, automation, or production readiness.

Required opening status language:

Status: Opened
This record has been opened for future evidence capture only. It does not claim release-candidate readiness, package generation, artifact publication, deployment, automation, or production readiness.
In-Progress Rules

A record may move to In Progress only when evidence capture has begun.

Evidence capture may include:

command evidence
validation output
environment metadata
commit identity
CI run metadata
failure notes
repair notes
reviewer notes

An in-progress record must not be represented as closed, passed, released, deployed, or production-ready.

Required in-progress status language:

Status: In Progress
Evidence capture is in progress. No release-candidate, package, deployment, automation, or production-readiness claim is made.
Blocked Rules

A record must move to Blocked when the intended evidence cannot proceed safely or truthfully.

Blocking causes may include:

validation failure
missing prerequisite evidence
environment mismatch
unresolved CI/local drift
missing source identity
failed release gate
incomplete evidence capture
repository state ambiguity
package boundary ambiguity

A blocked record remains auditable and must not be deleted.

Required blocked status language:

Status: Blocked
This record is blocked and cannot be used as release-candidate evidence unless the block is repaired or the record is superseded by a new evidence record.
Repair Versus New Record Rules

A failed or blocked record may be repaired only when the repair remains within the same validation attempt boundary.

A repair may remain in the same record when:

the same intended evidence attempt is still active
the same record ID still truthfully describes the validation attempt
the source identity can be clearly traced
the failed step and repair step are both documented
the evidence index can describe the record without ambiguity
no closed record is being rewritten

A new record must be created when:

the original record has already been closed
the original record has been abandoned
the original record has been superseded
the validation attempt is restarted from a new source commit after material repair
the intended validation scope changes
the evidence boundary changes
the record would become misleading if repaired in place
multiple failed attempts would become difficult to audit inside one record

Repair is not allowed to hide or remove failed evidence.

Repair notes must preserve:

the original failure
the repair action
the repair commit or source identity if applicable
the re-check evidence
the final state after repair

Required repair status language:

Status: Repair In Progress
This record remains open for repair evidence. Previous failure evidence must remain visible and must not be removed or rewritten as if it did not occur.
Supersession Rules

A record may be superseded when a newer record replaces it for the same intended evidence purpose.

Supersession is appropriate when:

a cleaner validation attempt is started
the source commit changes materially
the original record became too noisy or ambiguous
the original record was blocked but still historically relevant
the validation scope must be restarted

A superseded record must remain in the repository unless there is a separate documented reason to remove it.

A superseded record must reference the replacing record ID.

The replacing record must reference the superseded record ID.

Required superseded status language:

Status: Superseded
This record has been superseded by <NEW_RECORD_ID>. It remains historical evidence and must not be treated as the active release-candidate evidence record.
Abandonment Rules

A record may be abandoned when the intended evidence attempt will not continue and no replacement record is immediately designated.

Abandonment is appropriate when:

the validation attempt is cancelled
the intended scope is no longer relevant
the record was opened prematurely
prerequisites were not available
the attempt should not be repaired or superseded yet

An abandoned record must remain auditable.

An abandoned record must not be reused later.

Required abandoned status language:

Status: Abandoned
This record was abandoned and must not be used as release-candidate evidence. It remains historical documentation only.
Closure Rules

A record may be closed only when its final evidence state is known.

Allowed closure outcomes:

Closed - Passed
Closed - Failed
Closed - Not Executed

Closed records are immutable historical evidence.

After closure:

the record ID must not change
the filename must not change
the executed evidence must not be rewritten
failed evidence must not be removed
status must not be changed except by a new explicit supersession note
corrections must be appended as dated historical amendments
a new validation attempt must use a new record ID

Required passed closure language:

Status: Closed - Passed
This record is closed as passed within its declared scope only. This does not by itself claim package publication, deployment, automation, production readiness, or customer release.

Required failed closure language:

Status: Closed - Failed
This record is closed as failed and must not be used as successful release-candidate evidence.

Required not-executed closure language:

Status: Closed - Not Executed
This record is closed without execution and must not be used as validation evidence.
Evidence Index Reference Rules

The release candidate evidence index may reference future records only with explicit lifecycle status.

Every index entry for a future evidence record must include:

evidence record ID
filename or path
lifecycle status
opened date
closed date if applicable
source commit or source identity if applicable
supersedes record ID if applicable
superseded by record ID if applicable
abandonment reason if applicable
final evidence outcome if applicable
explicit non-release boundary statement

The index must not list an opened, blocked, abandoned, superseded, failed, or not-executed record as successful release-candidate evidence.

The index may preserve non-successful records for audit traceability.

Immutability Expectations

Closed records are immutable historical evidence.

Immutability means:

no rewriting passed evidence
no deleting failed evidence
no renaming the record to imply approval
no changing the original lifecycle timeline
no replacing source identity after closure
no converting a failed record into a passed record

Permitted post-closure changes:

append-only correction notes
append-only supersession notes
typo corrections that do not change evidence meaning
index reference updates that preserve historical status

Any post-closure amendment must be dated and must not hide the original record state.

Non-Release Boundary

These lifecycle and naming rules are governance documentation only.

They do not:

create a real release candidate
create a real release-candidate evidence record instance
execute validation packs
generate a package
publish artifacts
introduce release automation
deploy anything
modify CLI behavior
modify manifest schema
modify runtime code
change validation behavior
change CI behavior
claim release-candidate readiness
claim production readiness
Mini-EPIC 32.27 Outcome

Mini-EPIC 32.27 defines future evidence record lifecycle and naming rules so later records can remain traceable, auditable, and safe to reference across failed, repaired, superseded, abandoned, or completed validation attempts.

No actual release-candidate evidence instance is created by this document.
