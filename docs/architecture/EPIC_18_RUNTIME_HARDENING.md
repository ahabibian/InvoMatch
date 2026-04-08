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

Each runtime failure must map to a canonical structured failure record.

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
Product/API surfaces may expose a bounded subset only.

---

## 6. Retry Policy

Retry is policy-driven only.

No implicit retry is allowed inside handlers, orchestration branches, or product mapping code.

Initial runtime retry policy rules:

- terminal failure -> no retry
- non-retryable failure -> terminalize
- retryable failure before retry limit -> retry allowed
- retryable failure at retry limit -> terminalize as retry exhausted

Initial default retry limit: `3`

---

## 7. Re-entry Policy

Re-entry is allowed only when all are true:

- run status is `processing`
- the prior lease is no longer valid
- the last failure is retryable
- the last failure is not terminal
- the last failure is not a persistence, orchestration, or unexpected internal integrity failure

The runtime must remain strict, not optimistic.

---

## 8. Expected Next Implementation Stages

Planned follow-up implementation stages:

1. Runtime executor integration
2. terminal failure persistence rules
3. stuck-run resolver
4. lease ownership hardening
5. product-facing failed state consistency
6. degraded dependency handling tests

---

## 9. Test Strategy

Initial test coverage must validate:

- failure normalization
- retry decisioning
- retry exhaustion behavior
- re-entry legality rules
- product-safe failure structure

Later phases must add:

- executor integration tests
- stuck-run recovery tests
- lease handoff tests
- failed run contract tests
- degraded dependency tests

---

## 10. Closure Criteria

EPIC 18 is complete only if:

- runtime failure categories are explicit
- retry behavior is deterministic and test-covered
- stuck runs can be handled safely
- lease ownership integrity is enforced
- terminal failure behavior is consistent
- product-facing runtime failure truth is structured and bounded
- degraded dependency scenarios fail predictably
- no hidden lifecycle corruption remains under tested runtime failure conditions
---

## 11. Stuck Run Detection Baseline

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

## 12. Recovery Scan Baseline

The runtime recovery baseline must support deterministic scanning of persisted `processing` runs.

For each processing run:

- if it is not stuck -> leave unchanged
- if it is stuck and policy allows re-entry -> surface as a re-entry candidate
- if it is stuck and policy denies re-entry -> terminalize to `failed`

At this stage, the recovery layer does not execute re-entry automatically.
It only classifies and safely terminalizes unrecoverable stuck runs.