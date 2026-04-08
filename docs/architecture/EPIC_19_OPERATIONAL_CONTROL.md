# EPIC 19 - Operational Control, Recovery Loop and Runtime Observability

## 1. Purpose

EPIC 19 introduces an operational control layer above the deterministic runtime engine established in EPIC 18.

The system is now reliable under failure conditions, but it is not yet operationally autonomous or observable. A production-grade system must not only fail predictably, but must also detect, evaluate, recover, and expose runtime conditions without relying on manual intervention for standard cases.

This EPIC adds the control and visibility primitives required to make the runtime behave as a controlled, observable, semi-autonomous system.

After this EPIC, the system must be able to:

- detect failed and stuck runs automatically
- evaluate recovery eligibility deterministically
- trigger bounded retry or controlled re-entry through explicit policy
- expose operational metadata separately from business lifecycle state
- record all operational decisions as structured audit data
- provide minimal but queryable observability signals

---

## 2. Scope

This EPIC includes:

- recovery loop design and implementation
- stuck run detection rules
- scheduler or trigger-based operational scanning
- retry orchestration as an active control layer
- operational state model
- structured operational audit events
- minimal observability primitives
- policy and safety enforcement for self-healing behavior

This EPIC does not include:

- UI dashboards
- external monitoring platforms
- infrastructure-heavy observability stacks
- scaling or distributed orchestration concerns
- new product features
- AI, OCR, matching, or review intelligence improvements

This EPIC is about operational control and visibility, not feature expansion.

---

## 3. Architectural Position

EPIC 18 established deterministic execution, failure modeling, retry policy rules, and failure propagation consistency.

EPIC 19 must preserve those guarantees and build on top of them.

Operational control must be introduced as a separate layer above runtime execution. The runtime remains responsible for deterministic execution and lifecycle transitions. Operational control becomes responsible for recovery evaluation, retry orchestration, and observability.

The architecture must clearly separate the following responsibilities:

### Runtime Layer

Responsible for:

- run execution
- lifecycle transitions
- failure persistence
- deterministic retry policy enforcement primitives
- failure propagation into read surfaces

The runtime layer must not autonomously decide recovery actions.

### Operational Control Layer

Responsible for:

- inspecting runtime conditions
- evaluating recovery eligibility
- deciding retry, re-entry, skip, or terminal confirmation
- recording operational decisions
- coordinating bounded recovery actions

### Scheduler or Trigger Layer

Responsible for:

- periodically invoking operational scan services
- initiating candidate discovery for failed or stuck runs

The scheduler must not embed business or recovery logic.

### Observability and Audit Layer

Responsible for:

- recording structured operational events
- tracking counters and classifications
- exposing operational state and operational history

This layer must not perform hidden runtime mutation.

---

## 4. Core Principle

Business lifecycle state and operational condition are distinct concepts.

A run may be in a business state such as:

- processing
- review_required
- completed
- failed
- cancelled

At the same time, it may also have an operational condition such as:

- healthy
- retry_pending
- retry_in_progress
- stuck_detected
- recovery_skipped
- terminal_confirmed
- recovery_exhausted

Operational state must never replace or corrupt lifecycle truth.

The lifecycle state machine remains authoritative for product flow.
Operational state is an additional control and visibility layer.

---

## 5. Objective

The objective of EPIC 19 is to introduce a production-safe operational control plane that enables:

- automated recovery of failed or stuck runs
- deterministic and bounded retry orchestration
- safe recovery re-entry where explicitly allowed
- structured operational decision auditability
- queryable runtime observability primitives
- policy-driven self-healing without hidden mutation

The result should be a system that not only survives failure, but actively and safely recovers from recoverable operational conditions.

---

## 6. Recovery Loop

### 6.1 Definition

The recovery loop is a deterministic, policy-driven operational control process that:

- scans candidate runs
- identifies failed or stuck operational conditions
- evaluates whether recovery is allowed
- triggers retry or controlled re-entry where permitted
- records the outcome of each evaluation and action
- remains safe under repeated execution

