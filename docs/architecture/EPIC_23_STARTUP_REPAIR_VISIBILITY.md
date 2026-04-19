# EPIC 23 - Startup Consistency Repair & Operational Visibility

## 1. Purpose

EPIC 22 established restart-safe persistence integrity, restart-aware review truth continuity, and deterministic restart consistency repair rules for key lifecycle/business-truth mismatches.

At the end of EPIC 22, the system can already detect and repair important restart-induced inconsistencies between persisted run lifecycle state and persisted review truth.

However, that repair capability still exists only as an internal service-level behavior.

This is not sufficient for a production-grade SaaS system.

A restart-safe system is not fully operationally safe if:

- repair logic is not executed automatically at application startup
- repair decisions are not visible to operators
- repair actions are not auditable
- health and readiness surfaces do not reflect startup consistency outcomes
- startup repair can conflict with lease ownership or recovery policy

The purpose of EPIC 23 is to operationalize startup consistency repair so that it becomes part of system behavior, not just internal test-covered logic.

---

## 2. Production Gap Being Closed

Current repo reality at the start of EPIC 23 is:

- startup repair logic exists in `RestartConsistencyRepairService`
- runtime recovery logic exists in `RuntimeRecoveryService`
- operational recovery loop and observability foundations exist in:
  - `RecoveryLoopService`
  - `RecoveryEligibilityPolicy`
  - `OperationalScanService`
  - `OperationalMetricsService`
- persisted lease ownership and lease expiry exist in run stores
- `main.py` does not yet perform startup orchestration
- `api/health.py` currently exposes only a minimal liveness endpoint
- no startup consistency scan summary is exposed to operators
- no readiness semantics exist for startup repair success/failure
- startup repair actions are not yet integrated into operational audit/metrics surfaces

Therefore the real gap is not repair correctness in isolation.

The real gap is lack of startup operationalization, visibility, and accountability.

---

## 3. Current Repo Reality

### 3.1 Existing startup wiring

Application wiring currently occurs in `src/invomatch/main.py`.

At EPIC 23 start, `create_app()` wires:

- run store
- run registry
- reconcile function
- ingestion runtime adapter
- review store
- export services
- artifact query service
- export readiness evaluator
- action service
- input processing services
- API routers

But the application does not yet define:

- startup lifecycle orchestration
- startup scan coordinator
- startup repair result state
- startup repair audit emission
- readiness gate derived from startup scan outcome

### 3.2 Existing health surface

Current `src/invomatch/api/health.py` exposes only:

- `GET /health`

Current behavior is a static liveness-style response and does not reflect:

- startup scan success/failure
- repairs applied
- unresolved inconsistencies
- degraded startup condition
- readiness state

### 3.3 Existing restart repair behavior

`src/invomatch/services/restart_consistency_repair_service.py` already provides per-run repair logic.

Current covered repair patterns are:

- `processing -> review_required` when active review cases exist
- `review_required -> completed` when no active review remains
- `completed -> review_required` when active review exists for a completed run
- no-op result when no repair is needed

Current result model is minimal:

- `run_id`
- `original_status`
- `repaired_status`
- `reason`

This is sufficient for unit-level repair correctness, but insufficient for startup orchestration and operator observability.

### 3.4 Existing runtime recovery behavior

`src/invomatch/services/runtime_recovery_service.py` already performs runtime-side recovery scanning and decisions for persisted processing runs.

It can:

- scan processing runs
- assess stuck conditions
- fail unrecoverable stuck runs
- surface reentry candidates
- preserve untouched active processing runs

This is important because startup repair must not conflict with runtime recovery logic.

### 3.5 Existing operational recovery foundations

The system already has operational recovery architecture in:

- `RecoveryLoopService`
- `RecoveryEligibilityPolicy`
- `OperationalScanService`
- `OperationalMetricsService`
- operational audit integration

This means EPIC 23 must align with the operational recovery model rather than invent a parallel observability design.

### 3.6 Existing persistence and lease reality

Run stores already persist:

