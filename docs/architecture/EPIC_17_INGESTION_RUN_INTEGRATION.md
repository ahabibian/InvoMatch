# EPIC 17 — Ingestion → Run Integration & Entry Flow

## 1. Purpose

This EPIC connects the ingestion subsystem to the reconciliation run lifecycle.

The goal is to establish a deterministic, contract-driven entry flow from external raw input to normalized validated entities, and from those entities to a reconciliation run.

After this EPIC, the system must support the following end-to-end flow as a single operational pipeline:

raw input → ingestion → run creation → matching → review → resolution → export

This EPIC does not introduce new ingestion logic.  
It defines the integration boundary, orchestration rules, creation policies, idempotency behavior, traceability model, and failure handling required to turn ingestion into the official entry path of the product flow.

---

## 2. Problem Statement

EPIC 16 established a valid ingestion subsystem with normalization, validation, duplicate handling, conflict detection, traceability foundations, and repository seams.

However, ingestion is still operationally isolated from the reconciliation lifecycle.

At present:

- ingestion can process input
- reconciliation runs can exist
- matching/review/export flows exist

But there is no canonical system entry path that deterministically connects them.

This creates a structural gap:
- validated input is not yet the official source of run creation
- external input may still bypass ingestion assumptions
- traceability from run back to input is incomplete
- idempotent entry behavior is not yet defined at the ingest-to-run boundary

EPIC 17 closes that gap.

---

## 3. Scope

This EPIC includes:

- canonical ingestion-based run entry flow
- ingestion-to-run mapping definition
- run creation policy from validated ingestion output
- idempotent run creation behavior
- traceability chain from input to run
- deterministic failure handling at the integration boundary
- enforcement that raw external input cannot bypass ingestion contracts

This EPIC excludes:

- UI/upload interfaces
- external ERP or bank connectors
- deployment/infrastructure work
- observability systems
- advanced matching logic changes

---

## 4. Core Architectural Principle

External input must never enter run creation or matching directly.

The only valid path for external operational data is:

raw input → ingestion gateway/service → validated normalized ingestion result → run creation integration layer → reconciliation lifecycle

Ingestion becomes the single source of truth for input correctness at the system boundary.

---

## 5. Target End-to-End Flow

The target lifecycle after this EPIC is:

1. External input is received through an ingestion-based entry point.
2. The ingestion subsystem normalizes, validates, deduplicates, and classifies input.
3. A validated ingestion result is produced.
4. A run creation integration layer evaluates run creation policy.
5. A reconciliation run is created only from accepted validated ingestion outputs.
6. The run proceeds through matching, review, resolution, and export using the existing lifecycle.

No raw input is passed directly into reconciliation internals.

---

## 6. Canonical Entry Point

A canonical ingestion-based entry point must be defined.

Representative surfaces may include:

- POST /api/reconciliation/runs/ingest
- create_run_from_ingestion(...)
- IngestionRunIntegrationService

The chosen surface must behave as an application boundary, not as a convenience wrapper.

Responsibilities of the entry point:

- accept external input in ingestion-supported shape
- invoke ingestion deterministically
- obtain validated normalized ingestion output
- apply run creation policy
- create or reuse a reconciliation run deterministically
- return a stable product-facing result
- expose clear failure outcomes

Non-responsibilities:

- performing matching logic inline
- hiding ingestion errors
- creating runs from partially unknown state
- bypassing ingestion contracts

---

## 7. Integration Components

The following integration-layer components are required.

### 7.1 IngestionRunIntegrationService

Application service responsible for coordinating:

- ingestion invocation
- validated result inspection
- run creation policy evaluation
- idempotent run creation decision
- traceability linkage
- handoff into reconciliation lifecycle

This service is the canonical orchestration boundary for ingest-to-run flow.

### 7.2 Ingestion-to-Run Mapper

A dedicated mapper converts accepted normalized ingestion entities into internal run inputs.

Responsibilities:

