# REVIEW_ITEM_GENERATION_POLICY

Status: PROPOSED

---

## 1. Purpose

Define the deterministic rules for generating review cases from reconciliation outcomes.

This policy ensures that review case creation is:

- explicit
- deterministic
- idempotent
- auditable
- aligned with run orchestration and finalization policy

This document complements RUN_FINALIZATION_POLICY.md.

---

## 2. Review Unit

For EPIC 13, the review unit is invoice-level.

Each review case represents one invoice scope that cannot be safely finalized without human resolution.

A review case is not defined per raw candidate match row.
A review case is defined per invoice reconciliation decision boundary.

This keeps orchestration stable and prevents review explosion.

---

## 3. Input Sources

Review case generation consumes policy-evaluated reconciliation outcomes produced after matching completes.

These outcomes may include:

- selected candidate match
- alternative candidate matches
- confidence signals
- rule evaluation output
- mismatch taxonomy
- missing-field signals
- conflict markers
- forced-review markers
- explanation payloads

Generation must operate on normalized reconciliation output, not directly on route-layer data.

---

## 4. Generation Principle

A review case must be created only when an invoice scope is classified as review-required by policy.

The system must not generate review cases for invoice scopes that are already finalizable.

Generation is a policy-controlled transformation:

reconciliation outcome
    → review-required classification
    → review case creation

No ad hoc case creation is allowed outside this path.

---

## 5. Review-Required Outcome Types

A review case must be generated for invoice scopes with outcomes such as:

- unmatched
- ambiguous_match
- low_confidence_match
- conflicting_rules
- missing_required_fields
- forced_manual_review
- correction-policy escalation
- explainable_but_not_finalizable

These categories may evolve, but the orchestration rule remains the same:
if the invoice scope cannot be finalized safely, it must produce a review case.

---

## 6. Non-Review Outcome Types

A review case must not be generated for invoice scopes that are already safe for direct finalization.

Examples include:

- single acceptable match with no blocking conflict
- policy-approved auto-match
- finalized no-issue reconciliation outcome
- previously resolved and already-applied stable outcome

Informational warnings alone must not create review cases unless policy explicitly upgrades them into blocking review conditions.

---

## 7. Review Case Content Requirements

Each generated review case must include enough information for deterministic review handling.

At minimum, a review case should carry or reference:

- run_id
- invoice identifier / invoice scope key
- review reason category
- reconciliation summary
- candidate match context where applicable
- confidence context where applicable
- explanation context
- blocking status
- creation timestamp / audit metadata

The case must be representable in product-facing review views without leaking internal-only implementation detail.

---

## 8. Identity and Idempotency Rules

Review case creation must be idempotent.

The system must guarantee:

- one active review case per review-required invoice scope
- no duplicate active review cases for the same policy-equivalent invoice scope
- stable identity for the same unresolved review problem

Review case identity should be derived from stable orchestration keys, not transient UI state.

At minimum, identity must be anchored by:
- run_id
- invoice scope identifier
- active review problem boundary

If the same unresolved condition is evaluated multiple times, the system must reuse or preserve the existing active review case instead of creating duplicates.

---

## 9. Regeneration Rules

Re-evaluation of a run may occur multiple times.

During re-evaluation:

- unchanged unresolved review conditions must not create new duplicate cases
- newly discovered review-required invoice scopes must create new cases
- resolved-and-applied cases may remain in audit history but must not remain active blockers
- reopened cases may become active again according to review workflow policy

Case generation must therefore distinguish between:
- active blocking cases
- resolved historical cases
- newly emerged blocking cases

---

## 10. Blocking vs Non-Blocking Review Cases

For EPIC 13, generated review cases are assumed to be blocking by default unless an explicit policy later defines a non-blocking category.

This keeps run orchestration strict and predictable.

A blocking review case prevents run completion until:
- a valid review decision is made
- the decision is applied
- the invoice scope becomes finalizable

If future product policy introduces informational/non-blocking review items, that must be explicitly modeled and must not silently weaken finalization rules.

---

## 11. Relationship to Run Status

Review case generation directly affects run progression.

- zero generated blocking review cases → run may proceed to finalization evaluation
- one or more generated blocking review cases → run must enter review_required

Therefore, review generation is not just a review concern.
It is a run-state orchestration concern.

---

## 12. Product and API Consistency

Generated review cases must support consistent product-facing summaries, including:

- review counts
- blocking/unresolved state
- review status visibility
- linkage to run lifecycle state

The API/read-model layer must be able to derive stable review summaries from generated review cases.

No hidden or route-only review logic is allowed.

---

## 13. Required Implementation Responsibilities

Implementation must provide explicit components for:

- classification of reconciliation outcomes into review-required vs finalizable
- deterministic review case construction
- case identity enforcement / idempotency control
- regeneration handling during re-evaluation
- mapping to product-facing review summaries

These responsibilities must live in service/domain orchestration layers, not in UI or endpoint glue code.

---

## 14. Required Test Coverage

The implementation must be validated through tests covering:

- generation of review cases for each blocking outcome type
- absence of review case generation for finalizable outcomes
- idempotent generation on repeated evaluation
- correct case identity behavior
- regeneration behavior after partial and full resolution
- run-state consequences of generated review cases
- consistency of derived review summaries

---

## 15. Closure Criteria

This policy is considered implemented only when:

- every blocking reconciliation outcome deterministically generates a review case
- finalizable outcomes do not generate unnecessary review cases
- repeated evaluation does not create duplicate active cases
- generated review cases support run-state gating correctly
- review summaries remain consistent with active case state