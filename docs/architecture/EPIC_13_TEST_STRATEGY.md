# EPIC 13 — Test Strategy

Status: PROPOSED

Related Documents:
- EPIC_13_REVIEW_ORCHESTRATION.md
- RUN_FINALIZATION_POLICY.md
- REVIEW_ITEM_GENERATION_POLICY.md
- EPIC_13_IMPLEMENTATION_PLAN.md

---

## 1. Purpose

Define the complete validation strategy for EPIC 13.

This test strategy ensures that:

- review orchestration behaves deterministically
- run progression is correctly gated
- finalization is strictly enforced
- export readiness is never violated
- product contract remains consistent

This document defines what must be tested, not just how.

---

## 2. Test Layers

Testing must be structured across three layers:

1. Unit Tests
2. Service / Integration Tests
3. Contract / Read-Model Tests

All three layers are required for EPIC closure.

---

## 3. Unit Test Scope

### 3.1 Review Requirement Evaluation

Validate classification of reconciliation outcomes:

- finalizable outcome → no review required
- unmatched → review required
- ambiguous → review required
- low confidence → review required
- forced review rule → review required

Edge cases:
- borderline confidence
- conflicting rules
- missing fields

---

### 3.2 Review Case Generation

Validate:

- correct creation of review cases for blocking outcomes
- no case created for finalizable outcomes
- correct mapping of invoice scope to review case

Idempotency tests:

- repeated evaluation does not create duplicates
- same input produces same case identity

---

### 3.3 Run Finalization Evaluation

Validate:

- run is finalizable when zero blocking review cases exist
- run is NOT finalizable when at least one blocking case exists
- run remains blocked on deferred/reopened cases

---

## 4. Integration / Service Tests

### 4.1 Post-Matching Flow

Test full flow:

matching completed → orchestration → run state

Cases:

- no review needed → run becomes completed
- review required → run becomes review_required
- review cases created correctly

---

### 4.2 Review Resolution Flow

Test:

review_required → resolve cases → re-evaluate run

Cases:

- resolve one case → run stays in review_required
- resolve all cases → run becomes completed
- defer case → run stays blocked
- reopen case → run returns to blocked state

---

### 4.3 Idempotent Re-Orchestration

Test:

- running orchestration multiple times does not duplicate cases
- run state remains stable for same input

---

### 4.4 Export Readiness Flow

Test:

- completed run → export allowed
- review_required run → export blocked
- processing run → export blocked
- failed/cancelled → export blocked

---

## 5. Contract / Read Model Tests

Validate that product-facing API remains consistent:

### 5.1 Run Status

- status = review_required when active review exists
- status = completed only when fully resolved

### 5.2 Review Summary

- correct count of active review cases
- reflects blocking vs resolved state

### 5.3 Export Summary

- only available when run is completed
- not exposed prematurely

---

## 6. Edge Case Matrix

Must explicitly test:

- partial review resolution
- multiple invoice scopes with mixed states
- re-opening a previously resolved case
- conflicting user decisions
- repeated orchestration calls
- late-arriving review-required classification
- stale data vs re-evaluated data

---

## 7. Non-Negotiable Assertions

The following must NEVER pass incorrectly:

- run completes while review cases are still active
- export is allowed before completion
- duplicate review cases are created
- run state flips inconsistently across repeated evaluations
- product API exposes inconsistent state

---

## 8. End-to-End Flow Validation

Full scenario test:

1. create run
2. process matching
3. generate review cases
4. resolve cases step-by-step
5. verify run transitions
6. verify finalization
7. verify export readiness

This test must simulate real system usage.

---

## 9. Coverage Requirements

EPIC 13 is NOT complete unless:

- all evaluators are unit tested
- orchestration service is integration tested
- product contract behavior is validated
- edge cases are explicitly covered

---

## 10. Closure Criteria

EPIC 13 test coverage is complete only when:

- all blocking review scenarios are enforced by tests
- finalization cannot occur incorrectly
- export gating is validated
- orchestration is deterministic under repeated execution
- product-facing behavior matches internal orchestration state