- `claimed_by`
- `claimed_at`
- `lease_expires_at`
- `attempt_count`
- `version`

Therefore startup repair policy can and must respect active lease ownership.

---

## 4. EPIC Objective

Operationalize restart consistency repair so that the system can:

- scan persisted runs for lifecycle/business-truth mismatches on startup
- repair eligible mismatches automatically and deterministically
- skip repair when runtime safety rules require skipping
- record startup repair outcomes in operational audit/metrics surfaces
- expose startup repair outcomes through operator-facing health/readiness surfaces
- preserve alignment with runtime recovery policy, lease semantics, and terminal protection

After this EPIC, restart repair must become part of application startup behavior.

---

## 5. Scope

This EPIC includes:

1. startup consistency scan orchestration
2. startup repair decision policy
3. active lease protection during startup repair
4. terminal run protection during startup repair
5. startup repair result model
6. startup repair audit and metrics recording
7. health/readiness exposure for startup repair outcome
8. failure scenario handling for startup scan and repair
9. scenario-based validation for startup repair visibility and recovery alignment

This EPIC does not include:

- new matching logic
- end-user workflow changes
- distributed repair workers
- multi-node startup coordination
- external monitoring integrations
- dashboard platform design
- UI redesign
- generic observability overhaul

---

## 6. Design Principles

### 6.1 No guessing, repo-grounded only

All startup repair behavior must be built on existing repo truth:

- existing run store semantics
- existing lease semantics
- existing restart consistency repair logic
- existing operational recovery model
- existing audit/metrics foundations

### 6.2 Architecture first

Startup repair behavior must be policy-defined before implementation.

### 6.3 Deterministic before convenient

Startup scan and repair outcomes must be deterministic and reproducible from persisted truth.

### 6.4 Visibility is required

Repair must never occur silently.

### 6.5 Safety over aggressiveness

If startup repair conflicts with lease ownership, runtime recovery safety, or terminal protection, the system must prefer skip/report over unsafe mutation.

### 6.6 Reuse existing recovery patterns

EPIC 23 must align with existing operational recovery architecture rather than creating an isolated startup-only observability model.

---

## 7. Startup Consistency Scan Model

A startup consistency scan is a one-time application-start process that inspects persisted runs and determines whether restart-induced lifecycle/business-truth mismatches are present.

### 7.1 Scan target set

The scan target set must include persisted runs whose state can plausibly drift from persisted review truth.

At minimum, the scan must consider runs in these business states:

- `processing`
- `review_required`
- `completed`

The exact candidate selection mechanism must be explicit in implementation and should avoid scanning irrelevant states unnecessarily.

### 7.2 Scan inputs

The scan operates on persisted truth only:

- persisted run record from run store
- persisted review items / review truth from review store
- persisted lease ownership metadata
- persisted lifecycle status
- persisted terminal/error state where relevant

### 7.3 Scan output

The scan must produce a startup summary object describing:

- how many runs were scanned
- how many mismatches were found
- how many repairs were applied
- how many runs were skipped
- how many unresolved inconsistencies remain
- whether the scan failed
- whether the application should be considered ready

---

## 8. Startup Repair Decision Policy

Startup repair must be policy-driven and explicit.

### 8.1 Repairable mismatch classes

At minimum, the following mismatch classes are considered eligible for deterministic startup repair, subject to safety guards:

1. `processing -> review_required`
   - when active review truth exists

2. `review_required -> completed`
   - when no active review truth remains

3. `completed -> review_required`
   - when active review truth exists for a completed run

These repair classes already exist at service level and are the baseline repair behaviors operationalized by this EPIC.

### 8.2 No-op class

If no mismatch exists, the result must be reported as a no-op rather than an applied repair.

### 8.3 Report-only classes

Some startup findings must be reportable but not auto-repairable.

These include at minimum:

- runs protected by active valid lease ownership
- runs blocked by terminal protection policy
- startup scan failure cases
- any run whose persisted state changes during scan/revalidation
- any run whose repair safety cannot be established deterministically

