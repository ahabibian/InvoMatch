# EPIC 7 — Action Execution Integration

## Status
IN PROGRESS

---

## Purpose

EPIC 7 introduces a controlled and deterministic execution layer for product-facing actions.

Up to EPIC 6, the system enforces a stable product contract at the API boundary. However, action execution remains shallow and partially implemented. This EPIC closes the gap between:

- Contract-safe API behavior
- Real internal workflow mutation and side-effect execution

The goal is to ensure that every action results in:

- Explicit state transition
- Deterministic side effects
- Auditable execution trace

This EPIC does NOT change the API contract. It deepens execution behind it.

---

## Scope

### In Scope

- Integration of action execution with review workflow state transitions
- Full implementation of `resolve_review` behavior
- Transformation of `export_run` into a real export workflow
- Introduction of Action Execution Service
- Deterministic audit logging for all actions
- Explicit side-effect modeling
- Route-to-workflow command mapping

### Out of Scope

- UI or frontend changes
- Matching logic or scoring improvements
- Async job systems or distributed execution
- Notification systems
- External storage infrastructure (S3, etc.)
- Multi-tenant policy redesign

---

## Architectural Principles

### 1. Contract Boundary Preservation
API routes must only interact with product contract models.
No internal domain or persistence models may leak across the boundary.

### 2. Centralized Action Execution
All actions must be executed through a single application service:

ActionExecutionService

Routes must not perform state mutations directly.

### 3. Explicit Workflow Mutation
Every action must define:

- Target entity
- Allowed transitions
- Resulting state change
- Side effects
- Audit record

No implicit mutation is allowed.

### 4. Deterministic Execution
Given the same input, execution must produce the same result.
No hidden randomness or implicit retries.

### 5. Explicit Side Effects
All side effects must be:

- Observable
- Recorded
- Testable

Examples:
- Export artifact creation
- Review resolution
- Audit event emission

### 6. Idempotency
Repeated execution of the same action must not produce inconsistent results.

---

## High-Level Architecture

API Route
→ Contract Validation
→ Command Mapping
→ ActionExecutionService
→ Action Handler
→ Workflow / State Transition
→ Side Effects
→ Audit Logging
→ Contract-safe Response

---

## Core Components

### 1. ActionExecutionService

Responsibilities:

- Receive ActionCommand
- Validate execution eligibility
- Dispatch to appropriate handler
- Coordinate state mutation
- Collect side effects
- Record audit events
- Return structured execution result

---

### 2. Action Dispatcher

Maps:

action_type → handler

Ensures decoupling between API and execution logic.

---

### 3. Action Handlers

Each action has a dedicated handler.

#### Required handlers:

- ResolveReviewActionHandler
- ExportRunActionHandler

Handlers must:

- Validate input and eligibility
- Enforce state transition rules
- Apply mutation
- Produce side effects
- Emit audit data

---

### 4. ActionCommand (Internal)

Fields:

- action_type
- target_type
- target_id
- actor_id
- correlation_id
- payload
- requested_at

---

### 5. ActionExecutionResult

Fields:

- action_type
- target_type
- target_id
- status
- state_changes[]
- side_effects[]
- audit_event_ids[]
- response_payload

---

### 6. Audit Logging

Each action must generate an audit record with:

- action_type
- target_id
- actor
- before_state
- after_state
- side_effect_summary
- execution_status
- timestamp

---

## Workflow Integration

### Review Resolution

`resolve_review` must:

- Validate review exists and is pending
- Validate decision
- Apply resolution
- Update review state
- Update related run state if required
- Emit audit event

Allowed transitions:

PENDING → RESOLVED

Repeated execution must be handled deterministically.

---

### Export Workflow

`export_run` must become a real workflow.

Minimum requirements:

- Validate run eligibility
- Generate actual artifact (JSON minimum)
- Persist export reference
- Emit audit event

Suggested export states:

REQUESTED → COMPLETED
REQUESTED → FAILED

Export should be treated as a side workflow, not a destructive mutation of run lifecycle.

---

## Route to Workflow Mapping

Each route must map explicitly to a command.

Example:

POST /reviews/{id}/resolve
→ ResolveReviewActionCommand
→ ActionExecutionService

POST /runs/{id}/export
→ ExportRunActionCommand
→ ActionExecutionService

Routes must remain thin.

---

## File Plan

### Architecture Docs

- docs/architecture/EPIC_7_ACTION_EXECUTION_INTEGRATION.md
- docs/architecture/ACTION_EXECUTION_ARCHITECTURE.md
- docs/architecture/EXPORT_WORKFLOW.md
- docs/architecture/STATE_TRANSITION_INTEGRATION.md
- docs/architecture/ROUTE_WORKFLOW_MAPPING.md
- docs/architecture/ACTION_EXECUTION_TEST_STRATEGY.md

### Code Structure

src/invomatch/services/actions/
- execution_service.py
- dispatcher.py
- result.py
- handlers/
  - resolve_review.py
  - export_run.py

src/invomatch/services/audit/
- audit_log.py

src/invomatch/services/export/
- export_workflow.py
- export_writer.py

---

## Execution Plan

### Phase 1 — Architecture
- Define execution architecture
- Define transition rules

### Phase 2 — Core Engine
- Implement ActionExecutionService
- Implement dispatcher

### Phase 3 — Review Integration
- Implement resolve_review handler
- Enforce transitions

### Phase 4 — Export Integration
- Implement export workflow
- Generate real artifacts

### Phase 5 — Route Integration
- Connect routes to execution service

### Phase 6 — Testing
- Validate side effects
- Validate idempotency
- Validate transitions

---

## Test Strategy

Must include:

- Action execution integration tests
- State transition validation tests
- Side-effect verification tests
- Audit log tests
- Idempotency tests
- Forbidden transition tests

---

## Risks

- Mixing route logic with execution logic
- Hidden side effects
- Weak export implementation
- Missing audit trail
- Undefined idempotency behavior

---

## Definition of Done

EPIC 7 is complete when:

- resolve_review performs real state mutation
- export_run produces real artifacts
- all actions generate audit records
- side effects are deterministic and testable
- API contract remains unchanged
- invalid transitions are rejected
- repeated actions behave predictably

---

## Outcome

After EPIC 7:

- Actions are no longer placeholders
- Workflow mutation is controlled and explicit
- Side effects are observable and auditable
- System moves from contract enforcement to real execution layer

This EPIC establishes the foundation for reliable, scalable action orchestration.