- map normalized invoices to reconciliation invoice inputs
- map normalized payments to reconciliation payment inputs
- preserve deterministic field transformation
- attach provenance/traceability references where required

Constraints:

- no hidden enrichment
- no heuristic mutation
- no direct use of raw payloads
- fully unit-testable

### 7.3 Ingestion Run Creation Policy

A policy component defines whether a run may be created from a given ingestion result.

This policy must explicitly handle:

- full success
- partial acceptance
- full rejection
- conflict outcomes
- empty accepted datasets
- duplicate/idempotent replay cases

### 7.4 Traceability Link Model

A traceability model links:

raw source input → ingestion batch/result → accepted normalized entities → reconciliation run

This must be queryable from the run side.

---

## 8. Canonical Data/Control Flow

The canonical control flow is:

1. receive ingest request
2. persist/resolve ingestion batch identity
3. execute ingestion gateway/service
4. obtain ingestion result
5. evaluate creation policy
6. if not creatable, return deterministic failure outcome
7. if idempotent replay, reuse or return existing run
8. map accepted normalized entities to run inputs
9. create run with traceability metadata
10. hand off run to existing reconciliation lifecycle
11. expose stable result to caller

---

## 9. Ingestion → Run Mapping Rules

Mapping must be explicit and deterministic.

### 9.1 Source of Truth

Only accepted normalized entities are eligible for mapping into run input.

Rejected, conflicted, or invalid entities must never enter run creation input.

### 9.2 Invoice Mapping

Accepted normalized invoices map into internal reconciliation invoice inputs.

Rules:
- field names and transformations must be explicit
- identity keys used by ingestion remain traceable
- provenance reference to ingestion entity should be preserved where practical
- no raw fallback values are allowed

### 9.3 Payment Mapping

Accepted normalized payments map into internal reconciliation payment inputs.

Rules:
- transformations must be field-explicit
- date/amount/currency semantics must remain deterministic
- provenance reference to ingestion entity should be preserved where practical
- no hidden normalization should occur at mapping time

### 9.4 Mapping Constraints

The mapper must not:
- re-normalize already normalized data
- reinterpret invalid records
- silently drop accepted fields
- inject synthetic values without explicit documented policy

---

## 10. Run Creation Policy

Run creation policy must be explicit and deterministic.

### 10.1 Creatable Outcome

A run may be created only if:
- ingestion completed deterministically
- accepted normalized invoices exist
- accepted normalized payments exist
- no blocking conflict state is present
- policy rules permit creation

### 10.2 Partial Ingestion Outcome

Partial ingestion is allowed only if the remaining accepted dataset is still operationally valid for reconciliation.

Minimum rule:
- if accepted invoice count = 0, no run
- if accepted payment count = 0, no run
- if both sides contain at least one accepted record, run creation may proceed even if some records were rejected

When this occurs, the run must carry partial-ingestion trace metadata.

### 10.3 Full Failure Outcome

If ingestion results in zero creatable dataset, run creation must not occur.

The system must return a deterministic failure result rather than creating an empty or misleading run.

### 10.4 Conflict Outcome

If ingestion detects blocking identity or semantic conflict that invalidates run creation assumptions, run creation must fail deterministically.

Conflict handling must be explicit and test-covered.

---

## 11. Idempotent Run Creation Policy

Idempotency must exist at the ingest-to-run boundary.

### 11.1 Batch Identity

Run creation idempotency must be based on a stable ingestion batch identity and its validated accepted outcome.

### 11.2 Replay Behavior

For the same ingestion batch identity:

- same normalized accepted outcome → return existing run / reuse existing run result
- conflicting outcome under same identity → fail with deterministic conflict error
- already finalized prior ingestion-to-run creation → do not create a second inconsistent run

### 11.3 Duplicate Entity Presence Across Different Batches

Duplicate entities across distinct batches do not automatically imply run reuse.

