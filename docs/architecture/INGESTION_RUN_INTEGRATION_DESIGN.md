# Ingestion → Run Integration Design (EPIC 17)

## 1. Purpose

This document defines the executable design for connecting ingestion outputs to reconciliation run creation.

It specifies:
- service contracts
- mapping contracts
- run creation decision model
- idempotency behavior
- traceability structure

This document must be directly translatable into implementation.

---

## 2. Core Service

### IngestionRunIntegrationService

Responsible for:

- executing ingestion flow
- evaluating run creation policy
- applying idempotency rules
- mapping ingestion outputs to run inputs
- creating or reusing runs
- attaching traceability metadata

### Method (conceptual)

create_run_from_ingestion(request) -> IngestionRunResult

---

## 3. Result Model

### IngestionRunResult

Possible outcomes:

- RUN_CREATED
- RUN_REUSED
- RUN_REJECTED
- RUN_FAILED

Fields:

- status
- run_id (nullable)
- reason_code
- ingestion_batch_id
- accepted_invoice_count
- accepted_payment_count
- rejected_count
- conflict_count

---

## 4. Mapper Contract

### IngestionToRunMapper

Input:
- accepted normalized invoices
- accepted normalized payments

Output:
- run input model (internal)

Rules:

- deterministic field mapping
- no raw payload usage
- no hidden transformation
- preserve identity references

---

## 5. Run Creation Policy

### Decision Rules

1. If ingestion failed → RUN_FAILED
2. If accepted invoices == 0 → RUN_REJECTED
3. If accepted payments == 0 → RUN_REJECTED
4. If blocking conflict exists → RUN_REJECTED
5. Otherwise → eligible for creation

### Partial Handling

Allowed if:
- both sides have at least 1 accepted record

Must attach:
- partial_ingestion flag

---

## 6. Idempotency Policy

### Based on:

- ingestion_batch_id
- normalized accepted dataset fingerprint

### Rules:

- same batch + same result → RUN_REUSED
- same batch + different result → RUN_FAILED (conflict)
- new batch → new run

---

## 7. Traceability Model

Each run must include:

- ingestion_batch_id
- ingestion_result_reference
- accepted/rejected/conflict counts
- idempotency_decision
- creation_policy_result

Traceability must be queryable from run.

---

## 8. Failure Handling

- ingestion failure → no run
- mapping failure → no run
- creation failure → no partial state leak
- retry must be idempotent

---

## 9. Boundary Enforcement

- no raw input allowed into run creation
- ingestion is mandatory entry point
- all external data must pass ingestion contracts

---

## 10. Implementation Notes

This design must be implemented before exposing public API endpoints.

No shortcuts are allowed at the boundary.