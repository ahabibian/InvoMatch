# EPIC Closure Standard (FINAL)

Each EPIC is considered complete only if all of the following are satisfied:

---

## 1. Architecture

- Architecture document exists (docs/architecture/...)
- Scope, invariants, and constraints are explicitly defined
- Alignment with Product Contract v1 is verified

---

## 2. Implementation

- All required services / models / APIs implemented
- No leakage of internal domain objects into product layer
- Deterministic behavior enforced (no hidden state)

---

## 3. Tests (Strict)

Must include:

- Unit tests (core logic)
- Contract tests (Product API boundary)
- Integration tests (end-to-end flow)
- Failure scenario tests (edge cases, partial state, degraded dependencies)

Without failure scenario coverage, the EPIC is considered incomplete.

---

## 4. Projection / State Correctness

- Read models are consistent with source of truth
- No stale, partial, or contradictory data observable
- Idempotency verified where applicable
- Reconstructability of projection is validated

---

## 5. Execution Evidence

Closure must include:

- Executed commands (pytest, etc.)
- Test results (passed count)
- Covered modules/files
- No failing or skipped critical tests

---

## 6. Closure Document

EPIC_X_CLOSURE.md must contain:

- Summary of what was implemented
- Key design decisions
- Test coverage explanation
- Validation results
- Known limitations (explicitly stated)

---

## 7. Final Validation

- End-to-end flow validated (run → review → resolve → export → view)
- API responses verified (via tests or manual validation)
- No Product Contract violations

---

## Final Rule

An EPIC is NOT considered complete unless all of the above conditions are satisfied.

This document defines the quality gate for all future EPIC closures.