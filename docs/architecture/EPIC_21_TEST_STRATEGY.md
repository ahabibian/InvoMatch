# EPIC 21 — Test Strategy and Closure Criteria

## Purpose
Define the minimum credible validation approach for the operator-facing UI
without overbuilding a frontend test platform.

---

## 1. Testing Objective

Verify that the UI behaves as a thin backend consumer and that the full
minimal product loop is human-usable and backend-aligned.

---

## 2. What Must Be Proven

The implementation must prove:

- input can be submitted through the UI
- run list reflects backend run data
- run detail reflects backend read models accurately
- review surface reflects backend review data
- actions are executed through backend enforcement
- invalid actions are rejected visibly
- export visibility matches backend truth
- UI does not invent or soften business state

---

## 3. Test Scope

### A. Smoke Validation
Purpose:
Confirm the UI loads and can reach backend APIs.

Examples:
- application boots
- upload page renders
- run list page renders
- run detail route renders

---

### B. API-to-UI Integration Validation
Purpose:
Confirm UI surfaces map correctly to backend contract fields.

Examples:
- run_id and status shown from upload response
- run list rows match GET /runs response
- run detail sections match run view / review / export responses
- action response shown without reinterpretation

---

### C. Action Flow Validation
Purpose:
Confirm controlled action execution works end-to-end.

Examples:
- operator triggers action
- backend accepts action
- UI refreshes run detail
- backend rejects invalid action
- UI shows rejection and preserves visible truth

---

### D. State and Error Validation
Purpose:
Confirm truthful state presentation.

Examples:
- queued shown as queued
- processing not shown as completed
- review_required exposes review surface
- failed shown clearly
- validation error shown clearly
- degraded secondary section shown without inventing data

---

### E. Manual Human Demo Validation
Purpose:
Confirm the full operator loop is actually usable.

Demo path:
1. submit input
2. confirm run created
3. inspect run in run list
4. open run detail
5. inspect review state
6. execute action if applicable
7. inspect refreshed state
8. inspect export readiness or export artifact

---

## 4. Explicit Non-Goals for Testing

Do not build during EPIC 21:

- full frontend unit-test matrix
- snapshot-heavy UI suite
- broad visual regression harness
- synthetic frontend business-rule tests that duplicate backend tests

The frontend test approach should remain narrow and evidence-driven.

---

## 5. Failure Conditions

EPIC 21 must not be considered complete if:

- UI bypasses backend contracts
- UI derives business state independently
- action rejection is hidden or softened
- export readiness is inferred by frontend
- run detail does not match backend read model
- the full loop cannot be demonstrated by a human operator

---

## 6. Closure Criteria

EPIC 21 is closed only if all of the following are true:

- input submission works through the UI
- run list works through the UI
- run detail works through the UI
- review visibility is present where applicable
- action execution is backend-enforced and visible
- invalid actions are handled predictably
- export visibility/access is represented truthfully
- the UI remains a thin client
- the full loop is demoable by a human operator

---

## 7. Evidence Expectations

Closure evidence should include:

- implementation references
- route / page coverage summary
- API-to-UI mapping confirmation
- smoke / integration validation evidence
- manual demo evidence summary
- statement that no frontend-side business rules were introduced

---

## 8. Key Principle

A minimal UI is only valid if it preserves product truth.

The goal is not visual completion.
The goal is controlled, accurate human usability.
