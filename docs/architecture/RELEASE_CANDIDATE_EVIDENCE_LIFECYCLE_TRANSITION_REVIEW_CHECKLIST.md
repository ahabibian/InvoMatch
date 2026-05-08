# Release Candidate Evidence Lifecycle Transition Review Checklist

Status: Governance checklist

Related mini-epics:

- Mini-EPIC 32.35 - Release Candidate Evidence Record Creation Gate Definition
- Mini-EPIC 32.36 - Release Candidate Evidence Record Lifecycle State Transition
- Mini-EPIC 32.37 - Release Candidate Evidence Lifecycle Transition Review Checklist

## Purpose

This checklist defines the review that must be completed before any future release-candidate evidence record lifecycle state transition may be accepted.

The checklist converts lifecycle transition policy into a practical governance control. It does not execute a transition by itself, does not create a release candidate, does not create an evidence record instance, does not execute validation packs, and does not claim release-candidate readiness or production readiness.

## Review Boundary

The review is limited to documentation governance for future release-candidate evidence records.

It must not be treated as:

- a release event
- a package generation event
- an artifact publication event
- a deployment event
- a staging or production promotion
- a CI execution
- validation-pack evidence
- release-candidate readiness
- production readiness

## Required Inputs

A lifecycle transition review must have the following inputs before it can be accepted:

- the evidence record identifier
- the current lifecycle state
- the requested target lifecycle state
- the transition requester or owner
- the reason for the transition
- the evidence record location
- the applicable lifecycle transition rules from Mini-EPIC 32.36
- the applicable creation gate reference from Mini-EPIC 32.35
- any validation evidence required by the target state
- any repair or supersession references required by the target state

## Source State Verification

Before reviewing the target state, the reviewer must verify the source state.

| Check | Required outcome |
|---|---|
| Evidence record exists | The referenced evidence record is identifiable and reviewable. |
| Current state is explicit | The record declares exactly one current lifecycle state. |
| Current state is known | The declared current state belongs to the approved lifecycle state set. |
| Current state is not inferred | The current state is read from the record, not guessed from filenames or surrounding context. |
| Current state history is visible | Prior transitions, if any, remain visible and are not overwritten or hidden. |
| Failed or incomplete evidence remains visible | Failures, gaps, or incomplete sections are not removed to make the transition look clean. |

## Target State Verification

The reviewer must verify that the requested target state is valid and meaningful.

| Check | Required outcome |
|---|---|
| Target state is explicit | The requested target state is named directly. |
| Target state is valid | The target state belongs to the approved lifecycle state set. |
| Target state is not ambiguous | The request does not combine multiple target states. |
| Target state has a documented reason | The transition reason explains why this state is being requested. |
| Target state does not imply release readiness unless separately proven | No lifecycle state may be used to imply package, deployment, release-candidate, or production readiness. |

## Approved Lifecycle State Set

The lifecycle review checklist recognizes the following states:

- created
- pending_validation
- validation_recorded
- failed
- repair_required
- repaired
- superseded
- voided
- finalized

Any requested transition involving an unknown state must be rejected.

## Allowed Transition Verification

The reviewer must verify that the requested transition is allowed by the lifecycle rules defined in Mini-EPIC 32.36.

| Check | Required outcome |
|---|---|
| Transition pair is allowed | The source-to-target state pair is explicitly allowed. |
| Transition is not invented for convenience | The reviewer must not create ad hoc transition paths. |
| Transition does not skip required review | A record cannot bypass validation, repair, supersession, or voiding requirements. |
| Transition does not hide failed evidence | Failure states must remain traceable even after repair or supersession. |
| Transition preserves audit continuity | The transition must add traceability rather than rewrite the record history. |

## Blocked Transition Detection

The reviewer must reject blocked or unsafe transitions.

