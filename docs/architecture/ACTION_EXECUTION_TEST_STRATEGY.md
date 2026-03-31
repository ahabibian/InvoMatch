# ACTION EXECUTION TEST STRATEGY

## Purpose

This document defines how action execution must be tested to ensure:

- deterministic behavior
- correct state transitions
- explicit side effects
- reliable audit logging

This strategy ensures that actions are not only implemented, but provably correct.

---

## Testing Principles

### 1. Deterministic Testing

The same input and state must produce the same output.

No test should rely on randomness or implicit timing behavior.

---

### 2. Side Effect Validation

Tests must verify real side effects:

- state changes
- artifact creation
- audit logs

Status codes alone are not sufficient.

---

### 3. Isolation of Concerns

Tests must be structured across layers:

- route layer
- execution service
- handler logic

---

### 4. Explicit Failure Testing

All failure paths must be tested explicitly.

---

## Test Categories

### 1. Resolve Review Tests

Must verify:

- PENDING → RESOLVED transition
- decision is stored correctly
- audit record is created
- related run state is updated if required

---

### 2. Resolve Review Idempotency

Test cases:

- same decision repeated → no-op
- different decision → conflict

Must verify:

- no duplicate side effects
- no unintended state mutation

---

### 3. Export Run Tests

Must verify:

- eligible run produces real artifact
- artifact file exists
- artifact path is deterministic
- export metadata is recorded
- audit record is created

---

### 4. Export Idempotency

Test cases:

- repeated export request returns same artifact reference
- no duplicate uncontrolled files created

---

### 5. Forbidden Transition Tests

Must verify:

- resolving already resolved review fails correctly
- exporting ineligible run fails
- invalid inputs do not mutate state

---

### 6. Audit Tests

Must verify:

- audit record is created for each action
- audit contains required fields:
  - action_type
  - target_id
  - before_state
  - after_state
  - status

---

### 7. Route Integration Tests

Must verify:

- route maps request correctly to command
- response is contract-safe
- no internal model leakage

---

## Test Structure

Recommended structure:

tests/
  test_actions/
    test_resolve_review.py
    test_export_run.py
    test_idempotency.py
    test_transitions.py
    test_audit.py

---

## Assertions Required

Each test must assert:

- state before action
- state after action
- side effects
- audit entries

---

## Failure Handling Tests

Must include:

- invalid review id
- invalid run id
- invalid decision
- unsupported export format

---

## Anti-Patterns (Forbidden)

- testing only HTTP status codes
- skipping side effect verification
- relying on logs instead of assertions
- mixing multiple behaviors in one test
- non-deterministic tests

---

## Outcome

After applying this strategy:

- action execution is fully testable
- side effects are verifiable
- audit behavior is guaranteed
- system behavior becomes predictable and stable

This ensures EPIC 7 is production-grade, not prototype-level.