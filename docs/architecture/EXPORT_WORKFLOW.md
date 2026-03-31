# EXPORT WORKFLOW

## Purpose

This document defines the export workflow for product-facing run export actions.

The goal is to replace placeholder export behavior with a real, deterministic, auditable export flow while preserving the product contract boundary.

Export is treated as a controlled side workflow, not as an implicit rewrite of the main run lifecycle.

---

## Scope

This document covers:

- export eligibility
- export request handling
- artifact generation
- artifact naming and storage rules
- export status model
- repeated export behavior
- failure handling
- audit requirements

This document does NOT redefine the product API contract.

---

## Architectural Role of Export

Export is a side workflow attached to a run.

Export must not arbitrarily mutate the primary reconciliation lifecycle unless the product model explicitly requires it.

This keeps:

- reconciliation lifecycle stable
- export behavior modular
- audit trails clear
- repeated export behavior deterministic

---

## Export Workflow Model

Minimum export workflow states:

- REQUESTED
- COMPLETED
- FAILED

Optional future states may include:

- GENERATING
- REGISTERED
- AVAILABLE

For EPIC 7, the minimal deterministic workflow is sufficient.

---

## Export Entry Point

Product-facing route:

POST /runs/{run_id}/export

The route must:

- validate contract input
- build ExportRunActionCommand
- call ActionExecutionService
- map ActionExecutionResult to contract-safe response

The route must not generate artifacts directly.

---

## Export Eligibility

A run may only be exported if it is in an export-eligible state.

Suggested eligible states:

- COMPLETED
- READY_FOR_EXPORT
- REVIEW_RESOLVED

Suggested ineligible states:

- CREATED
- RUNNING
- FAILED
- CANCELLED

The implementation must align final eligibility with the actual run lifecycle model already enforced by the system.

---

## Export Request Inputs

Minimum export request data should include:

- target run_id
- export format

Optional future inputs may include:

- export profile
- include_audit_data
- include_review_data

For EPIC 7, the minimum supported format should be enough to produce a real artifact.

---

## Minimum Supported Export Format

At minimum, the system must support:

- JSON

JSON is the safest first real export target because it preserves structure and is deterministic.

CSV may be added later, but JSON must be real and complete first.

---

## Export Workflow Steps

### Step 1 — Request Accepted

Export request is received and mapped to internal command.

System records:

- action type
- target run
- actor
- requested format
- correlation id

Export workflow state becomes:

REQUESTED

---

### Step 2 — Eligibility Validation

System validates:

- run exists
- run is export-eligible
- format is supported

If validation fails:

- no artifact is generated
- no hidden mutation occurs
- failure is surfaced explicitly

---

### Step 3 — Export Data Assembly

System loads the exportable product-facing data for the run.

This may include:

- run summary
- review outcome
- exportable action/result metadata

The assembled export payload must be based on stable product-facing or export-safe internal representations.

Raw internal persistence structures must not leak directly.

---

### Step 4 — Artifact Serialization

System serializes the assembled export payload into the requested format.

For EPIC 7:

- JSON serialization must produce a real file
- serialization must be deterministic for the same underlying data

---

### Step 5 — Artifact Write

System writes the artifact to deterministic local storage.

Minimum requirements:

- real file is created
- path is predictable
- name is deterministic
- write result is observable

---

### Step 6 — Export Registration

System records export result metadata such as:

- run_id
- export format
- artifact path or URI
- export status
- timestamp

This metadata must be available for response shaping and audit.

---

### Step 7 — Audit Logging

System writes audit data containing:

- export action type
- target run
- format
- export status
- artifact reference
- actor
- timestamp

---

### Step 8 — Completion

If all prior steps succeed:

REQUESTED → COMPLETED

If any required step fails after workflow start:

REQUESTED → FAILED

---

## Deterministic Artifact Rules

Export output must be deterministic.

For the same run and same format, the system should produce the same artifact reference unless an explicit regeneration policy is later introduced.

### Required deterministic properties

- stable filename convention
- stable extension
- stable directory convention
- stable serialization ordering where applicable

---

## Suggested Artifact Naming Convention

A simple deterministic convention is recommended.

Example:

run_{run_id}_export.{ext}

Examples:

- run_123_export.json
- run_123_export.csv

If format-specific variants or versioning are introduced later, they must remain explicit and deterministic.

---

## Suggested Storage Location

For EPIC 7, local filesystem storage is acceptable.

Suggested pattern:

exports/
or
data/exports/

The exact location should be defined in implementation and remain consistent.

The location must support:

- deterministic writes
- easy test verification
- easy audit reference recording

---

## Repeated Export Behavior

Repeated export requests must be deterministic.

### Recommended EPIC 7 behavior

If the same run is exported again in the same format and no regeneration policy exists:

- return existing artifact reference
or
- return deterministic already-exported result

Do not generate uncontrolled duplicate files for identical requests.

---

## Failure Model

### Validation Failure

Examples:

- missing run
- ineligible run state
- unsupported format

Effects:

- no artifact generation
- no hidden mutation
- stable failure result

### Serialization Failure

Effects:

- export marked FAILED
- failure is auditable
- no silent success response

### File Write Failure

Effects:

- export marked FAILED
- artifact reference is not falsely registered
- failure is auditable

### Registration Failure

Effects:

- failure must be visible
- no silent success
- partial execution must remain traceable

---

## Relationship to Main Run Lifecycle

Export should not, by default, mutate the main run lifecycle.

Export is a side workflow.

This means:

- a completed run remains completed after export
- export status is tracked separately
- artifact generation does not redefine reconciliation status

If future product requirements need explicit EXPORTED lifecycle semantics, that must be introduced intentionally and not assumed here.

---

## Audit Requirements

Every export attempt should be traceable.

Minimum audit data:

- action_type = EXPORT_RUN
- target_type = RUN
- target_id
- actor
- export_format
- before_export_state
- after_export_state
- artifact_reference if created
- execution_status
- timestamp

---

## Testability Requirements

The export workflow must be testable end-to-end.

Minimum test coverage should validate:

- eligible run can be exported
- ineligible run is rejected
- real artifact file is created
- artifact path is deterministic
- repeated export behaves predictably
- failed write or serialization produces auditable failure
- product response remains contract-safe

---

## Risks Prevented by This Document

This workflow design prevents:

- fake export placeholders
- route-level file generation
- uncontrolled duplicate artifacts
- export mutating unrelated run state
- hidden side effects
- non-auditable export failures

---

## Outcome

After this workflow is implemented:

- export_run becomes a real product workflow
- artifacts are real and deterministic
- export remains safely separated from the main run lifecycle
- repeated export behavior becomes predictable
- export side effects become explicit and auditable