| Blocked condition | Required review response |
|---|---|
| Unknown source state | Reject transition. |
| Unknown target state | Reject transition. |
| Missing evidence record identifier | Reject transition. |
| Missing transition reason | Reject transition. |
| Missing required evidence for target state | Reject transition. |
| Attempt to move directly from repaired to finalized without revalidation | Reject transition. |
| Attempt to finalize from failed, repair_required, superseded, or voided | Reject transition. |
| Attempt to supersede without replacement reference | Reject transition. |
| Attempt to void while hiding why the record is voided | Reject transition. |
| Attempt to finalize using only file existence or manual checklist completion | Reject transition. |
| Attempt to treat governance review as release execution | Reject transition. |

## Required Evidence Presence

The reviewer must verify that the target state has the evidence required for that state.

| Target state | Required evidence review |
|---|---|
| created | Creation gate reference is present and the record identity is clear. |
| pending_validation | The record identifies the validation expected but does not claim execution. |
| validation_recorded | Real validation output is present and tied to the evidence record. |
| failed | Failure evidence is visible, including failed step or failed validation result. |
| repair_required | The reason repair is required is explicit and traceable to evidence. |
| repaired | Repair action is described, but the record is not treated as finalized until revalidated. |
| superseded | Replacement record or successor reference is identified. |
| voided | The void reason is explicit and the record is not reused as valid evidence. |
| finalized | Real validation evidence is present and reviewable. |

## Failed and Incomplete Evidence Handling

Failed or incomplete evidence must not be hidden, deleted, renamed into success, or replaced by summary language that removes the original failure context.

The reviewer must confirm:

- failed validation remains visible
- incomplete validation remains visible
- missing evidence is recorded as missing, not implied as complete
- failed records do not move to finalized
- repair_required records do not move to finalized
- failure history remains traceable after repair or supersession

## Repaired Record Handling

A repaired record may not move directly to finalized.

The reviewer must confirm:

- the repair action is described
- the original failure or gap remains visible
- the repaired record returns to a validation-required state before finalization
- new validation evidence exists after repair
- the finalization decision uses post-repair validation evidence, not the existence of the repair note

## Superseded Record Handling

A superseded record must identify the replacement or successor evidence record.

The reviewer must confirm:

- the superseded record remains preserved for audit
- the replacement record is named or otherwise traceable
- the superseded record is not treated as finalized
- the superseded record is not used as current release evidence
- the supersession reason is documented

## Voided Record Handling

A voided record must remain visible but must not be reused as valid release-candidate evidence.

The reviewer must confirm:

- the void reason is explicit
- the record is not deleted
- the record is excluded from final evidence claims
- the record is not silently replaced
- the voided state does not imply successful validation

## Finalized Record Handling

Finalized is the strictest review state.

A finalized record must contain real validation evidence. File existence, document existence, manual checklist completion, or policy agreement is not enough.

The reviewer must confirm:

- validation evidence is real and reviewable
- validation output is connected to the evidence record
- failed or incomplete checks are not hidden
- any repair was followed by revalidation
- any superseded or voided predecessor remains traceable
- finalization does not claim package generation
- finalization does not claim artifact publication
- finalization does not claim deployment
- finalization does not claim production readiness

## Governance Decision Outcomes

A lifecycle transition review may result in one of the following governance outcomes:

| Outcome | Meaning |
|---|---|
| Accepted | The requested transition satisfies the checklist and may be recorded. |
| Rejected | The requested transition violates one or more checklist rules. |
| Needs evidence | The transition cannot be accepted until required evidence is added. |
| Needs repair | The record contains defects that must be repaired before further transition. |
| Needs supersession | The record should not continue and must be replaced by a successor record. |
| Needs voiding | The record must remain visible but must not be used as valid evidence. |

## Non-Release Statement

Completing this checklist is a governance control only.

It does not create a release candidate, does not execute validation, does not generate a package, does not publish artifacts, does not deploy anything, does not promote to staging or production, and does not establish release-candidate or production readiness.
