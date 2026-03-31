# PRODUCT_CONTRACT_ENFORCEMENT.md

## EPIC 6 — Product Contract Enforcement

---

## 1. Purpose

The goal of this EPIC is to transform the Product Contract v1 into an enforced system boundary.

The contract defined in:

- docs/architecture/PRODUCT_CONTRACT_V1.md

is the single source of truth for all product-facing APIs.

This EPIC ensures:

- No API returns internal domain objects directly
- All responses conform strictly to product schemas
- All inputs are validated against product request models
- Contract drift between documentation and implementation is prevented
- Internal system details are never exposed unintentionally

---

## 2. Scope

### Included

- Product-level schema definitions (code-level)
- API boundary enforcement (request/response)
- Mapping layer between internal models and product models
- Contract validation tests for critical endpoints
- Prevention of internal field leakage

### Excluded

- Redesign of Product Contract v1
- Changes to domain models
- Business logic refactoring (matching, review, export)
- New product features

---

## 3. Source of Truth

The following document is authoritative:

- docs/architecture/PRODUCT_CONTRACT_V1.md

If implementation differs from the contract:

Implementation is wrong. Contract is correct.

---

## 4. Boundary Definition

### Product Boundary

The product boundary is defined at the API layer.

Everything exposed via API must conform to:

- Product schema definitions
- Contract rules
- Explicit mapping

### Internal Layer (NOT exposed)

- Domain models
- Persistence models
- Execution lifecycle metadata
- Learning system internals
- Debug / operational fields

---

## 5. Core Principles

### P1 — Explicit Product Models Only

All API responses MUST use product schema models.

Returning raw domain objects is forbidden.

---

### P2 — No Direct Serialization

This is NOT allowed:

return run
return run.model_dump()

All responses must go through mapping.

---

### P3 — Explicit Mapping Layer

Every response must pass through:

- internal to product mapper

Every action must pass through:

- product request to internal command mapper

---

### P4 — Allowlist Strategy

Product schemas define what is allowed.

Anything not explicitly defined is forbidden.

---

### P5 — Contract Tests Are Mandatory

Each product-facing endpoint must be covered by:

- Response shape validation
- Field presence validation
- Field absence validation

---

## 6. Product Schema Inventory

### 6.1 Run

- ProductRunSummary
- ProductRunDetail

### 6.2 Match Result

- ProductMatchResult
- ProductMatchExplanation

### 6.3 Review

- ProductReviewCase
- ProductReviewQueueItem

### 6.4 User Actions

- ProductActionRequest
- ProductActionResponse

### 6.5 Export

- ProductExportModel

---

## 7. Mapping Layer

A dedicated mapping layer MUST exist at:

- src/invomatch/api/mappers/

### Responsibilities

- Convert domain to product models
- Convert product requests to internal commands
- Enforce field allowlists
- Strip all internal-only data

### Rules

- Mapping must be explicit
- No generic dumping
- No hidden passthrough fields

---

## 8. Endpoint Contract Enforcement

### 8.1 GET /runs

Returns:

- List of ProductRunSummary

Forbidden:

- execution metadata
- lease info
- retry counters
- internal IDs not in contract

### 8.2 GET /runs/{id}

Returns:

- ProductRunDetail

Must include only contract-defined fields.

### 8.3 GET /runs/{id}/review

Returns:

- ProductReviewCase

Forbidden:

- raw feedback events
- learning signals
- internal scoring artifacts

### 8.4 POST /runs/{id}/actions

Accepts:

- ProductActionRequest

Returns:

- ProductActionResponse

Must NOT expose:

- internal command structures
- execution internals

### 8.5 GET /runs/{id}/export

Returns:

- ProductExportModel

Forbidden:

- storage backend info
- internal export job states

---

## 9. Field Leakage Prevention

### Strategy

- Strict product schema usage
- Explicit mapping layer
- Negative tests for forbidden fields

### Examples of forbidden fields

- internal_status
- retry_count
- lease_owner
- version
- debug_info

---

## 10. Validation Strategy

Each endpoint must be tested for:

### 10.1 Shape Validation

- Response matches expected schema

### 10.2 Field Presence

- Required fields exist

### 10.3 Field Absence

- Internal fields are NOT present

### 10.4 Input Validation

- Invalid action requests are rejected

---

## 11. Implementation Phases

### Phase 1 — Architecture (this document)

- Define boundary rules
- Define schema inventory
- Define enforcement strategy

### Phase 2 — Product Schemas

- Implement product models
- No route changes yet

### Phase 3 — Mapping Layer

- Implement explicit mapping functions

### Phase 4 — Contract Tests (FIRST)

- Write failing tests for endpoints
- Validate shape and leakage

### Phase 5 — Route Enforcement

- Refactor API routes to use:
  - product models
  - mapping layer

### Phase 6 — Hardening

- Add negative tests
- Remove all direct serialization
- Enforce response models

---

## 12. Exit Criteria

EPIC 6 is complete ONLY IF:

- Product schemas are defined and used
- Mapping layer is implemented
- All target endpoints are contract-tested
- No endpoint returns domain objects directly
- Internal fields cannot leak through API
- Contract v1 and API behavior are aligned
- Tests fail if contract is violated

---

## 13. Risks

### R1 — Fake Enforcement

Renaming models without removing direct domain serialization.

### R2 — Hidden Leakage

Optional or extra fields leaking through loosely controlled serialization.

### R3 — Mapper Complexity Explosion

Too many fragmented mappers without structure.

### R4 — Contract Ambiguity

Unclear fields in Product Contract v1.

Must NOT trigger redesign in this EPIC.

---

## 14. Final Rule

If an API response is not defined in Product Contract v1, it must NOT exist in the system.