### 8.4 Safety-first rule

If a startup scan cannot safely prove that repair is allowed, it must not apply repair.

It must record a skipped or unresolved outcome instead.

---

## 9. Active Lease Protection Rules

Active lease protection is mandatory.

### 9.1 Rule

Startup repair must not mutate a run if that run is currently protected by a valid active lease.

### 9.2 Why

A valid lease means another runtime worker may still legitimately own execution responsibility for that run.

Applying startup repair to an actively leased run risks breaking:

- runtime ownership
- lifecycle safety
- recovery alignment
- execution consistency

### 9.3 Required behavior

If a run has:

- `claimed_by` not null
- `lease_expires_at` present
- lease still valid at startup scan time

then startup repair must not modify the run.

It must produce a startup result classified as:

- skipped due to active lease

### 9.4 Expired lease

If lease metadata exists but lease is expired, the run may be eligible for further startup evaluation, subject to recovery/repair policy.

Expired lease alone does not mean "repair immediately".
It only means "not blocked by active lease".

---

## 10. Terminal Protection Rules

Startup repair must respect terminal protection rules.

### 10.1 Protected states

The system must not blindly mutate all terminal states.

At minimum, startup policy must explicitly distinguish:

- `completed`
- `failed`
- `cancelled`

### 10.2 Allowed exceptional case

A previously completed run may be moved back to `review_required` when persisted active review truth exists.

This is already part of existing repair logic and is an explicit business-truth restoration case.

### 10.3 Restricted terminal mutation

Other terminal states, especially terminal failure or cancellation states, must not be altered by startup repair unless policy explicitly authorizes such change.

### 10.4 Rule

If startup repair encounters a terminal-protected state that is not explicitly repairable under policy, the system must:

- not mutate the run
- record the finding
- classify it as skipped or unresolved depending on severity

---

## 11. Recovery Loop Alignment Rules

Startup repair must not conflict with runtime recovery behavior.

### 11.1 No duplication of runtime recovery role

Startup repair is not a replacement for runtime recovery scanning.

Startup repair fixes lifecycle/business-truth mismatches.
Runtime recovery handles stuck processing, reentry, and recovery eligibility.

### 11.2 Startup repair must not bypass:

- retry eligibility rules
- reentry eligibility rules
- active recovery in progress protections
- lease ownership protections
- terminal failure confirmation rules

### 11.3 Alignment requirement

Startup repair and runtime recovery must satisfy this separation:

- startup repair restores persisted business truth consistency
- runtime recovery handles operational continuation or failure decisions

### 11.4 Conflict resolution rule

If startup repair and runtime recovery semantics conflict, startup repair must defer and report rather than mutate unsafely.

---

## 12. Startup Repair Result Model

A dedicated startup result model is required.

At minimum it must support these summary fields:

- `total_runs_scanned`
- `repairable_mismatches_found`
- `repairs_applied`
- `no_repair_needed_count`
- `skipped_due_to_active_lease`
- `skipped_due_to_terminal_protection`
- `unresolved_mismatches`
- `startup_scan_failed`
- `startup_scan_completed_at`

### 12.1 Per-run result detail

In addition to summary fields, each processed run should produce a structured detail entry with fields such as:

- `run_id`
- `original_status`
- `result_type`
  - `repaired`
  - `skipped`
  - `no_op`
  - `unresolved`
  - `failed`
- `repaired_status`
- `reason`
- `source`
  - `startup_consistency_scan`
- `lease_blocked`
- `terminal_protected`

Exact naming may vary in implementation, but equivalent semantics are required.

### 12.2 Application state exposure

The final startup result summary must be stored on application state so that health/readiness surfaces can expose current startup condition.

---

## 13. Audit Model for Startup Repair

Startup repair must be auditable.

### 13.1 Requirement

Each startup repair action and each startup skip/unresolved outcome must produce an operationally meaningful record.

### 13.2 Minimum audit semantics

Each recorded startup repair event must capture at least:

