# STATE TRANSITION INTEGRATION

## Purpose

This document defines how product-facing actions integrate with internal workflow state transitions.

It establishes:

- Allowed transitions
- Forbidden transitions
- Review-to-run impact rules
- Export workflow boundaries
- Deterministic repeated-action behavior

This document exists to prevent implicit or inconsistent state mutation.

---

## Scope

This document covers:

- Review resolution transitions
- Run impact caused by review resolution
- Export-related workflow behavior
- Idempotency rules for repeated actions

This document does NOT redefine the public API contract.

---

## Transition Design Principles

### 1. Explicitness
All state transitions must be explicitly defined.

No action may mutate workflow state unless the transition is documented and allowed.

### 2. Determinism
The same action against the same current state must produce the same outcome.

### 3. Validation Before Mutation
Eligibility must be checked before any transition occurs.

### 4. No Silent Recovery
Invalid transitions must fail explicitly.

### 5. Separation of Main Workflow and Side Workflow
Export should be treated as a side workflow unless a strong reason exists to mutate the main run lifecycle.

---

## Review State Model

Minimum review states assumed:

- PENDING
- RESOLVED

Resolution metadata must capture the actual decision.

Example decision values:

- APPROVED
- REJECTED
- NEEDS_CHANGES

If the current implementation uses fewer decision types, the system must still preserve deterministic handling.

---

## Review Resolution Transition Rules

### Allowed Transition

PENDING → RESOLVED

Conditions:

- Review exists
- Review is currently pending
- Resolution decision is valid
- Action is authorized by workflow rules

Effects:

- Review state changes to RESOLVED
- Resolution metadata is recorded
- Audit event is emitted
- Related run may be updated if policy requires it

---

### Forbidden Transitions

The following transitions are forbidden:

- RESOLVED → RESOLVED with different decision
- RESOLVED → PENDING
- Missing review → any transition
- Invalid decision value → any transition

These must fail explicitly and must not create side effects.

---

## Repeated Resolve Behavior

Repeated resolve must be deterministic.

### Case 1 — Same decision repeated
If a review is already RESOLVED with the same decision:

- No new mutation
- No duplicate side effects
- Return deterministic no-op or already-resolved result

### Case 2 — Different decision repeated
If a review is already RESOLVED with a different decision:

- Reject action
- Return controlled conflict result
- Do not mutate review
- Do not emit duplicate workflow side effects

---

## Review-to-Run Integration

Review resolution may affect the related run.

This must be policy-driven and explicit.

### Recommended Rule

If a run is in review-gated state such as:

- AWAITING_REVIEW

Then review resolution may allow transition to one of the following:

- READY_FOR_EXPORT
- COMPLETED
- REVIEW_RESOLVED

The exact target depends on the existing run model and must remain consistent with prior lifecycle semantics.

### Constraint

Review resolution must not arbitrarily rewrite unrelated run fields.

Only workflow-relevant fields may change.

---

## Run Transition Rules Triggered by Review Resolution

### Allowed pattern

AWAITING_REVIEW → next eligible terminal or post-review state

Examples:

- AWAITING_REVIEW → COMPLETED
- AWAITING_REVIEW → READY_FOR_EXPORT

### Forbidden pattern

- COMPLETED → AWAITING_REVIEW
- EXPORTED → AWAITING_REVIEW
- FAILED → COMPLETED without explicit recovery flow

If no run transition is required by policy, review resolution must leave run state unchanged.

---

## Export Workflow Boundary

Export must be modeled as a side workflow.

Export should NOT automatically redefine the primary reconciliation lifecycle unless the product model explicitly requires that behavior.

### Recommended export states

- REQUESTED
- COMPLETED
- FAILED

These states belong to the export workflow, not necessarily the main run lifecycle.

---

## Export Eligibility Rules

A run may be exported only if it is in an export-eligible state.

Suggested eligible run states:

- COMPLETED
- READY_FOR_EXPORT
- REVIEW_RESOLVED

Suggested ineligible run states:

- CREATED
- RUNNING
- FAILED
- CANCELLED

Exact eligibility must match the actual run lifecycle model.

---

## Export Transition Behavior

### Allowed export behavior

eligible run
→ export requested
→ artifact generated
→ export completed

Effects:

- Export artifact is created
- Export reference is stored
- Audit event is emitted

### Forbidden export behavior

- Export for missing run
- Export for non-terminal or ineligible run
- Export that silently mutates unrelated workflow state
- Export that generates uncontrolled duplicate artifacts

---

## Repeated Export Behavior

Repeated export requests must be deterministic.

### Recommended behavior

If the same export request is repeated for the same run and format:

- Reuse existing export artifact reference
or
- Return deterministic already-exported result

Do not generate duplicate uncontrolled artifacts unless a future explicit regeneration policy exists.

---

## Failure Handling Rules

### Validation failure
- No mutation
- No artifact generation
- Audit may record failed attempt if policy requires

### Transition failure
- No hidden retries
- No partial undocumented state changes

### Side-effect failure after transition
- Must be visible
- Must be audited
- Must not be silently swallowed

---

## Route-to-Transition Mapping Summary

### Resolve Review
Route action:
POST /reviews/{id}/resolve

Transition:
PENDING → RESOLVED

Possible run effect:
AWAITING_REVIEW → next allowed state

---

### Export Run
Route action:
POST /runs/{id}/export

Transition:
No required main run transition by default

Side workflow:
REQUESTED → COMPLETED
or
REQUESTED → FAILED

---

## Audit Requirements for Transitions

Every successful or failed transition attempt should be traceable.

Minimum audit data:

- action_type
- target_type
- target_id
- actor
- before_state
- after_state
- decision or export format
- execution_status
- timestamp

---

## Risks Prevented by This Document

This transition plan prevents:

- implicit workflow mutation
- handler-specific transition drift
- duplicate side effects
- export incorrectly mutating the run lifecycle
- inconsistent repeated action behavior

---

## Outcome

After applying this transition model:

- review resolution becomes controlled and enforceable
- run effects become explicit
- export remains safely integrated as a side workflow
- repeated actions behave predictably
- action handlers can be implemented without guessing transition semantics