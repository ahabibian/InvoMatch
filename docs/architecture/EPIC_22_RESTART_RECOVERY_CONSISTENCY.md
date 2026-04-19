# EPIC 22 â€” Restart Recovery Consistency & Persistence Integrity

## 1. Purpose

EPIC 22 hardens restart safety across runtime, persistence, review orchestration, export readiness, and product-facing projections.

The system already supports:

- ingestion â†’ run creation
- runtime execution
- review orchestration
- export readiness
- operational recovery controls
- operator-facing product surfaces

However, restart and re-entry behavior is still not fully hardened.

A process restart, crash, or recovery loop re-entry must never corrupt:

- run lifecycle state
- review state
- export readiness
- structured errors
- retry metadata
- operational ownership
- run view projection
- finalized business truth

This EPIC defines the restart model required to preserve system truth across restart and persistence boundaries.

---

## 2. Scope

This EPIC focuses on:

- restart consistency
- runtime re-entry
- stale lease reclaim
- retry-safe reacquisition
- persistence reload behavior
- review and export restart safety
- run view consistency after restart
- operational recovery interaction
- deterministic crash handling

This EPIC does not include:

- new product features
- matching changes
- UI redesign
- distributed workers
- multi-node coordination
- infrastructure scaling
- new product flows

---

## 3. Core Principle

A restarted system is only considered safe if persisted truth remains intact after restart.

Restart must never:

- silently reset run status
- silently reset retry counters
- silently remove structured errors
- silently regenerate review state
- silently regenerate export state
- silently overwrite finalized runs
- silently change run ownership
- silently lose operational metadata

All restart behavior must be deterministic, explicit, and persistence-backed.

---

## 4. Restart State Model

### queued

Restart behavior:

- queued runs remain queued
- no lifecycle timestamps are recalculated
- no retry counters are modified
- queued runs may be safely reacquired

### processing

Restart behavior:

- processing runs are not automatically considered healthy
- existing lease ownership must be evaluated
- stale ownership must be reclaimed through lease-expiry rules
- processing runs may resume only if the lease is valid
- processing runs may be re-entered only after stale ownership is cleared

### review_required

Restart behavior:

- review summary must survive restart exactly as persisted
- existing review items must not be regenerated
- resolved review items must remain resolved
- unresolved review items must remain unresolved
- restart must not reset review-required state back to processing

### completed

Restart behavior:

- completed runs are immutable
- completed runs cannot re-enter runtime execution
- completed runs cannot be retried
- completed runs retain export summary, artifacts, timestamps, and run view state

### failed

Restart behavior:

- failed runs remain failed unless recovery eligibility explicitly permits retry
- structured errors must survive restart
- retry counters must survive restart
- terminal failure metadata must survive restart

### cancelled

Restart behavior:

- cancelled runs are immutable
- cancelled runs cannot be reclaimed
- cancelled runs cannot be retried

### retry_pending

Restart behavior:

- retry eligibility survives restart
- retry counters survive restart
- recovery scheduling survives restart
- retry_pending runs may be reacquired only through recovery rules

### export_ready

Restart behavior:

- export readiness survives restart
- export summary survives restart
- export artifact references survive restart
- finalized export-ready state cannot be downgraded during restart

---

## 5. Persistence Integrity Rules

The following fields must survive restart without recalculation or silent reset:

- run status
- created_at
- updated_at
- started_at
- finished_at
- retry_count
- retry_budget_remaining
- recovery_attempts
- structured_errors
- review_summary
- export_summary
- export_artifacts
- review_case identifiers
- review item identifiers
- operational metadata
- lease ownership metadata
- last heartbeat timestamp
- terminal failure reason
- run view projection inputs

The following fields may be recalculated safely after restart:

- stale lease eligibility
- lease expiration status
- next recovery attempt timestamp
- operational reclaim eligibility

The following fields must never be regenerated after restart:

- review items already created
- resolved review decisions
- finalized export artifacts
- finalized export summary
- structured error history
- retry history
- run identifiers
- review identifiers
- artifact identifiers

---

## 6. Re-Entry Claim Model

Restart-safe run ownership requires deterministic claim semantics.

Rules:

1. Only one active owner may exist for a run at a time.
2. A run with an active valid lease cannot be reclaimed.
3. A run with an expired lease may be reclaimed.
4. Lease reclaim must be explicit and persistence-backed.
5. Restart must never create duplicate owners.
6. Re-entry must never reset retry metadata.
7. Re-entry must never re-run finalized actions.
8. Re-entry must never overwrite terminal state.
9. Re-entry must never create duplicate review items.
10. Re-entry must never create duplicate export artifacts.

---


## 6A. Canonical Restart Ownership Rules

The following ownership rules are normative:

- restart re-entry for a previously processing run is treated as a new persisted execution claim
- a successful recovery reclaim increments attempt_count
- claim ownership is always persistence-backed
- only one persisted active owner may exist at a time
- terminal runs must not be reclaimable
- review_required runs must not be reclaimed through runtime claim flow
- completed runs must not be reclaimed through runtime claim flow
- failed runs must only re-enter through explicit recovery eligibility rules, never through direct runtime reclaim
- restart must not create a synthetic owner for runs that are not actively reclaimed

This means recovery reclaim is not an in-memory continuation.
It is a persisted re-acquisition event.

## 6B. Canonical Truth Sources

The following truth-source rules are normative:

- run lifecycle truth is owned by the run store
- review item truth is owned by the review store
- export artifact truth is owned by the export artifact repository
- run view is a projection and must never invent state not supported by persisted sources

When persisted sources disagree, the system must prefer explicit persisted business truth over inferred readiness.

Run view must never:

