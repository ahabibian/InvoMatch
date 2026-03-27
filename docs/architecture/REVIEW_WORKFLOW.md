# EPIC 5 - Review Workflow

## Purpose
Define the operational workflow that governs how raw feedback moves through review, audit, and learning eligibility decisions.

This workflow exists to prevent unsafe direct propagation from user correction to learning behavior.

---

## Workflow Objective
The review workflow must ensure that:
- raw feedback is captured safely
- review decisions are explicit
- audit events are generated consistently
- learning eligibility is derived only after valid review outcomes
- unresolved or rejected items cannot influence downstream learning

---

## High-Level Flow

1. Feedback is captured from a user correction event.
2. Raw feedback is persisted in the feedback store.
3. A review item is created and linked to a review session.
4. The review item enters the review queue.
5. A reviewer evaluates the item with source context.
6. The reviewer selects a decision:
   - APPROVE
   - REJECT
   - MODIFY
   - DEFER
7. The system persists the review decision event.
8. The system writes a corresponding audit event.
9. The system updates the current review item state.
10. The system derives learning eligibility from the reviewed state.
11. The item is either closed, deferred, or reopened later if needed.

---

## Workflow Stages

### Stage 1 - Feedback Capture
Input:
- user correction
- workflow context
- source reference

Output:
- FeedbackRecord persisted
- feedback_status = CAPTURED

Requirements:
- raw payload must be stored unchanged
- source context reference must be retained
- no learning action may happen here

---

### Stage 2 - Review Queue Insertion
Input:
- captured feedback record

Output:
- ReviewItem created
- ReviewSession assigned or created
- feedback_status = QUEUED_FOR_REVIEW

Requirements:
- every review item must reference exactly one raw feedback record
- queue insertion must not imply reviewer approval
- queue state must be queryable

---

### Stage 3 - Review Assignment
Input:
- queued review item

Output:
- assigned reviewer
- session_status may become IN_PROGRESS

Requirements:
- reviewer assignment must be traceable
- assignment changes should produce audit evidence
- assignment does not change learning eligibility

---

### Stage 4 - Review Evaluation
Input:
- review item
- raw feedback
- source context
- matching context if available

Output:
- reviewer decision candidate

Requirements:
- reviewer must evaluate against context, not isolated payload only
- review item must support approve, reject, modify, defer
- evaluation may produce comments or reason text

---

### Stage 5 - Decision Persistence
Input:
- reviewer decision

Output:
- ReviewDecisionEvent persisted
- ReviewItem current state updated

Requirements:
- previous state and new state must be captured
- modified decisions must preserve reviewed payload separately
- rejected items must remain ineligible for learning

---

### Stage 6 - Audit Recording
Input:
- persisted review decision event

Output:
- AuditEvent persisted

Requirements:
- actor, timestamp, action, and target entity must be recorded
- audit records must be append-only in business terms
- audit event must remain available even if current state changes later

---

### Stage 7 - Learning Eligibility Derivation
Input:
- current reviewed state

Output:
- LearningEligibilityRecord created or updated

Rules:
- APPROVED -> potentially ELIGIBLE
- MODIFIED -> potentially ELIGIBLE using reviewed payload
- REJECTED -> INELIGIBLE
- DEFERRED -> PENDING / INELIGIBLE until resolved
- REOPENED -> prior eligibility may need invalidation

Requirements:
- eligibility must be derived, not manually assumed
- raw payload must never bypass reviewed state

---

### Stage 8 - Closure or Follow-Up
Input:
- final or temporary review state

Output:
- item closed, deferred, or reopened

Requirements:
- APPROVED / REJECTED / MODIFIED may close an item
- DEFERRED keeps the item unresolved
- REOPEN must generate new decision and audit history
- closed sessions must not hide unresolved items silently

---

## Decision Paths

### APPROVE Path
1. feedback captured
2. review item created
3. reviewer approves
4. decision event stored
5. audit event stored
6. item marked APPROVED
7. eligibility derived as ELIGIBLE or policy-qualified

### REJECT Path
1. feedback captured
2. review item created
3. reviewer rejects
4. decision event stored
5. audit event stored
6. item marked REJECTED
7. eligibility derived as INELIGIBLE

### MODIFY Path
1. feedback captured
2. review item created
3. reviewer modifies reviewed payload
4. modified payload stored separately
5. decision event stored
6. audit event stored
7. item marked MODIFIED
8. eligibility derived from reviewed payload, not raw payload

### DEFER Path
1. feedback captured
2. review item created
3. reviewer defers decision
4. decision event stored
5. audit event stored
6. item marked DEFERRED
7. eligibility remains pending or ineligible until follow-up

### REOPEN Path
1. previously reviewed item is reopened
2. prior state remains in history
3. new review cycle begins
4. new decision event must be recorded
5. prior eligibility may be invalidated if necessary

---

## State Transition Rules

### Allowed ReviewItem Transitions
- PENDING -> IN_REVIEW
- IN_REVIEW -> APPROVED
- IN_REVIEW -> REJECTED
- IN_REVIEW -> MODIFIED
- IN_REVIEW -> DEFERRED
- DEFERRED -> IN_REVIEW
- APPROVED -> REOPENED (logical transition via decision event)
- REJECTED -> REOPENED (logical transition via decision event)
- MODIFIED -> REOPENED (logical transition via decision event)

### Forbidden Transitions
- PENDING -> ELIGIBLE directly
- CAPTURED -> ELIGIBLE directly
- REJECTED -> ELIGIBLE without explicit re-review
- DEFERRED -> ELIGIBLE without explicit resolution

---

## Audit Points
Audit events should be generated at minimum for:
- review item creation
- reviewer assignment
- decision submission
- decision modification
- defer action
- reopen action
- learning eligibility creation
- learning eligibility invalidation

---

## Failure Handling
The workflow must define safe behavior for partial failures:

### If decision persistence fails
- no audit event should claim success
- review state must remain unchanged

### If audit persistence fails
- the system should not silently finalize the review outcome
- the failure should be surfaced for recovery handling

### If eligibility derivation fails
- reviewed state may be stored
- eligibility must remain unresolved until derivation is completed safely

---

## Operational Constraints
- Review workflow must be deterministic enough for audit reconstruction.
- Business state must be reconstructable from persisted evidence.
- Learning must be downstream of reviewed state, never parallel to it.
- Review throughput optimization must not weaken control boundaries.

---

## Deliverable Outcome
This workflow defines the operational contract for how review moves from raw feedback capture to audit-backed learning eligibility.

It is not the final API specification or storage schema.
It is the workflow-level architecture required before implementation.