- `run_id`
- `event_type`
- `original_status`
- `new_status` or effective outcome
- `reason`
- `source = startup_consistency_scan`
- whether action was taken
- any safety block classification if skipped

### 13.3 Alignment with existing operational audit

Where possible, startup repair audit should reuse the existing operational audit writing style rather than inventing a disconnected event format.

### 13.4 No silent repair

Silent mutation of persisted runs at startup is forbidden.

---

## 14. Metrics Model for Startup Repair

Startup repair must be visible in operational metrics.

### 14.1 Requirement

Startup repair outcomes must increment explicit counters, not just produce local return values.

### 14.2 Minimum counters

At minimum, metrics must support equivalent visibility for:

- startup scan attempts
- startup repair actions applied
- startup repair no-op outcomes
- startup repair skipped outcomes
- startup unresolved outcomes
- startup scan failures

### 14.3 Alignment rule

This should extend the existing operational metrics surface rather than introducing a disconnected startup-only metrics subsystem.

---

## 15. Operator Visibility Model

Operator visibility must be explicit and minimal.

This EPIC does not build dashboards.
It builds trustworthy operator-facing system surfaces.

### 15.1 Operators must be able to answer:

- did startup scan run successfully?
- did startup repair apply any changes?
- which runs were repaired?
- which runs were skipped?
- why were they skipped?
- do unresolved inconsistencies remain?
- is the application ready for normal operation?

### 15.2 Minimum exposure surfaces

At minimum, this EPIC must provide operator visibility through:

- health endpoint
- readiness endpoint
- startup result summary exposed from application state
- audit/metrics observability surfaces

---

## 16. Health and Readiness Exposure Semantics

Health and readiness must be distinct.

### 16.1 Health semantics

Health answers:
Is the application alive?

Health should remain true if:

- the API process is running
- the app booted
- startup orchestration did not fatally crash the process

Health should not try to represent full operational safety.

### 16.2 Readiness semantics

Readiness answers:
Is the application in a state that is safe to serve normally after startup consistency evaluation?

Readiness must consider startup scan result.

### 16.3 Required readiness states

At minimum, readiness semantics must support these cases:

1. **ready**
   - startup scan succeeded
   - no critical unresolved inconsistencies remain

2. **degraded but ready**
   - startup scan succeeded
   - some non-critical skipped/unresolved conditions remain
   - these do not block safe normal operation

3. **not ready**
   - startup scan failed
   - or unresolved critical inconsistency remains
   - or startup state cannot be trusted for safe operation

### 16.4 Example readiness interpretations

- scan success + repairs applied + no unresolved critical mismatch -> ready
- scan success + skipped due to active lease only -> typically degraded but ready
- scan success + unresolved critical consistency drift -> not ready
- startup scan exception/failure -> not ready

### 16.5 Explicitness rule

Readiness logic must be deterministic, documented, and testable.

---

## 17. Failure Scenario Matrix

Startup scan must define deterministic handling for failure and edge cases.

### 17.1 Repairable mismatch at startup

Condition:
- persisted run and review truth mismatch is detected
- no active lease block
- no terminal protection block

Expected result:
- repair applied
- audit recorded
- metrics recorded
- reflected in startup summary

### 17.2 Non-repairable mismatch at startup

Condition:
- inconsistency exists but policy does not permit safe auto-repair

Expected result:
- no mutation
- unresolved or skipped recorded
- reflected in readiness evaluation

### 17.3 Terminal-protected run

Condition:
- mismatch exists but run is protected by terminal policy

Expected result:
- no mutation
- skipped due to terminal protection
- operator-visible

### 17.4 Active lease conflict

Condition:
- mismatch exists but valid active lease is present

Expected result:
- no mutation
- skipped due to active lease
- operator-visible
- readiness determined by severity policy

### 17.5 Review truth / lifecycle truth drift

Condition:
- persisted review truth and run status diverge

Expected result:
- eligible deterministic repair if allowed
- otherwise explicit unresolved/skip result

### 17.6 Startup scan failure

Condition:
- scan cannot complete due to exception or infrastructure error