The recovery loop must be idempotent, explicit, and testable.

### 6.2 Inputs

The recovery loop evaluates each candidate using:

- business lifecycle state
- runtime failure metadata
- retry policy state and retry count
- lease status or ownership health
- prior recovery attempts
- terminal markers
- operational policy configuration

### 6.3 Outputs

The recovery loop must produce explicit, typed outcomes such as:

- retry_triggered
- reentry_triggered
- recovery_skipped
- terminal_confirmed
- candidate_rejected
- already_recovered_noop

These outcomes must not exist only as logs. They must be represented as structured operational facts.

### 6.4 Hard Requirements

The recovery loop must be:

- idempotent
- deterministic
- bounded
- policy-driven
- safe under repeated scans
- safe under mixed healthy and unhealthy populations
- revalidation-aware before mutating state

A repeated scan must not re-trigger the same recovery action for the same incident.

---

## 7. Recovery Eligibility Policy

A run is eligible for recovery only when all required conditions hold.

At minimum, recovery eligibility must require:

- the run is not already in a completed or cancelled terminal business state
- the failure class or stuck condition is recoverable by policy
- retry budget has not been exhausted
- no active recovery operation is already in progress
- no valid current lease or active claim blocks recovery
- the run has not already been recovered for the same incident
- recovery action would not violate lifecycle invariants

Recovery must be rejected when any of the following is true:

- retry budget is exhausted
- failure class is non-recoverable
- terminal failure is already confirmed
- the run is manually cancelled
- the candidate state changed between scan-time and act-time
- recovery would bypass product flow rules
- recovery would re-open a completed terminal outcome

Eligibility must be revalidated before any recovery mutation is applied.

---

## 8. Stuck Run Detection

A run must not be called "stuck" informally. Stuck detection must be policy-defined.

A run may be classified as stuck when all relevant conditions hold, such as:

- business state is processing
- lease or ownership window has expired
- expected progress or heartbeat has not advanced within allowed threshold
- no healthy active execution claim exists
- the same incident has not already been processed by the recovery loop

Stuck detection is not itself recovery.

The system must maintain a clear boundary between:

1. detection
2. eligibility evaluation
3. recovery execution

This separation is required for correctness, auditability, and debugging clarity.

---

## 9. Scheduler and Trigger Mechanism

This EPIC introduces a lightweight scheduler or trigger mechanism for operational scan execution.

Its responsibilities are limited to:

- invoking operational scans on a defined cadence
- passing configuration thresholds or scan limits
- collecting structured scan summaries

It must not:

- embed recovery rules
- mutate runtime state directly
- bypass recovery orchestration services
- become a second execution engine

The scheduler must remain lightweight, deterministic, and testable.

A callable scan service must also exist so that operational scanning can be exercised directly in tests without relying on real timers.

---

## 10. Retry Orchestration

EPIC 18 established retry rules. EPIC 19 must make retry an actively controlled operational behavior.

Retry orchestration must:

- trigger retries only through approved operational control paths
- track retry attempts and retry outcomes
- prevent duplicate concurrent retries
- stop deterministically at retry cutoff
- mark retry exhaustion explicitly
- emit structured audit events for each retry decision

Retry orchestration must protect against:

- retry storms
- recursive self-triggering
- duplicate recovery from repeated scans
- concurrent retry triggers from multiple control paths
- retry without traceable audit evidence

Retry budget must become a first-class concept and should be represented explicitly through fields such as:

- retry_count
- retry_limit
- retry_budget_remaining

---

## 11. Controlled Re-entry

If the implementation distinguishes between retry and re-entry, that distinction must be modeled explicitly.

### Retry

Retry means re-executing a run after a recoverable failure under the runtime retry policy.

### Re-entry

Re-entry means re-admitting a run into runtime processing from a recoverable operational condition, such as a stuck or expired-lease incident, where direct retry semantics alone are not sufficient.

