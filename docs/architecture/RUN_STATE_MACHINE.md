# RUN_STATE_MACHINE

Status: Proposed

## Purpose
This document defines the authoritative run state machine for InvoMatch.

The objective is to replace loosely managed status changes with a strictly controlled lifecycle model. A run state is not a convenience field. It is a product-level contract that determines what operations are legal, what transitions are allowed, and when the run becomes immutable.

This document defines:
- the canonical run states
- the allowed transitions between states
- terminal state behavior
- lifecycle invariants
- ownership of state mutation
- integration expectations for services and actions

Operational guard rules are defined in RUN_LIFECYCLE_RULES.md.

## Design Principles

### 1. State Is a Controlled Boundary
Run status must be treated as a controlled lifecycle boundary, not as a mutable implementation detail.

### 2. No Implicit Transition
A run must never change state as a side effect of arbitrary field mutation or route-level logic. Every transition must be explicit and intentional.

### 3. Deterministic Lifecycle
For the same current state and the same requested operation, the outcome must be deterministic and testable.

### 4. Terminal Means Terminal
Completed, failed, and cancelled are terminal states unless a future architecture document explicitly introduces a controlled reopening policy.

### 5. State and Operation Are Separate Concerns
The state machine defines which state-to-state transitions are allowed.
Lifecycle guards define which operations are legal while a run is in a given state.

## Canonical Run States

The run lifecycle is defined by the following canonical product states:

- queued
- processing
- review_required
- completed
- failed
- cancelled

No other product-facing run state is allowed unless this document is revised.

## State Definitions

### queued
The run has been created and accepted by the system but processing has not yet started.

Expected characteristics:
- input payload is registered
- run identity exists
- processing work has not yet been claimed or started
- export is not allowed
- review is not allowed
- cancellation may be allowed by policy

### processing
The run is actively being processed by the matching pipeline or another controlled execution stage.

Expected characteristics:
- work has started
- match evaluation and related processing logic may still modify internal execution data
- export is not allowed
- review resolution is not allowed
- cancellation may be allowed only if supported by lifecycle policy

### review_required
The run has completed automated processing but requires human review before it can be finalized.

Expected characteristics:
- at least one review-triggering condition has been detected
- review items or review cases are open
- export is not allowed unless an explicit policy later allows provisional export
- completion is blocked until review obligations are resolved

### completed
The run has completed successfully and no further lifecycle progression is expected.

Expected characteristics:
- automated processing is complete
- all required review work is complete
- the run is eligible for downstream product flows such as export
- no further state transitions are allowed

### failed
The run ended unsuccessfully due to a controlled failure condition.

Expected characteristics:
- processing cannot continue without a new controlled retry or restart model
- export is not allowed
- no further state transitions are allowed under the current lifecycle model

### cancelled
The run was intentionally stopped before successful completion.

Expected characteristics:
- the run must not continue processing
- export is not allowed
- no further state transitions are allowed under the current lifecycle model

## Authoritative Transition Map

The allowed transitions are:

- queued -> processing
- queued -> failed
- queued -> cancelled

- processing -> review_required
- processing -> completed
- processing -> failed
- processing -> cancelled

- review_required -> completed
- review_required -> failed
- review_required -> cancelled

- completed -> no further transitions
- failed -> no further transitions
- cancelled -> no further transitions

## Transition Matrix

| Current State   | Allowed Target States                     |
|-----------------|-------------------------------------------|
| queued          | processing, failed, cancelled             |
| processing      | review_required, completed, failed, cancelled |
| review_required | completed, failed, cancelled              |
| completed       | none                                      |
| failed          | none                                      |
| cancelled       | none                                      |

## Forbidden Transitions

The following classes of transition are explicitly forbidden:

- queued -> review_required
- queued -> completed
- processing -> queued
- review_required -> processing
- review_required -> queued
- completed -> any state
- failed -> any state
- cancelled -> any state

In general, backward transitions are forbidden unless a future lifecycle version explicitly introduces them with controlled policy and migration semantics.

## Terminal States

The terminal states are:

- completed
- failed
- cancelled

Rules:
- a terminal run must reject further lifecycle transitions
- a terminal run must reject processing re-entry
- a terminal run must not accept review reopening through direct state mutation
- a terminal run may still allow read-only access depending on product surface rules

## Transition Invariants

The following invariants must always hold:

1. A run must always have exactly one canonical lifecycle state.
2. A transition must always originate from a known valid current state.
3. A transition must always target a valid canonical state.
4. A transition must be rejected if it is not in the authoritative transition map.
5. Terminal states must reject all further transitions.
6. No service may bypass lifecycle control by directly mutating run.status.
7. Lifecycle decisions must be enforceable through automated tests.
8. Product-facing behavior must remain consistent with the state machine at all integration points.

## Ownership of State Changes

Run state changes must be owned by a dedicated lifecycle control layer.

That means:
- routes must not mutate run.status directly
- action handlers must not mutate run.status directly
- export services must not mutate run.status directly
- review services must not mutate run.status directly unless delegated through lifecycle control
- reconciliation orchestration must use controlled transition APIs

The lifecycle control layer becomes the single authority for:
- validating requested transitions
- applying allowed transitions
- rejecting illegal transitions
- enforcing terminal state behavior

## Integration Points

The state machine must be integrated with the following product flows:

### Run Creation
A newly created run must start in queued.

### Processing Start
When controlled execution begins, the run transitions from queued to processing.

### Review Escalation
If automated processing determines that human intervention is required, the run transitions from processing to review_required.

### Successful Finalization
If processing completes with no review requirement, or after required review is resolved, the run transitions to completed.

### Failure Handling
If a controlled unrecoverable error occurs, the run transitions to failed.

### Cancellation
If a valid cancellation request is accepted before terminal completion, the run transitions to cancelled.

### Export Eligibility
Export must not be treated as a transition itself. Export is an operation whose eligibility depends on lifecycle state and guard rules.

## Error Semantics

Illegal lifecycle behavior must fail explicitly.

The lifecycle layer must distinguish at least between:
- unknown state
- invalid target state
- illegal transition
- terminal state mutation attempt
- operation not allowed for current state

Exact exception class names may be defined in implementation, but the behavior must be explicit and testable.

## Implementation Expectations

Implementation must introduce a dedicated lifecycle enforcement structure, expected to include:
- transition policy definition
- lifecycle error model
- lifecycle guard layer
- controlled lifecycle service or equivalent transition controller

The implementation must ensure that direct run.status mutation is removed or blocked across service-layer workflows.

## Testing Requirements

The following test categories are mandatory:

### State Machine Tests
- valid transitions are accepted
- invalid transitions are rejected
- terminal states reject further transitions

### Guard Integration Tests
- export eligibility is enforced by state
- review operations are enforced by state
- action handlers respect lifecycle boundaries

### Service Integrity Tests
- no direct uncontrolled mutation path remains
- lifecycle service is the authoritative mutation path
- integration flows remain deterministic

## Non-Goals for This Document

This document does not define:
- retry orchestration policy
- worker claim semantics
- review item internal workflow states
- export artifact format
- audit event schema details

Those belong to separate architecture documents unless later linked explicitly.

## Summary

InvoMatch run lifecycle is defined by a strict, explicit, and terminal-aware state machine.

The authoritative lifecycle path is:

queued -> processing -> review_required -> completed

with controlled alternative terminal exits:

queued -> failed
queued -> cancelled
processing -> failed
processing -> cancelled
review_required -> failed
review_required -> cancelled

No state outside this model is valid, and no transition outside the allowed map is permitted.