Expected result:
- startup failure recorded
- readiness becomes not ready
- health remains a process/liveness concern unless startup crashes process entirely

---

## 18. Scenario 7 - Startup Repair Visibility & Recovery Alignment

### Goal

Validate that startup consistency scan:

- detects repairable mismatches
- repairs eligible runs correctly
- preserves terminal protection
- respects active lease ownership
- exposes repair results through health/readiness surfaces
- does not conflict with recovery loop behavior

### Core flows

1. startup with repairable mismatch  
2. startup with unresolved mismatch  
3. startup with terminal run inconsistency  
4. startup with active lease conflict  
5. startup with startup-scan failure  

### Expected validation themes

- startup summary is deterministic
- operator surfaces reflect real startup outcome
- startup repair respects lease and terminal rules
- runtime recovery alignment is preserved
- no silent repair occurs

---

## 19. Required Scenario Re-Runs

Because EPIC 23 touches:

- restart consistency
- persistence integrity
- recovery behavior
- run view correctness
- operational recovery visibility

the following permanent scenarios must be re-run before closure:

- Scenario 1 - Happy Path Full Flow
- Scenario 2 - Review Resolution Flow
- Scenario 4 - Runtime Failure Terminalization
- Scenario 6 - Restart Recovery Consistency

Additionally, EPIC 23 must introduce:

- Scenario 7 - Startup Repair Visibility & Recovery Alignment

---

## 20. Implementation Plan

Implementation must follow this order.

### Step 1 - Add architecture-backed startup scan coordinator

Introduce a startup orchestration component responsible for:

- selecting startup scan candidates
- evaluating lease and terminal protection
- invoking restart repair for eligible runs
- building startup result summary
- recording audit/metrics
- surfacing final startup state

### Step 2 - Extend startup result modeling

Add structured startup scan result models for:

- summary
- per-run detail

### Step 3 - Integrate startup scan into application startup

Update `main.py` so application startup performs startup consistency scanning and stores result in `app.state`.

### Step 4 - Extend health surface

Upgrade `/health` from static liveness response to a structured health response.

### Step 5 - Add `/readiness`

Introduce readiness endpoint backed by startup scan result semantics.

### Step 6 - Integrate audit and metrics

Record startup scan and repair outcomes into existing operational observability patterns.

### Step 7 - Add targeted tests

Add tests for:

- startup repair orchestration
- active lease skip behavior
- terminal protection skip behavior
- startup scan failure behavior
- health/readiness exposure
- metrics/audit recording

### Step 8 - Execute scenario validation and regressions

Run Scenario 7 and required scenario re-runs.

---

## 21. Test Strategy

### 21.1 Unit coverage

Add/extend unit coverage for:

- startup coordinator decision logic
- lease blocking behavior
- terminal protection behavior
- startup summary classification
- readiness evaluation logic

### 21.2 Integration coverage

Add integration coverage for:

- startup scan orchestration with real run/review persistence
- audit/metrics recording from startup scan
- application startup state exposure

### 21.3 API coverage

Add API tests for:

- `/health`
- `/readiness`

These tests must verify:

- startup scan success
- startup scan degraded state
- startup scan failure state

### 21.4 Scenario coverage

Implement Scenario 7 and re-run required permanent scenarios.

### 21.5 Regression requirement

EPIC 22 restart consistency behavior must remain green.

---

## 22. Closure Criteria

EPIC 23 is complete only if:

- startup consistency scan is deterministic
- eligible mismatches are auto-repaired correctly
- active lease protection is enforced
- terminal protection is enforced
- repair actions are auditable
- repair outcomes are visible to operators
- health and readiness reflect startup repair outcomes
- Scenario 7 passes
- required scenario re-runs remain green
- repo evidence proves implementation, tests, and closure
- no part of the EPIC is justified by assumption alone

---

## 23. Key Principle

A restart-safe system is stronger when repair is not only possible, but operationalized, visible, and accountable.

EPIC 23 closes the gap between "repair exists in code" and "repair exists as trustworthy system behavior."