If the current runtime model does not truly distinguish these paths, the implementation should prefer one explicit model rather than introducing ambiguous terminology.

No recovery path may bypass lifecycle guards.

---

## 12. Operational State Model

A structured operational state model must be introduced.

This model exists alongside lifecycle state and must remain distinct from it.

At minimum, the operational condition model should support states such as:

- healthy
- retry_pending
- retry_in_progress
- reentry_pending
- stuck_detected
- recovery_skipped
- terminal_confirmed
- recovery_exhausted

The purpose of this model is to expose runtime-operational truth in a way that is queryable, auditable, and safe.

It must not replace lifecycle state, and it must not allow ambiguous interpretation of run condition.

---

## 13. Operational Metadata Surface

Each run must expose structured operational metadata.

This metadata should include, at minimum:

- retry_count
- retry_limit
- retry_budget_remaining
- last_failure_code
- last_failure_at
- last_recovery_attempt_at
- last_recovery_decision
- last_recovery_reason_code
- recovery_attempt_count
- stuck_detected_at
- lease_expired_at
- terminal_confirmed_at
- last_operational_event_at

This metadata must be:

- deterministic
- queryable
- consistent with runtime facts
- separate from business summary and lifecycle fields
- updated only through explicit control paths

The system must preserve a strict distinction between product business state and operational metadata.

---

## 14. Operational Audit Trail

Every operational decision must be traceable through structured audit data.

This is not simple logging. This is structured operational history.

At minimum, the system must record events such as:

- stuck_run_detected
- lease_expired_detected
- retry_eligibility_evaluated
- retry_triggered
- retry_skipped
- retry_exhausted
- recovery_reentry_triggered
- terminal_failure_confirmed
- recovery_noop_already_handled

Each audit event should include fields such as:

- event_id
- run_id
- event_type
- event_time
- actor_type
- decision
- reason_code
- reason_detail
- previous_operational_state
- new_operational_state
- related_failure_code
- attempt_number
- correlation_id or recovery_cycle_id

No operational recovery decision may occur without a corresponding audit event.

Audit data must be suitable for deterministic tests and future operational investigations.

---

## 15. Observability Primitives

EPIC 19 requires minimal but structured observability primitives.

These primitives must remain intentionally lightweight and must not expand into a full monitoring platform.

At minimum, the system should track counters such as:

- runs_scanned_total
- stuck_runs_detected_total
- recovery_attempts_total
- recovery_success_total
- recovery_failure_total
- retries_triggered_total
- retries_exhausted_total
- terminal_failures_confirmed_total
- recovery_skipped_total

The system should also expose structured classification visibility using dimensions such as:

- failure_code
- recovery_decision
- skip_reason
- retry_outcome

These observability signals must be queryable and testable.

They must not exist only as ad hoc logs.

---

## 16. Operational Read Surface

The system must expose operational state through a structured read surface.

This may be implemented by:

- extending the existing run view with a nested operational section
- or exposing a dedicated operational read model

The preferred rule is clarity over convenience.

If the current product read model is strongly product-facing, the operational data should be introduced as a nested section instead of polluting the top-level contract.

A representative operational section may include:

- condition
- retry_count
- retry_limit
- retry_budget_remaining
- last_failure_code
- last_failure_at
- last_recovery_decision
- last_recovery_reason_code
- recovery_attempt_count
- terminal_confirmed
- last_operational_event_at

This read surface must remain consistent with the underlying runtime and operational audit state.

---

## 17. Safety Rules

The following rules are mandatory:

1. Recovery must not violate lifecycle invariants.
2. Completed runs must never re-enter processing.
3. Retry must not bypass review, export, or product flow rules.
4. Scan-only operations must not cause hidden mutation.
5. Recovery decisions must be idempotent.
6. No run may be recovered twice for the same incident.
7. Retry exhaustion must produce explicit terminal operational outcome.
8. Repeated scheduler execution must remain no-op safe for already-settled incidents.
9. All operational recovery decisions must emit structured audit events.
10. Operational state must never replace lifecycle truth.

