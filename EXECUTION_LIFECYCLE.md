# EXECUTION_LIFECYCLE.md

## InvoMatch Execution Lifecycle Architecture

### Status
Draft v1.0 (Epic 1 baseline)

### Purpose

This document defines the execution lifecycle rules for reconciliation runs in InvoMatch.

Scope of this document:

- claiming model
- lease expiry
- retry semantics
- terminal enforcement

This document is intentionally limited to execution ownership and lifecycle correctness. It does not define matching logic, OCR behavior, or stage business rules.

---

## Current Run Model Baseline

The current `ReconciliationRun` model includes:

- `run_id`
- `status`
- `version`
- `created_at`
- `updated_at`
- `started_at`
- `finished_at`
- `claimed_by`
- `claimed_at`
- `lease_expires_at`
- `attempt_count`
- `invoice_csv_path`
- `payment_csv_path`
- `error_message`
- `report`

Current lifecycle statuses:

- `pending`
- `running`
- `completed`
- `failed`

Current terminal statuses:

- `completed`
- `failed`

This document treats the current schema as the implementation baseline, while defining stricter lifecycle rules for production-safe behavior.

---

## Lifecycle Principles

Execution lifecycle must guarantee:

- at most one valid executor per run
- deterministic recovery after worker crash
- bounded retry behavior
- immutable terminal states
- persistent lifecycle audit fields

Lifecycle correctness must not depend on in-memory process state.

All lifecycle decisions must be derived from persisted run state.

---

## Claiming Model

Workers do not "own" runs permanently.

Workers acquire a **time-bounded lease** for a run.

A worker may claim a run only if all of the following are true:

- run status is `pending` or `running`
- run is not terminal
- `lease_expires_at` is null, or earlier than current time

Successful claim must atomically update:

- `claimed_by`
- `claimed_at`
- `lease_expires_at`
- `updated_at`

A claim must fail if another worker already owns a still-valid lease.

This guarantees single active executor semantics at the persistence layer.

---

## Claim Eligibility Rules

A run is claimable under these conditions:

### Case 1 — Fresh pending run
- `status = pending`
- no active lease exists

### Case 2 — Recoverable running run
- `status = running`
- previous lease expired

This second case is required for crash recovery.

A worker must never claim:

- `completed` runs
- `failed` runs

---

## Lease Model

Lease is the execution ownership mechanism.

Recommended baseline values:

- lease duration: 30 seconds
- renewal interval: 10 seconds

The lease duration must tolerate temporary storage latency, process jitter, and short pauses without causing unnecessary ownership churn.

Lease ownership is represented by:

- `claimed_by`
- `claimed_at`
- `lease_expires_at`

The worker that owns the lease is the only valid executor of that run until the lease expires.

---

## Lease Renewal

While executing, a worker must periodically renew the lease before `lease_expires_at`.

Lease renewal must atomically update:

- `lease_expires_at`
- `updated_at`

Renewal must only succeed if:

- the run is still claimed by the same worker
- the run is not terminal

If renewal fails, the worker must assume lease ownership has been lost and must stop execution immediately.

A worker that loses lease ownership must not commit stage results afterward.

This is a strict correctness rule.

---

## Lease Expiry Recovery

If a worker crashes or stops renewing lease, the run becomes reclaimable after lease expiry.

Recovery rules:

- expired lease invalidates previous ownership
- another worker may claim the run
- resumed execution must use persisted run state only
- execution replay must be safe

This requires idempotent run processing behavior.

The system must prefer replay safety over optimistic in-memory continuation.

---

## Retry Semantics

Retry behavior is run-level in the current baseline model because the current schema includes `attempt_count` but does not yet include stage-level retry tracking.

`attempt_count` therefore represents:

- total execution attempts for the run

Retry is allowed only for retryable failures such as:

- transient storage failures
- temporary IO failures
- worker crash or process loss
- lease expiry during active execution

Retry is not allowed for:

- deterministic validation failures
- malformed input files
- non-retryable domain errors
- invariant violations that indicate logic or data corruption

---

## Retry Policy

Baseline retry policy:

- maximum attempts: 3
- backoff strategy: exponential
- attempt progression must be persisted

Example backoff:

- attempt 1 → immediate or short delay
- attempt 2 → delay
- attempt 3 → longer delay
- after max attempts → terminal failure

Each retry attempt must update:

- `attempt_count`
- `updated_at`
- optionally `error_message` with latest failure summary

If retry budget is exhausted, the run must transition to `failed`.

---

## Retry Boundary

In the current baseline, retry is defined at the run execution boundary.

This means the system may re-enter execution for the same run after crash or lease loss, but it must not assume partial in-memory progress survives.

The next executor must reconstruct all necessary state from persisted fields and durable artifacts only.

This is mandatory for future compatibility with multi-worker and Postgres-backed execution.

---

## Terminal Enforcement

Terminal states are immutable.

Current terminal states:

- `completed`
- `failed`

Terminal enforcement rules:

- terminal runs cannot be claimed
- terminal runs cannot renew lease
- terminal runs cannot increment retries
- terminal runs cannot transition back to non-terminal state

Store-level lifecycle logic must reject illegal writes against terminal runs.

No worker is allowed to continue execution after a run is terminal.

---

## Allowed Status Transitions

Current baseline transitions:

- `pending` → `running`
- `pending` → `failed`
- `running` → `completed`
- `running` → `failed`

The current model implementation also permits self-transitions:

- `pending` → `pending`
- `running` → `running`
- `completed` → `completed`
- `failed` → `failed`

These self-transitions should be treated as implementation-level persistence tolerance, not as meaningful business lifecycle progress.

They must not be used to bypass lifecycle rules.

---

## Failure Rules

A run must transition to `failed` when any of the following is true:

- retry budget is exhausted
- a non-retryable error occurs
- lifecycle invariants are violated
- execution cannot safely continue after repeated lease loss

`error_message` should contain the latest failure summary suitable for debugging and audit.

---

## Execution Invariants

The lifecycle engine must preserve the following invariants:

- at most one valid lease owner exists per run
- terminal runs are immutable
- retry count is monotonic
- lease renewal is ownership-bound
- execution after lease loss is invalid
- recovery must be based on persisted state only

Any implementation that violates these invariants is incorrect even if tests appear to pass.

---

## Known Gaps in Current Schema

The current baseline model is sufficient for initial lifecycle control, but it has explicit limitations:

- no `cancelled` status
- no `waiting_input` status
- no stage-level retry ledger
- no lease generation token / fencing token
- no explicit next retry timestamp
- no structured failure classification

These are intentional future extensions and are outside Epic 1 scope.

Epic 1 defines the minimum safe lifecycle contract around the current schema.

---

## Implementation Guidance

For the current SQLite-based baseline:

- claim must be atomic at the store layer
- lease expiry must be evaluated against persisted timestamps
- workers must not rely on in-memory ownership assumptions
- recovery logic must assume crash can happen at any point

Future Postgres migration must preserve the same lifecycle semantics.

---

## Non-Goals

This document does not define:

- reconciliation matching behavior
- report generation logic
- file ingestion parsing rules
- UI review workflow
- multi-stage business orchestration design

It only defines execution lifecycle control.

---

## Implementation Notes for Next PR

The next implementation PR for execution lifecycle should:

- enforce atomic claim behavior in the run store
- enforce lease renewal ownership checks
- reject lifecycle writes on terminal runs
- apply retry budget checks using `attempt_count`
- add test coverage for lease expiry reclaim and terminal immutability

---

## Epic Closure Condition

Epic 1 is considered functionally defined when this document is accepted as the lifecycle reference for:

- claim ownership behavior
- lease expiry behavior
- retry boundaries
- terminal state enforcement

Further work after this document belongs to implementation and storage hardening, not lifecycle definition itself.