- infer completed review when persisted open review items still exist
- infer exported state when no persisted ready artifact exists
- infer failed export unless persisted export evidence supports it
- infer review completion from run status alone

## 6C. Restart-Safe Projection Rules

After restart, run view must be rebuilt entirely from persisted state.

The projection layer must treat all in-memory assumptions as invalid after restart.

Required guarantees:

- review_summary must be computed only from persisted review data
- export_summary must be computed only from persisted artifact state and persisted readiness rules
- terminal run status must not be contradicted by projection
- review_required status must remain review_required until persisted review state allows completion
- completed status must not imply exported status
- exported status requires persisted ready artifact existence

## 6D. Crash Boundary Rules

The following crash boundaries must be treated as explicit integrity boundaries:

1. crash after review item generation but before run persistence
2. crash after review decision but before run persistence
3. crash after run completion but before export readiness visibility
4. crash after export generation started but before artifact persistence
5. crash after artifact persistence but before run view retrieval

For each boundary the persisted state is the only source of truth after restart.
No in-memory operation may be assumed committed.

## 6E. Required Implementation Hardening Targets

Implementation must explicitly harden the following:

- RuntimeRecoveryService must reject reclaim for non-processing persisted states
- recovery reclaim behavior must be validated against persisted lifecycle state
- run store reclaim semantics must remain consistent across InMemoryRunStore, JsonRunStore, and SqliteRunStore
- run view projection must not over-infer readiness from fallback logic
- orchestration persistence flows must preserve truth when interrupted between business transitions and persistence

## 6F. Required New Tests

At minimum, EPIC 22 must add targeted tests for:

- restart-safe reclaim rejection for review_required runs
- restart-safe reclaim rejection for completed runs
- restart-safe reclaim rejection for failed runs without explicit recovery eligibility
- persistence reload preserving claimed_by, lease_expires_at, attempt_count, error, and report
- run view consistency after persistence reload
- review summary consistency after persistence reload
- exported state consistency after persistence reload
- no duplicate review generation after interrupted orchestration
- no duplicate export visibility after interrupted export flow

## 7. Run View Restart Consistency Rules

Run view must always reflect persisted truth.

Restart must not create:

- stale review summaries
- stale export summaries
- contradictory product-facing status
- review-required runs with completed export summaries
- failed runs with active processing ownership
- completed runs with unresolved review summaries
- processing runs with finalized export state

Run view projection must derive from persisted state, not in-memory assumptions.

---

## 8. Review Restart Safety

Restart must preserve:

- review case existence
- review item existence
- review item status
- reviewer decisions
- review-required state
- review completion state
- review resolution metadata

Restart must not:

- duplicate review items
- reopen resolved review items
- lose review comments
- lose reviewer identity
- downgrade resolved state

---

## 9. Export Restart Safety

Restart must preserve:

- export readiness
- export summary
- export artifact metadata
- export artifact references
- export completion timestamps
- finalized export state

Restart must not:

- regenerate duplicate artifacts
- downgrade export-ready state
- remove export metadata
- invalidate finalized artifacts

---

## 10. Recovery Loop Interaction Rules

Restart behavior must respect EPIC 19 recovery controls.

Restart must not bypass:

- retry eligibility rules
- retry cutoff rules
- recovery scheduling rules
- stuck run detection rules
- terminal failure rules
- retry budget enforcement
- recovery attempt limits

Recovery loop re-entry must continue using persisted retry metadata.

---

## 11. Failure Scenario Matrix

### Crash During Processing

Expected result:

- run remains processing
- stale lease may later trigger reclaim
- no duplicate execution allowed

### Crash During Review Generation

Expected result:

- partially-created review state must be rejected or cleaned safely
- duplicate review items must not be created
- review generation must remain idempotent

### Crash After Review Resolution But Before Persistence

Expected result:

- persisted review state remains source of truth
- unresolved persisted review state must remain unresolved
- in-memory resolution must not be assumed completed

### Crash Before Export Readiness Persistence

Expected result:

- export readiness remains unchanged
- export-ready state only exists if persisted

### Crash During Retry Re-Entry

Expected result:

- retry counters remain accurate
- recovery ownership remains single-owner only
- retry budget cannot reset

---

## 12. Implementation Plan

1. Define restart lifecycle model
2. Define persistence integrity rules
3. Define stale lease reclaim model
4. Define restart-safe ownership model
5. Harden runtime re-entry behavior
6. Harden review generation idempotency
7. Harden export readiness persistence rules
8. Harden run view projection rules
9. Add restart-focused runtime tests
10. Add Scenario 6
11. Re-run required regression scenarios
12. Produce closure document

---

## 13. Test Strategy

Required test coverage should include:

- restart-safe lease reclaim
- stale ownership detection
- retry-safe reacquisition
- structured error persistence after restart
- review summary persistence after restart
- export summary persistence after restart
- run view consistency after restart
- prevention of duplicate review generation
- prevention of duplicate export generation
- restart-safe retry counters
- restart-safe recovery metadata
- restart-safe terminal failure behavior

Required regression scenarios:

- Scenario 1 â€” Happy Path Full Flow
- Scenario 2 â€” Review Resolution Flow
- Scenario 4 â€” Runtime Failure Terminalization
- Scenario 6 â€” Restart Recovery Consistency

---

## 14. Closure Criteria

EPIC 22 is complete only if:

- restart behavior is deterministic for all major lifecycle states
- re-entry cannot create duplicate processing
- retry metadata survives restart
- structured errors survive restart
- review state survives restart
- export readiness survives restart
- run view remains consistent after restart
- restart cannot corrupt finalized state
- Scenario 6 passes
- required regression scenarios pass
- no restart-induced lifecycle corruption remains