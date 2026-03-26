# RUN_STORE_CONTRACT_PHASES.md

## Status
Proposed

## Purpose

Define the phased delivery model for the Run Store contract introduced in EPIC 2.

The contract written in `RUN_STORE_CONTRACT.md` is the long-term target.
However, the current domain model and SQLite implementation do not yet support all contract semantics.

This document separates:

- what must conform now
- what is intentionally deferred
- what requires domain evolution before backend conformance is possible

The goal is to avoid pretending the current backend supports semantics that do not yet exist.

---

## 1. Problem Statement

The current implementation in `src/invomatch/services/sqlite_run_store.py` is based on:

- `ReconciliationRun`
- optimistic versioned updates
- explicit `claim_run(...)`
- explicit `heartbeat_run(...)`
- status set limited to:
  - `pending`
  - `running`
  - `completed`
  - `failed`

The long-term contract in `RUN_STORE_CONTRACT.md` includes semantics beyond the current domain model, such as:

- `awaiting_review`
- `cancelled`
- `claim_next_eligible_run(...)`
- `release_claim(...)`
- durable retry visibility methods
- backend-neutral lifecycle operations

This means the long-term contract must be phased.

---

## 2. Phase Model

The Run Store contract is split into two phases:

- **Phase A — Core Contract**
- **Phase B — Expanded Contract**

### Rule

Phase A must be satisfied by the current SQLite implementation or by a thin conformance layer around it.

Phase B remains the target contract, but is not required for EPIC 2 closure unless explicitly implemented.

---

## 3. Phase A — Core Contract

Phase A is the minimal enforceable behavioral contract for the current repository state.

### 3.1 Supported Lifecycle States

Phase A is limited to:

- `pending`
- `running`
- `completed`
- `failed`

### 3.2 Supported Operations

Phase A includes:

- create run
- get run by id
- list runs deterministically
- duplicate create rejection
- claim a known run by id
- heartbeat lease for current owner
- optimistic version safety
- mark completed through current update flow
- mark failed through current update flow
- missing run returns none or explicit not found behavior, depending on operation

### 3.3 Supported Guarantees

Phase A guarantees:

- durable creation
- durable get
- deterministic list ordering
- no silent duplicate create
- claim conflicts are visible
- heartbeat ownership conflicts are visible
- terminal states remain terminal within the current state model
- persistence behavior is testable against SQLite

### 3.4 Phase A Non-Goals

Phase A does not require:

- queue-level claim-next semantics
- awaiting review semantics
- cancelled semantics
- explicit release semantics
- retry policy API
- backend-neutral payload inputs
- fully relocated implementation under `persistence/sqlite/`

---

## 4. Phase B — Expanded Contract

Phase B is the long-term target defined by `RUN_STORE_CONTRACT.md`.

### 4.1 Intended Additions

Phase B includes:

- `awaiting_review`
- `cancelled`
- `claim_next_eligible_run(...)`
- `renew_claim(...)` in final contract form
- `release_claim(...)`
- `increment_retry(...)`
- `is_retry_allowed(...)`
- backend-neutral lifecycle API
- storage-first queue semantics
- contract-first backend parity with PostgreSQL

### 4.2 Preconditions for Phase B

Phase B should not be enforced until the following are addressed:

- domain model expansion
- lifecycle state model expansion
- persistence API expansion
- migration path for current service-layer callers
- explicit decision on adapter vs full backend refactor

---

## 5. Why This Split Is Necessary

Without phasing, one of two bad outcomes happens:

1. the contract gets weakened to match the current implementation too early
2. the tests become unrealistic and fail for reasons that do not reflect meaningful conformance work

Phasing avoids both mistakes.

It allows the project to:

- keep a strong long-term contract
- keep current implementation reality visible
- write meaningful tests now
- defer incompatible semantics honestly

---

## 6. Test Strategy by Phase

### Phase A Tests

Phase A tests should validate only behavior that the current implementation can reasonably support.

Examples:

- create then get
- duplicate create rejection
- deterministic list ordering
- get missing run
- claim known run by id
- reject claim conflicts
- heartbeat only by owner
- complete through current update flow
- fail through current update flow

### Phase B Tests

Phase B tests should remain separate until implementation support exists.

Examples:

- claim next eligible run
- release claim
- awaiting review transition
- retry visibility APIs
- queue-driven reclaim semantics
- backend-neutral contract input semantics

---

## 7. Architectural Decision

Decision:

- `RUN_STORE_CONTRACT.md` remains the long-term target
- EPIC 2 enforcement work is split into Phase A and Phase B
- SQLite conformance for EPIC 2 focuses on Phase A
- Phase B remains explicit, visible, and deferred rather than silently dropped

---

## 8. Exit Criteria for Phase A

Phase A is complete when:

- a core contract test suite exists
- SQLite can be bound to that suite meaningfully
- core behavior passes or produces intentional, tracked failures
- deterministic list behavior is verified
- claim and heartbeat semantics are verified in current-store terms
- terminal update behavior is verified in current-store terms

---

## 9. Exit Criteria for Phase B Readiness

Phase B becomes actionable when:

- domain state model is expanded
- lifecycle contract is accepted by callers
- backend adapter or refactor strategy is approved
- SQLite and PostgreSQL parity work is ready to begin

---

## 10. Summary

The Run Store contract is not being weakened.
It is being phased.

Phase A defines the enforceable core contract for the current repository state.

Phase B defines the expanded backend-independent persistence target.

This split allows EPIC 2 to produce honest, testable progress without forcing a reckless refactor.