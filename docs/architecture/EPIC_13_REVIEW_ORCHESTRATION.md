# EPIC 13 — Review Orchestration & Run Finalization

Status: PROPOSED

---

## 1. Purpose

Define deterministic orchestration for transitioning a run from matching completion into review and finalization.

This EPIC ensures:
- no ambiguous run states
- no premature completion
- strict review gating
- export only after valid finalization

---

## 2. Scope

This EPIC defines:

- Review Trigger Policy
- Review Item Generation
- Review Resolution → Run Progression
- Run Finalization Policy
- Export Readiness Rules
- Orchestration Service

---

## 3. Non-Goals

This EPIC does NOT define:
- UI behavior
- heuristic-based decision making
- manual workflows outside system control

---

## 4. System Context

Input:
- Match results (EPIC 3)
- Review system (EPIC 5)
- Action execution (EPIC 7)
- Run lifecycle (EPIC 1 & 12)

Output:
- deterministic run state transitions
- stable final run state
- export-ready artifact state

---

## 5. High-Level Flow

matching_completed
    → evaluate_review_requirement
        → (no review) → finalize_run
        → (review required) → create_review_items → review_required

review_resolution
    → evaluate_completion
        → (all resolved) → finalize_run
        → (pending items) → stay_in_review

---

## 6. Core Components (to be defined)

- ReviewTriggerEvaluator
- ReviewItemFactory
- RunFinalizationEvaluator
- RunOrchestrationService

---

## 7. Policies (detailed in separate docs)

- RUN_FINALIZATION_POLICY.md
- REVIEW_ITEM_GENERATION_POLICY.md

---

## 8. API / Product Contract Impact

Must remain aligned with Product Contract v1:

- run.status
- match_summary
- review_summary
- export_summary

No internal leakage allowed.

---

## 9. Test Strategy (to be expanded)

- policy validation tests
- orchestration flow tests
- contract enforcement tests

---

## 10. Open Questions

(to be resolved during implementation)

- review granularity (match vs invoice)
- partial resolution behavior
- re-open review semantics

---

## 11. Exit Criteria

- deterministic transitions enforced
- no run completes with pending review
- export blocked before finalization
- full test coverage for orchestration logic