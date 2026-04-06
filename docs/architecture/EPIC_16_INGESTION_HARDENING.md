# EPIC 16 — Ingestion Boundary / Input Contract Hardening

## 1. Purpose

This EPIC hardens the ingestion boundary of InvoMatch as a deterministic, contract-driven input layer.

The goal is to ensure that external business inputs enter the system in a form that is:

- explicitly structured
- validated against canonical contracts
- deterministically normalized
- traceable from raw input to normalized entity
- safe for downstream matching, review, and export flows

This is not an integrations EPIC.
It is a boundary-hardening EPIC.

---

## 2. Problem Statement

Execution lifecycle, orchestration, review resolution, export delivery, product read models, and product flow enforcement are now deterministic and contract-bound.

However, downstream correctness depends on upstream trust.

If ingestion is ambiguous, inconsistent, or partially heuristic, then:

- matching becomes non-deterministic
- review semantics become unstable
- export correctness becomes accidental
- auditability breaks
- product reliability becomes untrustworthy

The ingestion layer must therefore act as a strict system boundary, not a loose parsing utility.

---

## 3. Scope

This EPIC covers the internal ingestion boundary for external business inputs.

Included:

- canonical input contracts for invoice and payment ingestion
- deterministic parsing and normalization rules
- validation and rejection policy
- ingestion determinism and idempotency rules
- traceability and auditability model
- downstream safety guarantees
- implementation plan
- test strategy

Not included:

- ERP integrations
- bank integrations
- OCR extraction quality improvements
- UI upload workflows
- ML-based parsing or enrichment
- deployment or infrastructure changes

---

## 4. Architectural Principles

### 4.1 Boundary First

The ingestion layer is a trust boundary.
Raw input must not flow directly into downstream business logic.

### 4.2 Contract Driven

All accepted input types must have explicit canonical schemas and validation rules.

### 4.3 Deterministic Normalization

The same input must always produce the same normalized output.

### 4.4 Explicit Rejection

Invalid or ambiguous input must be rejected or flagged according to explicit rules.
No silent coercion is allowed.

### 4.5 Auditability by Design

Every ingestion decision must be traceable from raw input to normalized outcome.

### 4.6 Downstream Safety

Matching, review, export, and product read models must only consume trusted normalized entities.

---

## 5. Boundary Model

The ingestion boundary will be designed around four distinct model layers:

1. Raw Input Model
2. Validation Result
3. Normalized Input Model
4. Ingestion Decision / Audit Record

These layers must remain explicit and separated.

### 5.1 Raw Input Model

Represents incoming external data exactly as received, before trust is established.

### 5.2 Validation Result

Captures structural and semantic validation outcome, including errors and warnings.

### 5.3 Normalized Input Model

Represents canonical, trusted internal input shape used by downstream flows.

### 5.4 Ingestion Decision / Audit Record

Captures the final ingestion decision, normalization context, rejection reasons, warning flags, and traceability metadata.

---

## 6. Canonical Input Contracts

This EPIC defines explicit canonical contracts for:

- Invoice input
- Payment input
- Optional ingestion metadata

### 6.1 Invoice Input Contract

The invoice input contract must define:

- required fields
- optional fields
- field types
- field constraints
- normalization expectations
- rejection conditions

Candidate invoice field categories include:

- external identifiers
- invoice number
- issue date
- due date
- currency
- gross amount
- net amount
- tax amount
- counterparty references
- source metadata

### 6.2 Payment Input Contract

The payment input contract must define:

- required fields
- optional fields
- field types
- field constraints
- normalization expectations
- rejection conditions

Candidate payment field categories include:

- external identifiers
- payment reference
- payment date
- amount
- currency
- payer/payee references
- source metadata

### 6.3 Ingestion Metadata Contract

Optional ingestion metadata may include:

- source system
- source file identifier
- import batch identifier
- received timestamp
- contract version
- rule version

Metadata must not replace core business fields.
It only supports traceability and operational safety.

---

## 7. Parsing and Normalization Rules

All accepted transformations must be rule-based, explicit, deterministic, and testable.

No hidden heuristics.
No silent fallback behavior.
No runtime-dependent interpretation.

### 7.1 Date Normalization

Rules must define:

- accepted input formats
- canonical output representation
- timezone handling policy
- invalid date rejection behavior
- null and empty value semantics

### 7.2 Amount Normalization

Rules must define:

- accepted numeric formats
- decimal normalization
- sign handling
- rounding policy
- invalid amount rejection behavior

### 7.3 Currency Normalization

Rules must define:

- accepted currency representations
- canonical currency format
- missing currency behavior
- invalid currency rejection or flagging rules

### 7.4 Identifier Normalization

Rules must define:

- invoice number cleanup
- payment reference cleanup
- whitespace handling
- separator normalization
- casing policy
- unsupported character handling

### 7.5 String Normalization

Rules must define:

- trimming policy
- empty-string handling
- casing normalization where applicable
- Unicode cleanup policy
- encoding anomaly behavior

### 7.6 Missing / Null / Empty Semantics

Rules must explicitly distinguish between:

- missing field
- null field
- empty string
- invalid value

These must not be treated as interchangeable.

---

## 8. Validation and Rejection Policy

Validation must be deterministic and explicit.

