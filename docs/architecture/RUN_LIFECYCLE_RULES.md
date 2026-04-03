# RUN_LIFECYCLE_RULES

Status: Proposed

## Purpose
This document defines the operational lifecycle guard rules for InvoMatch runs.

RUN_STATE_MACHINE.md defines which state-to-state transitions are allowed.
This document defines which product operations are legal while a run is in a given state.

The purpose of lifecycle rules is to prevent invalid behavior even when no state transition is being requested directly.

Examples:
- export must be rejected if the run is not in an export-eligible state
- review resolution must be rejected if the run is not in review_required
- cancellation must be rejected if the run is already terminal

This document is the policy foundation for lifecycle guards in the service layer.

## Design Principles

### 1. Operations Must Be State-Aware
Every lifecycle-sensitive operation must validate the current run state before execution.

### 2. Transition Validation and Operation Validation Are Different
A valid state transition does not automatically mean every operation is legal in that state.
State transition control and operation guard control must remain separate concerns.

### 3. Guard Failures Must Be Explicit
Invalid operations must fail with clear lifecycle errors. Silent no-op behavior is forbidden.

### 4. Terminal Runs Are Operationally Restricted
A terminal run may still support read access, but write-like lifecycle operations must be rejected.

### 5. Lifecycle Policy Must Be Reusable
Guard logic must not be duplicated inconsistently across routes, handlers, and services. It must be centralized and reusable.

## Lifecycle-Sensitive Operations

This document governs at least the following operation categories:

- processing start
- review access
- review resolution
- export execution
- cancellation
- failure transition handling
- completion/finalization
- action dispatch requiring lifecycle eligibility

## State-by-State Operational Rules

## queued

Allowed:
- read run details
- start processing
- transition to failed if initialization fails
- transition to cancelled if cancellation is accepted by policy

Not allowed:
- export
- review resolution
- completion
- review-required actions

Operational interpretation:
queued means the run exists but has not entered active execution.

## processing

Allowed:
- read run details
- continue controlled processing work
- transition to review_required when review conditions are detected
- transition to completed when processing finishes cleanly and no review is required
- transition to failed on controlled unrecoverable processing failure
- transition to cancelled if cancellation is permitted by policy

Not allowed:
- export
- review resolution as a final human decision flow
- direct rollback to queued

Operational interpretation:
processing is the only active execution state in the current lifecycle model.

## review_required

Allowed:
- read run details
- read review data
- resolve review items through controlled review flows
- transition to completed once all review obligations are satisfied
- transition to failed if review-stage failure policy triggers
- transition to cancelled if product policy allows cancellation at this stage

Not allowed:
- export unless a future policy explicitly allows it
- restart processing by direct lifecycle mutation
- bypass review and force completion without controlled policy

Operational interpretation:
review_required means automated execution has paused at a human decision boundary.

## completed

Allowed:
- read run details
- read review outcomes
- execute export if export policy requires completed state
- read export metadata and artifacts if they exist

Not allowed:
- cancellation
- reprocessing
- review reopening through uncontrolled mutation
- transition to any other lifecycle state

Operational interpretation:
completed is a terminal success state with downstream read/export eligibility.

## failed

Allowed:
- read run details
- inspect failure information
- read audit/history data if available

Not allowed:
- export
- review resolution
- completion
- processing re-entry
- cancellation after failure
- transition to any other lifecycle state

Operational interpretation:
failed is a terminal non-success state.

## cancelled

Allowed:
- read run details
- inspect lifecycle history and cancellation context if available

Not allowed:
- export
- review resolution
- completion
- processing re-entry
- transition to any other lifecycle state

Operational interpretation:
cancelled is a terminal administrative stop state.

## Operation Eligibility Matrix

| Operation              | queued | processing | review_required | completed | failed | cancelled |
|-----------------------|--------|------------|-----------------|-----------|--------|-----------|
| Read run              | yes    | yes        | yes             | yes       | yes    | yes       |
| Start processing      | yes    | no         | no              | no        | no     | no        |
| Continue processing   | no     | yes        | no              | no        | no     | no        |
| Escalate to review    | no     | yes        | no              | no        | no     | no        |
| Resolve review        | no     | no         | yes             | no        | no     | no        |
| Finalize completed    | no     | yes        | yes             | no        | no     | no        |
| Mark failed           | yes    | yes        | yes             | no        | no     | no        |
| Cancel run            | yes    | yes*       | yes*            | no        | no     | no        |
| Export run            | no     | no         | no              | yes       | no     | no        |

