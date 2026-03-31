# ROUTE WORKFLOW MAPPING

## Purpose

This document defines the mapping between product-facing API routes and internal workflow execution.

Its goal is to make route behavior explicit and prevent business logic from leaking into the API layer.

Each mapped route must clearly specify:

- contract request model
- internal command
- execution service entry point
- action handler
- workflow/state mutation
- side effects
- contract-safe response shape

---

## Architectural Rule

Routes must remain thin.

Routes are responsible only for:

- receiving contract-safe request data
- validating contract-level input
- mapping request to internal command
- invoking ActionExecutionService
- mapping execution result back to contract-safe response

Routes must NOT:

- mutate workflow state directly
- construct domain side effects directly
- embed transition logic
- return internal models

---

## Mapping Model

Each product-facing action route follows this structure:

Route
→ Contract Request
→ Internal Command
→ ActionExecutionService.execute(...)
→ Action Handler
→ Workflow Mutation / Side Effects
→ ActionExecutionResult
→ Contract Response

---

## Route Mapping: Resolve Review

### Route

POST /reviews/{review_id}/resolve

### Contract Request

Expected request contains resolution intent such as:

- decision
- actor metadata if applicable
- optional reason or notes if supported by contract

### Internal Command

ResolveReviewActionCommand

Suggested internal fields:

- action_type = RESOLVE_REVIEW
- target_type = REVIEW
- target_id = review_id
- actor_id
- correlation_id
- payload.decision
- payload.reason
- requested_at

### Execution Entry Point

ActionExecutionService.execute(command)

### Handler

ResolveReviewActionHandler

### Workflow Mutation

Primary mutation:

- review: PENDING → RESOLVED

Possible related mutation:

- run: AWAITING_REVIEW → next allowed state

### Side Effects

- audit event creation
- resolution metadata persistence
- possible run progression

### Response Mapping

Route must map ActionExecutionResult into contract-safe response.

Response should expose:

- action accepted/result status
- review resolution outcome
- related references if needed

Response must NOT expose:

- internal handler class
- store object structure
- internal domain entities directly

---

## Route Mapping: Export Run

### Route

POST /runs/{run_id}/export

### Contract Request

Expected request contains export intent such as:

- export format
- optional export options if contract supports them

### Internal Command

ExportRunActionCommand

Suggested internal fields:

- action_type = EXPORT_RUN
- target_type = RUN
- target_id = run_id
- actor_id
- correlation_id
- payload.format
- payload.options
- requested_at

### Execution Entry Point

ActionExecutionService.execute(command)

### Handler

ExportRunActionHandler

### Workflow Mutation

Primary workflow impact:

- no required mutation of main run lifecycle by default

Side workflow:

- export: REQUESTED → COMPLETED
or
- export: REQUESTED → FAILED

### Side Effects

- export artifact generation
- artifact reference persistence
- audit event creation

### Response Mapping

Route must map ActionExecutionResult into contract-safe response.

Response should expose:

- export status
- export reference or artifact URI if allowed by contract
- export format
- completion/failure outcome

Response must NOT expose:

- file writer internals
- persistence internals
- internal workflow models

---

## Command Construction Rules

Routes must build internal commands deterministically.

### Required command qualities

- stable action_type
- stable target_type
- explicit target_id
- explicit payload
- explicit actor identity where available
- correlation_id for audit traceability

### Forbidden command construction patterns

- partial payload guessing inside handler
- hidden defaults that change execution semantics
- route-specific ad hoc command shapes

---

## Response Mapping Rules

Execution results must be translated back into contract-safe responses.

### Route response mapper responsibilities

- convert internal execution status to contract status
- expose stable product-facing fields only
- hide internal workflow details
- preserve backward compatibility with EPIC 6 boundary

### Forbidden response behavior

- leaking store state
- leaking raw domain model objects
- leaking handler-specific internal fields
- changing existing response contract shape without explicit contract revision

---

## Error Mapping Rules

Routes must map internal failures into stable product-facing API errors.

### Validation failures

Examples:

- invalid decision
- ineligible export state
- missing target entity

These must produce stable API error responses.

### Conflict failures

Examples:

- resolving already-resolved review with different decision
- duplicate export request with incompatible semantics

These must produce controlled conflict responses.

### Internal execution failures

Examples:

- side-effect generation failure
- persistence failure during action handling

These must not leak stack-sensitive internal structures through the API.

---

## Route Ownership Boundaries

### Routes own

- HTTP concerns
- contract validation
- command construction
- response mapping

### ActionExecutionService owns

- orchestration
- dispatch
- execution lifecycle consistency

### Handlers own

- business execution logic
- transition enforcement
- side-effect production

### Stores own

- persistence mechanics only

---

## Deterministic Mapping Requirement

The same route request with the same current system state must produce the same command and the same mapped result.

This prevents route-layer ambiguity and keeps execution reproducible.

---

## Initial Route Coverage for EPIC 7

This EPIC requires explicit workflow mapping for at least:

- POST /reviews/{review_id}/resolve
- POST /runs/{run_id}/export

Additional action routes may adopt the same pattern later, but these two define the minimum product-grade action mapping for EPIC 7.

---

## Risks Prevented by This Document

This mapping prevents:

- route-layer business logic drift
- handler ambiguity
- contract leakage
- inconsistent response construction
- state mutation from API layer
- unstable action execution behavior

---

## Outcome

After this mapping is applied:

- routes stay thin
- execution logic stays centralized
- handlers remain responsible for workflow mutation
- contract boundary remains stable
- action behavior becomes explicit from route to side effect