# EPIC 18 - Operational Reliability / Runtime Hardening

## 1. Objective

EPIC 18 hardens InvoMatch as a deterministic, failure-aware runtime environment.

The goal is to ensure the system behaves predictably under failure, retry, re-entry, lease expiry, partial degradation, and recovery scenarios.

This EPIC does not add new product flows.
It hardens runtime trustworthiness.

---

## 2. Scope

This EPIC includes:

- runtime failure taxonomy
- retry and re-entry policy
- stuck-run handling rules
- lease / concurrency integrity
- terminal failure semantics
- structured runtime error behavior
- degraded-mode safety rules
- runtime hardening implementation and tests

This EPIC excludes:

- UI changes
- new ingestion features
- new external integrations
- observability dashboards
- performance optimization
- new matching intelligence

---

## 3. Design Principles

- Determinism over convenience
- No hidden retry behavior
- No false success after failed persistence
- No silent lifecycle drift
- Terminal failure must be explicit
- Runtime truth must be product-safe and auditable

---

## 4. Canonical Runtime Failure Categories

The runtime layer uses the following canonical failure categories:

- `execution_failure`
- `orchestration_failure`
- `dependency_failure`
- `persistence_failure`
- `retry_exhausted`
- `unexpected_internal_error`

Each runtime failure maps to a canonical structured failure record.

---

## 5. Runtime Failure Record

Canonical runtime failure shape:

- `category`
- `code`
- `message`
- `is_retryable`
- `is_terminal`
- `operation_name` (optional)
- `dependency_name` (optional)

This structure is internal runtime truth.
Product/API surfaces expose a bounded subset only.

---

## 6. Retry Policy

Retry is policy-driven only.

No implicit retry is allowed inside handlers, orchestration branches, or product mapping code.

Implemented runtime retry policy rules:

- terminal failure -> no retry
- non-retryable failure -> terminalize
- retryable failure before retry limit -> retry allowed
- retryable failure at retry limit -> terminalize as retry exhausted

Implemented default retry limit: `3`

---

## 7. Re-entry Policy

Re-entry is allowed only when all are true:

- run status is `processing`
- the prior lease is no longer valid
- the last failure is retryable
- the last failure is not terminal
- the last failure is not a persistence, orchestration, or unexpected internal integrity failure

The runtime remains strict, not optimistic.

---

## 8. Implemented Runtime Hardening Scope

The following runtime hardening scope is now implemented:

1. canonical runtime failure model
2. deterministic retry / terminalization executor
3. runtime executor integration into reconciliation execution
4. terminal failure persistence on failed runs
5. structured run error model at domain/service level
6. stuck-run assessment baseline
7. recovery scan baseline for stuck processing runs
8. lease-safe re-entry claim handoff
9. structured failure propagation into run view
10. degraded read projection hardening for run view dependencies

---

## 9. Stuck Run Detection Baseline

A processing run is considered operationally stuck when one of the following is true:

- it remains in `processing` without a valid owner
- its lease has expired and no safe re-entry path exists
- its lease has expired and runtime failure context is missing
- its lease has expired and re-entry is explicitly denied by runtime policy

Baseline recovery decisions are restricted to:

- `none`
- `reenter`
- `fail`

No ambiguous recovery state is allowed.

---

## 10. Recovery Scan Baseline

The runtime recovery baseline supports deterministic scanning of persisted `processing` runs.

For each processing run:

- if it is not stuck -> leave unchanged
- if it is stuck and policy allows re-entry -> surface as a re-entry candidate
- if it is stuck and policy denies re-entry -> terminalize to `failed`

At this stage, the recovery layer does not execute re-entry automatically.
It classifies and safely terminalizes unrecoverable stuck runs.

---

## 11. Recovery Handoff Baseline

A run classified as a re-entry candidate may be claimed by a new worker only if:

- it is still in `processing`
- its existing lease is expired
- runtime policy explicitly allows re-entry
- ownership is reacquired through the canonical lease claim path

At this stage, handoff only reacquires ownership.
It does not automatically resume execution.

---

## 12. Structured Terminal Failure Semantics

Terminal runtime failures now persist as explicit failed run state.

Implemented behavior:

- failed runs transition through canonical lifecycle rules only
- terminal failure is persisted at the run level
- structured error state is stored as `RunError`
- legacy `error_message` is still preserved for bounded backward compatibility
- failed runs do not falsely appear completed after terminal runtime failure

---

## 13. Product-safe Failure Surface

Runtime failure truth is now propagated into the run view contract through a bounded structured error shape.

Implemented product-safe run view error fields:

- `code`
- `message`
- `retryable`
- `terminal`

Fallback rule:

- if structured run error is absent but legacy `error_message` exists, run view exposes a bounded fallback error with code `runtime_error`

No internal runtime-only fields are exposed.

---

## 14. Degraded Read Projection Rules

Run view degradation now follows bounded safety rules:

- artifact query failure -> artifacts degrade to empty list
- review store interface gaps -> review summary degrades to `not_started`
- review store runtime exceptions -> review summary degrades to `not_started`
- export readiness evaluator failure -> export readiness degrades to `False`
- failed run structured error remains visible even under read dependency degradation

The projection must fail safe and must not fabricate successful downstream state.

---

## 15. Test Strategy

Implemented coverage validates:

- failure normalization
- retry decisioning
- retry exhaustion behavior
- re-entry legality rules
- runtime executor terminalization
- stuck-run assessment
- recovery scan behavior
- recovery re-entry claim handoff
- structured terminal run error persistence
- run view structured failure propagation
- degraded dependency handling in run view

---

## 16. Explicit Deferrals

The following items are intentionally deferred beyond EPIC 18:

- automatic execution resume after recovery claim
- background recovery worker loop
- full persistence-backed runtime failure history / audit stream
- broader structured error rollout across every API surface outside the run view path
- infrastructure / observability rollout

These are not required for EPIC 18 closure.

---

## 17. Closure Criteria

EPIC 18 is complete only if:

- runtime failure categories are explicit
- retry behavior is deterministic and test-covered
- stuck runs can be handled safely
- lease ownership integrity is enforced
- terminal failure behavior is consistent
- product-facing runtime failure truth is structured and bounded
- degraded dependency scenarios fail predictably
- no hidden lifecycle corruption remains under tested runtime failure conditions