The system must distinguish between:

- hard rejection
- soft acceptance with warnings or flags
- accepted clean input

### 8.1 Hard Rejection

Hard rejection applies when the input is structurally invalid or semantically unsafe for downstream use.

Examples include:

- missing required fields
- invalid type shape
- invalid amount format
- invalid date format
- irreconcilable currency state

### 8.2 Soft Acceptance with Flags

Soft acceptance applies when the input is ingestible but incomplete or operationally risky.

Examples include:

- optional reference missing
- source metadata absent
- non-critical identifier cleanup applied

### 8.3 Accepted Clean Input

Accepted clean input has passed required validation and normalization without material warnings.

### 8.4 Partial Ingestion

Partial ingestion is only allowed if explicitly defined.
If allowed, the exact rules, safety limits, and downstream guarantees must be documented and tested.

---

## 9. Ingestion Determinism and Idempotency

The ingestion layer must be deterministic and replay-safe.

### 9.1 Determinism

The same raw input must always produce the same:

- validation result
- normalized output
- ingestion decision

No hidden mutable state may influence results.

### 9.2 Idempotency

Repeated ingestion of the same logical item must be handled safely.

Idempotency rules must define the difference between:

- exact replay
- source-level duplicate
- semantic duplicate
- conflicting duplicate

### 9.3 Duplicate Handling

Duplicate handling must be explicit and test-covered.

Possible strategies may include:

- source idempotency key
- normalized content fingerprint
- conflict classification rules

No implicit duplicate handling is allowed.

---

## 10. Traceability and Auditability

Every ingested item must preserve the relationship between:

- raw source input
- validation result
- normalization decisions
- normalized entity
- final ingestion decision
- rejection reason or warning flags

The system must support debugging and correction without guesswork.

The audit model should capture at least:

- raw payload snapshot or reference
- schema version
- normalization rule version
- validation errors
- warning flags
- normalized entity reference
- idempotency outcome
- timestamp

---

## 11. Downstream Safety Guarantees

The ingestion boundary must guarantee that downstream layers never receive undefined or malformed entities.

This applies to:

- matching
- review generation
- export generation
- product read models

Downstream components must consume trusted normalized entities, not ambiguous raw payloads.

No downstream component should need to guess input meaning.

---

## 12. Proposed Internal Design Direction

Implementation should follow explicit separation of concerns.

### 12.1 Contract Models

Define canonical raw input contracts and canonical normalized input models.

### 12.2 Normalization Layer

Implement pure normalization components for:

- dates
- amounts
- currency
- identifiers
- strings
- null / empty semantics

### 12.3 Validation Layer

Implement structural and semantic validation with explicit error and warning outputs.

### 12.4 Decision Layer

Implement final ingestion decision logic:

- reject
- accept_with_flags
- accept_clean

### 12.5 Traceability Layer

Implement raw-to-normalized linkage and ingestion audit recording.

### 12.6 Downstream Boundary Enforcement

Ensure downstream services only receive normalized trusted entities.

---

## 13. Implementation Plan

### Phase A — Contract and Model Definition

- define invoice input contract
- define payment input contract
- define ingestion metadata contract
- define normalized invoice model
- define normalized payment model
- define validation result model
- define ingestion decision / audit model

### Phase B — Normalization Engine

- implement date normalization
- implement amount normalization
- implement currency normalization
- implement identifier normalization
- implement string normalization
- implement missing/null/empty handling rules

### Phase C — Validation and Rejection

- structural validation
- semantic validation
- hard rejection policy
- warning/flagging policy
- accepted-clean decision criteria

### Phase D — Idempotency and Traceability

- define idempotency key strategy
- define duplicate classification rules
- define raw-to-normalized traceability rules
- define audit persistence contract

### Phase E — Downstream Integration

- enforce normalized input boundary for matching
- enforce normalized input boundary for review
- enforce normalized input boundary for export
- verify compatibility with product read models

---

## 14. Test Strategy

This EPIC requires multiple layers of testing.

### 14.1 Contract Tests

Verify accepted and rejected shapes for invoice, payment, and metadata contracts.

### 14.2 Normalization Tests

Verify deterministic normalization for dates, amounts, identifiers, strings, and null semantics.

### 14.3 Failure Path Tests

Verify deterministic behavior for malformed:

- dates
- amounts
- currency values
- identifiers
- required field absence
- invalid structural shapes

### 14.4 Idempotency and Duplicate Tests

Verify behavior for:

- exact replay
- source duplicate
- semantic duplicate
- conflicting duplicate

### 14.5 Downstream Safety Tests

Verify that downstream flows never consume malformed or undefined input structures.

### 14.6 Auditability Tests

Verify that raw input, validation, normalization, and decision records remain traceable and explainable.

---

## 15. Closure Criteria

EPIC 16 is complete only when:

- all supported input types have explicit canonical schemas
- ingestion rules are deterministic and testable
- invalid inputs are rejected or flagged according to explicit policy
- normalization behavior is stable and reproducible
- duplicate and idempotent ingestion behavior is defined and verified
- every accepted or rejected input is traceable to raw source data
- downstream layers operate only on trusted normalized entities
- ingestion is covered by unit, integration, and failure-path tests

---

## 16. Core Principle

If input is not trusted, the system is not trusted.