\* cancellation during processing or review_required is policy-controlled and must be explicitly validated by the lifecycle layer.

## Export Eligibility Rules

Export is a guarded operation, not a lifecycle transition.

Rules:
- export must be rejected unless the run is in completed
- export must not mutate lifecycle state as a side effect
- export services must validate lifecycle eligibility before generating artifacts
- export handlers must not define their own inconsistent eligibility logic

The initial policy for EPIC 12 is strict:
- completed = export allowed
- all other states = export rejected

If this policy changes later, it must be updated in both architecture and tests.

## Review Operation Rules

Review operations must be allowed only when the run is in review_required, unless a future read-only exception is introduced explicitly.

Rules:
- review resolution requires review_required
- review closure requires review_required
- review-driven completion may occur only through controlled lifecycle finalization
- completed runs may expose historical review results as read-only data
- queued, processing, failed, and cancelled runs must reject review resolution actions

## Action Dispatch Rules

Any action handler that can affect lifecycle-sensitive behavior must validate run eligibility first.

Rules:
- action dispatch must not assume the current state is valid
- action handlers must use lifecycle guard checks before side effects
- action handlers must never bypass lifecycle transition control
- illegal action requests must fail explicitly and predictably

## Cancellation Rules

Cancellation is allowed only when the run is non-terminal and policy permits the interruption.

Rules:
- completed, failed, and cancelled runs must reject cancellation
- queued may allow cancellation
- processing may allow cancellation only through controlled policy
- review_required may allow cancellation only through controlled policy
- cancellation must transition the run to cancelled through lifecycle control, not direct mutation

## Failure Rules

Failure is a controlled lifecycle outcome.

Rules:
- failure may be entered from queued, processing, or review_required
- failure must be explicit and auditable
- terminal failure must block export and further lifecycle progression
- failure handling must not leave the run in ambiguous partial status

## Completion Rules

Completion is allowed only when lifecycle obligations are satisfied.

Rules:
- processing may transition directly to completed only if no review is required
- review_required may transition to completed only after all required review obligations are resolved
- completion must be rejected for queued, failed, cancelled, and already completed runs
- completion must go through lifecycle transition control

## Guard Layer Responsibilities

The lifecycle guard layer is responsible for:
- validating whether an operation is allowed for the current run state
- providing reusable policy checks to services and handlers
- raising explicit lifecycle errors on invalid usage
- keeping operational policy centralized

The guard layer is not responsible for:
- mutating the run state directly
- replacing the transition controller
- embedding unrelated business logic
- deciding review content or export file format

## Error Model Expectations

Lifecycle enforcement should distinguish at least the following categories:

- operation not allowed for current state
- illegal transition
- terminal state mutation attempt
- unknown lifecycle state
- invalid lifecycle target
- cancellation not permitted by policy
- export not allowed for current state
- review operation not allowed for current state

Exact class names may differ in implementation, but the categories must remain explicit.

## Service Integration Expectations

The following integration rules are mandatory:

- routes must call services that validate lifecycle rules
- services must not duplicate inconsistent guard logic
- action handlers must check lifecycle eligibility before side effects
- export execution must validate completed-state eligibility
- review services must validate review_required-state eligibility
- lifecycle mutation must remain centralized in a dedicated lifecycle transition service or equivalent component

## Testing Requirements

The following test categories are mandatory:

### Guard Rule Tests
- export rejected outside completed
- review resolution rejected outside review_required
- cancellation rejected for terminal states
- processing start rejected outside queued

### Integration Tests
- action handlers fail correctly on invalid state
- export services fail correctly on invalid state
- review flows respect lifecycle boundaries
- successful operations remain allowed in the correct states

### Error Behavior Tests
- lifecycle guard failures are explicit
- terminal-state violations are distinguishable
- operation-level policy remains deterministic

## Summary

InvoMatch lifecycle integrity depends on two separate but connected controls:

1. the state machine defines allowed lifecycle transitions
2. the lifecycle rules define which operations are legal in each state

No lifecycle-sensitive action may execute without validating the current run state.
No service may bypass lifecycle policy through direct status mutation or duplicated ad hoc logic.