# RUN_FINALIZATION_POLICY

Status: PROPOSED

---

## 1. Purpose

Define the deterministic policy that governs run progression after matching has completed.

This policy controls:

- whether a run may finalize directly after matching
- whether a run must enter review_required
- when review cases must be created
- when a run may transition from review_required to completed
- when export becomes valid

This policy is authoritative for post-matching orchestration.

---

## 2. Canonical Run States

The canonical run states remain:

- queued
- processing
- review_required
- completed
- failed
- cancelled

This policy only governs legal transitions after matching execution has produced reconciliation results.

---

## 3. Policy Objectives

The system must guarantee:

- no run completes while unresolved review work still exists
- no run enters review_required without explicit review-worthy conditions
- no export is allowed before valid run finalization
- finalization is deterministic and auditable
- product-facing status remains aligned with Product Contract v1

---

## 4. Review Model

For EPIC 13, review orchestration is defined at the invoice-level.

The review unit is a Review Case associated with a single source invoice context.

A review case may include:
- the invoice reference
- candidate match information
- explanations
- confidence information
- issue taxonomy
- required user decision

Run progression is governed by review case status, not by raw candidate match count.

---

## 5. Post-Matching Decision Policy

After matching completes, the system must evaluate the reconciliation outcome for each invoice scope.

The run may finalize directly only if all invoice scopes are finalizable without human review.

The run must enter review_required if one or more invoice scopes are classified as requiring review.

The decision is binary at run level:

- if zero review cases are required → run may proceed to finalization evaluation
- if one or more review cases are required → run must transition to review_required

There is no partial review state.

---

## 6. Conditions That Require Review

A review case must be created when at least one of the following conditions exists for an invoice scope:

- no acceptable match candidate exists
- multiple competing match candidates remain unresolved
- reconciliation confidence is below the policy threshold
- rule evaluation produces a conflict that cannot be auto-resolved
- critical reconciliation fields are missing or inconsistent
- a policy rule explicitly forces manual review
- a prior correction-learning rule marks the case as review-required
- match outcome is explainable but not finalizable

These conditions must be derived from explicit system rules, not ad hoc heuristics in route or UI layers.

---

## 7. Conditions That Allow Direct Finalization

An invoice scope may be considered finalizable without review only when all of the following are true:

- exactly one acceptable reconciliation outcome exists
- no unresolved rule conflict exists
- required reconciliation fields are present
- confidence satisfies finalization policy
- no explicit manual-review rule applies
- the result is stable enough to be represented in product-facing output

If all invoice scopes satisfy these conditions, the run may proceed directly to finalization.

---

## 8. Review Case Creation Rules

Review case creation must be deterministic and idempotent.

The system must guarantee:

- the same post-matching result does not create duplicate review cases
- each review-required invoice scope maps to exactly one active review case
- review case identity is stable for orchestration and audit purposes

A review case is created only from policy-evaluated review-required outcomes.

The system must not create review cases for already finalizable invoice scopes.

---

## 9. Behavior While Run Is In review_required

A run in review_required is considered non-final and non-exportable.

While in review_required:

- unresolved review cases may exist
- completed export must not be produced
- run completion must not be reported
- product read models must show review summary consistent with active review cases

The run remains in review_required until finalization eligibility is re-evaluated and all blocking review work is resolved.

---

## 10. Review Resolution and Run Progression

Resolving a single review case does not by itself complete the run.

After every review resolution action, the system must re-evaluate run finalization eligibility.

The run may transition from review_required to completed only when:

- no active review case remains unresolved
- all review decisions have been applied
- no reopened or newly-created blocking review case exists
- the resulting reconciliation set is internally consistent
- export-readiness criteria are satisfied or can be satisfied immediately after completion

If any blocking review case remains unresolved, the run must stay in review_required.

---

## 11. Deferred / Reopened / Non-Terminal Review Outcomes

Review outcomes that do not produce a final applied decision must keep the run blocked from completion.

Examples include:

- deferred review decisions
- reopened review cases
- incomplete modification flows
- unresolved conflicts after user action

These outcomes are non-terminal at orchestration level and must prevent run completion.

---

## 12. Finalization Rules

Run finalization is valid only when all of the following are true:

- matching execution has completed
- review case generation has completed
- zero blocking review cases remain
- reconciliation output is stable
- final product-facing summaries can be derived consistently
- no terminal failure or cancellation condition overrides completion

Finalization must be a deliberate orchestration step, not an incidental side effect.

---

## 13. Export Readiness Rules

A run becomes export-ready only after valid finalization.

Export readiness requires:

- run status = completed
- finalized reconciliation output exists
- no active blocking review case exists
- export payload can be generated from stable finalized data
- artifact references, if produced, point to finalized output only

Export must never be allowed from:
- processing
- review_required
- failed
- cancelled

---

## 14. Product Contract and Read Model Consistency

All orchestration outcomes must preserve Product Contract v1 consistency.

At minimum, the following must remain aligned:

- run.status
- match_summary
- review_summary
- export_summary

The read model must not expose internal orchestration ambiguity.

If review work is active, the product-facing run must reflect review_required and corresponding review summary data.

If finalization is complete, the product-facing run must reflect completed and export readiness consistently.

---

## 15. Required Service Responsibilities

Implementation must introduce explicit orchestration responsibilities, including:

- evaluation of review requirement after matching
- creation of review cases from policy-qualified results
- re-evaluation of run completion after review resolution
- enforcement of export-readiness gating
- deterministic update of product-facing state

These responsibilities must not be scattered across route handlers.

---

## 16. Required Test Coverage

The implementation must be validated through:

- review trigger policy tests
- review case idempotency tests
- run finalization eligibility tests
- review resolution progression tests
- export readiness gating tests
- contract/read-model consistency tests
- end-to-end orchestration flow tests

---

## 17. Closure Criteria

This policy is considered implemented only when:

- runs requiring manual review always enter review_required
- runs with no blocking review conditions may complete deterministically
- no run completes with unresolved blocking review work
- no export is possible before valid completion
- orchestration behavior is covered by deterministic tests
- product-facing representations remain consistent across all legal transitions