This case must remain traceable and policy-driven, but batch replay and cross-batch overlap must not be conflated.

---

## 12. Traceability Model

The system must support traceability from run back to input.

At minimum, a run created from ingestion must retain or reference:

- ingestion batch id
- ingestion result id or equivalent reference
- source reference metadata if available
- accepted invoice count
- accepted payment count
- rejected/conflict counts
- idempotency decision
- creation policy mode
- normalized entity provenance references or resolvable links

Traceability must support:
- debugging
- auditability
- replay analysis
- support investigation
- explaining why a run was or was not created

---

## 13. Failure Handling and Recovery

Failure handling must be deterministic.

### 13.1 Failure Before Run Creation

If ingestion fails before a validated result is produced:
- no run is created
- failure is returned explicitly
- no partial hidden state is treated as a valid run input

### 13.2 Failure During Mapping

If validated accepted entities cannot be mapped to run input:
- run creation must fail
- failure must be explicit
- partial mapped state must not leak into lifecycle state

### 13.3 Failure During Run Creation

If mapping succeeds but run creation fails:
- the failure must be exposed deterministically
- traceability context should still allow support/debug visibility
- no ambiguous duplicate recovery behavior may remain

### 13.4 Recovery Principle

Recovery must be replay-safe.

A retry of the same ingest request must obey idempotent policy, not create inconsistent duplicate runs.

---

## 14. Boundary Enforcement Rules

The following must hold after this EPIC:

- external raw input cannot directly create reconciliation runs
- matching services do not consume raw external payloads
- run creation from external operational data must pass through ingestion contracts
- ingestion validated output becomes the only acceptable source for external-input-driven run creation

Any pre-existing bypass path must either be removed, restricted, or explicitly classified as internal-only/test-only.

---

## 15. API/Product Surface Expectations

If an API entry point is exposed, it must return a stable product-facing response.

At minimum, the response should clearly represent:
- whether ingestion succeeded
- whether a run was created, reused, or rejected
- run identifier if created/reused
- deterministic error information if rejected
- traceable linkage metadata where appropriate

The product surface must not expose internal ingestion implementation details unnecessarily, but it must not hide material outcome states.

---

## 16. Implementation Plan

Implementation should proceed in this order:

1. define architecture and policy document
2. define integration service contract
3. define mapper contract
4. define run creation policy rules
5. define idempotent replay policy
6. define traceability fields/model extensions
7. implement canonical entry point
8. integrate with existing reconciliation lifecycle
9. enforce boundary rules / remove bypasses
10. add unit, integration, and contract tests
11. verify end-to-end executable flow

---

## 17. Test Strategy

Testing must cover three layers.

### 17.1 Unit Tests
- ingestion-to-run mapper behavior
- run creation policy decisions
- idempotent replay decisions
- failure classification behavior

### 17.2 Integration Tests
- ingestion success → run created
- partial ingestion → policy-respecting result
- replay same batch → run reused/deterministic result
- mapping failure → no run
- blocking conflict → no run
- run traceability links preserved

### 17.3 End-to-End Tests
- raw input → ingestion → run → matching → review → export
- run can be traced back to ingestion batch/input reference
- no direct raw bypass path remains for external operational input

---

## 18. Closure Criteria

EPIC 17 is complete only if:

- a canonical ingestion-based run entry point exists
- runs are created only from validated ingestion outputs
- ingestion-to-run mapping is deterministic and tested
- duplicate ingestion replay does not create inconsistent runs
- end-to-end flow from ingestion to export is executable
- run-to-input traceability is verifiable
- failure scenarios are deterministic and tested
- no external raw-input bypass path remains into core reconciliation flow

---

## 19. Summary

EPIC 16 made ingestion valid.
EPIC 17 makes ingestion operational.

This EPIC is the point where input correctness becomes structurally connected to the lifecycle of the product.

Once complete, the system will no longer consist of isolated subsystems.
It will have a single deterministic entry path from external data to final reconciliation output.