These are hard invariants, not implementation suggestions.

---

## 18. Suggested Internal Components

The implementation should remain simple, but responsibility boundaries must be explicit.

Suggested logical components include:

### Policies

- RecoveryEligibilityPolicy
- StuckRunPolicy
- RetryBudgetPolicy

### Services

- RecoveryLoopService
- OperationalScanService
- RetryOrchestrator
- OperationalAuditService
- OperationalMetricsService

### Models

- RunOperationalState
- RecoveryDecision
- RecoveryEvaluationResult
- OperationalAuditEvent
- OperationalCountersSnapshot

### Repositories or Stores

- OperationalAuditRepository
- optional operational counters repository or queryable metrics store

These names are illustrative and may be adapted to existing project naming conventions, but the separation of responsibilities must remain.

---

## 19. Implementation Plan

### Phase A - Model and Policy Baseline

Implement:

- operational state model
- recovery decision model
- recovery eligibility policy
- stuck detection policy
- retry budget representation
- operational audit event schema

This phase must come first. Scheduler-first implementation would be structurally wrong.

### Phase B - Recovery Loop

Implement:

- candidate selection
- eligibility evaluation
- retry or re-entry decision flow
- act-time revalidation
- idempotency protection
- recovery outcome persistence

### Phase C - Scheduler Integration

Implement:

- lightweight periodic trigger
- deterministic scan cycle execution
- bounded scan processing
- repeated-invocation no-op behavior
- testable callable scan path

### Phase D - Observability and Read Surface

Implement:

- operational counters
- classification tracking
- operational metadata projection
- structured operational read surface

### Phase E - Hardening

Implement:

- duplicate trigger protection
- exhausted retry enforcement
- incident-level no-double-recovery protection
- mixed-population scan consistency
- recovery race condition protection

---

## 20. Test Strategy

EPIC 19 requires strong automated validation.

### Policy Tests

- failed run eligible for retry
- non-recoverable failure rejected
- exhausted retry budget rejected
- stuck run correctly classified
- cancelled or completed run not recoverable

### Recovery Loop Tests

- retry triggered once for eligible failure
- second scan produces noop for same incident
- same incident cannot recover twice
- skipped recovery records structured reason
- terminal confirmation emitted correctly

### Scheduler Tests

- scheduler detects stuck processing run
- expired lease leads to recovery evaluation
- repeated scheduler ticks do not duplicate recovery
- mixed healthy and unhealthy populations are handled safely

### Audit Tests

- every operational decision emits audit event
- audit event includes structured reason code
- retry attempt numbering remains correct
- terminal confirmation is traceable

### Observability Tests

- counters increment deterministically
- recovery success and failure tracking work
- classification visibility is queryable
- operational metadata projection is consistent

### Safety Tests

- no infinite retry loop exists
- completed run never re-enters processing
- recovery cannot bypass lifecycle rules
- scan-only invocation does not mutate hidden state
- concurrent recovery attempts remain bounded and deterministic

This EPIC must not be closed without explicit safety coverage.

---

## 21. Closure Criteria

EPIC 19 is complete only when all of the following are true:

- failed and stuck runs are automatically detected
- recovery eligibility is policy-driven and deterministic
- retry orchestration is active, bounded, and test-covered
- repeated scans remain idempotent and safe
- operational metadata is exposed consistently
- all operational decisions emit structured audit records
- observability primitives are queryable
- no infinite or hidden recovery loop exists
- standard recoverable runtime failures no longer require manual intervention

---

## 22. Final Standard

A reliable system survives failure.

A production system detects failure, evaluates recovery deterministically, recovers safely where allowed, stops explicitly where not allowed, and proves every decision through structured operational evidence.

EPIC 19 exists to establish that standard for InvoMatch.