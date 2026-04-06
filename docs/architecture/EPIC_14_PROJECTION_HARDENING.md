# EPIC 14 — Projection / Product Read Model Hardening

## 1. Problem Statement

The execution layer is correct and stable after EPIC 13.
However, the product-facing read layer (projections) may still produce:

- stale data
- partially aggregated summaries
- inconsistent state representations
- drift between source-of-truth and API responses

This EPIC ensures that all product-facing read models are deterministic, consistent, and contract-compliant.

---

## 2. Product Read Surface

The following product models are in scope:

- ProductRunView
- ProductRunMatchSummary
- ProductRunReviewSummary
- ProductRunExportSummary
- Export API response models

Primary API:

- GET /api/reconciliation/runs/{run_id}/view
- GET /api/reconciliation/runs/{run_id}/export

---

## 3. Source of Truth Mapping

### Run Status
Source:
- RunStore (persisted lifecycle state)

### Match Summary
Source:
- persisted match results within run

### Review Summary
Source:
- ReviewStore (review items)

Must:
- reflect real-time review state
- distinguish terminal vs non-terminal states

### Export Summary
Source:
- Export artifact repository
- export lifecycle state

Must:
- not report ready unless gating is satisfied
- reflect actual artifact existence

---

## 4. Projection Invariants

The following must ALWAYS hold:

1. No stale summaries:
   - summaries must reflect current persisted state

2. Review consistency:
   - unresolved review items => cannot present finalized state

3. Export correctness:
   - export cannot be "ready" without satisfying gating conditions
   - export cannot be "available" without artifact

4. No implicit state:
   - projections must be reconstructable from source of truth

5. No contradictory fields:
   - no combination of fields may violate lifecycle rules

---

## 5. Failure Scenario Matrix

We must handle:

- partial updates (run updated, review not yet reflected)
- concurrent updates (review resolution during read)
- stale reads (race between persistence and projection)
- crash during export creation
- artifact exists but projection not aligned
- projection during state transition

---

## 6. Projection Construction Strategy

Rules:

- projections must be built from source-of-truth on demand
- no hidden caching that introduces inconsistency
- aggregation must be deterministic
- all summaries must be recomputable

Single authoritative path:
- RunViewQueryService (or equivalent canonical service)

---

## 7. Contract Enforcement

All read models must:

- strictly follow Product Contract v1
- not expose internal domain models
- not leak internal enums or fields
- maintain stable response shape

---

## 8. Implementation Plan

1. Introduce canonical projection assembly layer
2. Centralize summary builders:
   - match summary
   - review summary
   - export summary
3. Add projection validation guards
4. Enforce export readiness rules
5. Ensure no read-side mutation
6. Align all API mappers with contract

---

## 9. Test Strategy

### Unit Tests
- summary aggregation correctness
- invariant validation

### Integration Tests
- run view endpoint correctness
- export endpoint correctness

### Contract Tests
- no internal leakage
- response shape stability

### Concurrency Tests
- read during review resolution
- read during export creation

### End-to-End Tests
- full lifecycle projection validation

---

## 10. Closure Checklist

EPIC is complete only if:

- all projections are consistent with source-of-truth
- no stale or contradictory API data is observable
- concurrency does not break projection correctness
- Product Contract v1 is enforced at read layer
- end-to-end tests validate projection integrity
