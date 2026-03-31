# ACTION EXECUTION ARCHITECTURE

## Purpose

This document defines the internal execution architecture for product-facing actions.

It introduces a controlled execution layer that connects API commands to:

- Workflow state transitions
- Side effect execution
- Audit logging

This layer sits behind the product contract boundary and must not leak internal models.

---

## Architectural Position

The action execution layer sits between:

API Routes (contract boundary)
and
Domain / Persistence / Workflow systems

---

## Execution Flow

Each action follows a strict execution pipeline:

1. Route receives request (contract-safe)
2. Route maps request → ActionCommand
3. ActionExecutionService receives command
4. Dispatcher selects handler
5. Handler validates eligibility
6. Handler performs state transition
7. Handler triggers side effects
8. Audit log is written
9. Result is returned and mapped to response

---

## Core Components

### ActionExecutionService

Responsibilities:

- Entry point for all actions
- Accepts ActionCommand
- Calls dispatcher
- Ensures execution lifecycle is consistent
- Aggregates results
- Ensures audit logging occurs

---

### Action Dispatcher

Maps:

action_type → handler

Must be deterministic and static.

No dynamic runtime resolution.

---

### Action Handlers

Handlers contain the actual execution logic.

Each handler must:

- Validate input
- Validate current state
- Enforce allowed transitions
- Perform mutation
- Produce side effects
- Return structured result

Handlers must NOT:

- Access API layer
- Return contract models directly
- Perform unrelated logic

---

## Execution Model

### Step 1 — Command Intake

ActionExecutionService receives:

ActionCommand

---

### Step 2 — Handler Resolution

Dispatcher resolves correct handler:

Example:

RESOLVE_REVIEW → ResolveReviewActionHandler  
EXPORT_RUN → ExportRunActionHandler  

---

### Step 3 — Validation

Handler validates:

- Target existence
- Current state
- Action eligibility

Invalid cases must fail explicitly.

---

### Step 4 — State Transition

Handler applies state change:

- Review state update
- Run state update (if required)

Transitions must be:

- Explicit
- Deterministic
- Enforced

---

### Step 5 — Side Effects

Handler executes side effects:

Examples:

- Export file generation
- Metadata update
- Logging

Side effects must be:

- Observable
- Recorded
- Deterministic

---

### Step 6 — Audit Logging

Audit record must include:

- action_type
- target_id
- actor
- before_state
- after_state
- side effects summary
- execution status

---

### Step 7 — Result Construction

Handler returns:

ActionExecutionResult

Service returns it to route.

Route maps to contract response.

---

## Idempotency Model

Actions must behave predictably under repeated execution.

### Resolve Review

- If already resolved with same decision → no-op
- If conflicting decision → controlled failure

### Export Run

- Same request → same artifact reference
- No duplicate uncontrolled artifacts

---

## Failure Model

### Validation Failure

- No mutation
- No side effects

### Execution Failure

- Partial execution must be visible
- Audit must still be recorded

No hidden rollback assumptions.

---

## Separation of Concerns

Layer responsibilities:

Route:
- Input/output mapping only

ActionExecutionService:
- Orchestration

Handler:
- Business execution

Store:
- Persistence only

Audit:
- Logging only

---

## Anti-Patterns (Forbidden)

- Direct state mutation inside routes
- Hidden side effects
- Mixing export logic with unrelated handlers
- Returning domain models to API
- Implicit transitions without validation

---

## Minimal Initial Implementation Strategy

Start with:

1. ResolveReviewActionHandler
2. ExportRunActionHandler
3. Basic ActionExecutionService
4. Deterministic audit logging

Do NOT:

- Add async execution
- Add background workers
- Add event buses

---

## Outcome

After implementation:

- All actions go through a unified execution layer
- State transitions are controlled and explicit
- Side effects are deterministic and testable
- Audit trail is complete and reliable

This architecture becomes the foundation for all future product actions.