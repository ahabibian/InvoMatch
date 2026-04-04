# EPIC 13 — Implementation Plan

Status: PROPOSED

Related Documents:
- EPIC_13_REVIEW_ORCHESTRATION.md
- RUN_FINALIZATION_POLICY.md
- REVIEW_ITEM_GENERATION_POLICY.md

---

## 1. Implementation Objective

Implement the orchestration layer that governs run progression after matching completes and after review decisions are resolved.

The implementation must turn policy into enforceable system behavior.

This includes:

- review requirement evaluation
- review case generation
- run progression gating
- run finalization eligibility evaluation
- export-readiness enforcement
- product/read-model consistency

---

## 2. Architectural Intent

EPIC 13 must be implemented as explicit orchestration logic, not as scattered conditional behavior across endpoints or unrelated services.

The orchestration flow must remain:

matching result
    → review requirement evaluation
    → review case generation if needed
    → run state update
    → finalization evaluation when eligible
    → export readiness only after valid completion

Review resolution must also re-enter this orchestration path.

---

## 3. Required New Responsibilities

The system must introduce explicit responsibilities for:

- classifying reconciliation outcomes into finalizable vs review-required
- generating invoice-level review cases from blocking outcomes
- enforcing idempotent review case creation
- evaluating run completion eligibility after review actions
- preventing completion while blocking review work exists
- enforcing export readiness only from finalized output

These responsibilities must be concentrated in orchestration-aware services.

---

## 4. Proposed Components

### 4.1 ReviewRequirementEvaluator
Responsible for evaluating reconciliation outcomes and deciding whether each invoice scope is:
- finalizable
- review-required

Expected responsibilities:
- apply explicit review-trigger rules
- expose deterministic classification output
- avoid route-level heuristics

### 4.2 ReviewCaseFactory
Responsible for building review cases from review-required reconciliation outcomes.

Expected responsibilities:
- construct invoice-level review cases
- map review reason categories
- attach explanation / confidence / candidate context
- support deterministic case identity inputs

### 4.3 ReviewCaseGenerationService
Responsible for idempotent creation/upsert behavior for active review cases.

Expected responsibilities:
- ensure one active blocking review case per invoice scope
- avoid duplicate active case creation
- preserve historical/audit-safe behavior

### 4.4 RunFinalizationEvaluator
Responsible for deciding whether a run may transition to completed.

Expected responsibilities:
- inspect active review state
- confirm zero blocking unresolved review cases
- confirm reconciliation output stability
- confirm completion eligibility before export

### 4.5 RunOrchestrationService
Primary orchestration entry point for EPIC 13.

Expected responsibilities:
- orchestrate post-matching progression
- orchestrate post-review-resolution progression
- choose between review_required and completed
- trigger finalization evaluation
- coordinate export-readiness state

---

## 5. Expected Integration Points

Implementation is expected to integrate with existing areas such as:

- matching result output/services
- review service / review store
- action execution flow
- run persistence / run lifecycle state machine
- product run view / projection layer
- export workflow / export summary logic

EPIC 13 must reuse existing lifecycle and review capabilities rather than bypassing them.

---

## 6. Suggested File / Module Impact

The exact filenames may be adjusted to match the current repository structure, but the following kinds of changes are expected.

### 6.1 New or Extended Service Modules
Potential additions under service orchestration areas such as:

- src/invomatch/services/orchestration/review_requirement_evaluator.py
- src/invomatch/services/orchestration/review_case_factory.py
- src/invomatch/services/orchestration/review_case_generation_service.py
- src/invomatch/services/orchestration/run_finalization_evaluator.py
- src/invomatch/services/orchestration/run_orchestration_service.py

### 6.2 Existing Services Likely To Change
Likely integration changes in modules such as:

- reconciliation completion / matching completion flow
- review resolution action handling
- review service integration points
- run state transition services
- export readiness / export run action integration
- unified run view query service or related product read models

### 6.3 Existing Models Potentially To Extend
Possible additions to support orchestration clarity:

- review reason classification fields
- blocking/non-blocking semantics
- reconciliation outcome classification shape
- run-level finalization markers if needed
- projection/read-model summary derivation support

---

## 7. Implementation Sequence

### Phase 1 — Classification and Finalization Evaluation
Implement:
- ReviewRequirementEvaluator
- RunFinalizationEvaluator

Purpose:
- define the decision boundary for review_required vs finalizable
- define completion eligibility deterministically

This phase should not yet depend on route-specific behavior.

### Phase 2 — Review Case Construction and Idempotent Generation
Implement:
- ReviewCaseFactory
- ReviewCaseGenerationService

Purpose:
- turn review-required outcomes into active invoice-level review cases
- guarantee deterministic/idempotent case creation

### Phase 3 — Run Orchestration Integration
Implement:
- RunOrchestrationService

Purpose:
- connect post-matching outputs to review/finalization flow
- connect review resolution outcomes back into run progression

### Phase 4 — Product Projection / Export Readiness Alignment
Integrate orchestration outcomes into:
- run view/read model
- review summary projection
- export summary readiness behavior

### Phase 5 — End-to-End Validation and Hardening
Validate:
- state transitions
- review gating correctness
- no premature completion
- export gating correctness
- read-model consistency

---

## 8. Test Strategy

### 8.1 Unit Tests
Add focused tests for:
- review requirement classification
- finalization eligibility evaluation
- review case factory mapping
- review case idempotent generation behavior

Example test modules:
- tests/test_review_requirement_evaluator.py
- tests/test_run_finalization_evaluator.py
- tests/test_review_case_factory.py
- tests/test_review_case_generation_service.py

### 8.2 Service / Integration Tests
Add orchestration flow tests for:
- post-match run goes directly to completed when no review is required
- post-match run enters review_required when blocking review cases exist
- repeated orchestration does not duplicate active review cases
- resolving one review case does not prematurely complete the run
- resolving all blocking review cases allows finalization
- deferred/reopened review keeps run blocked

Example test modules:
- tests/test_run_orchestration_service.py
- tests/test_review_to_completion_flow.py

### 8.3 Contract / Read-Model Tests
Validate:
- run.status consistency
- review_summary consistency
- export_summary consistency
- no exposure of ambiguous orchestration state

Example test modules:
- tests/test_run_view_orchestration_contract.py
- tests/test_export_readiness_gating.py

---

## 9. Non-Negotiable Invariants

The implementation must preserve these invariants:

- a run with blocking review work cannot complete
- a run cannot export finalized output before valid completion
- review case generation must be idempotent
- review orchestration must be deterministic for the same input state
- product-facing run views must reflect orchestration truth
- route handlers must not contain hidden orchestration policy

---

## 10. Risks To Avoid

The following implementation mistakes are explicitly disallowed:

- embedding review/finalization policy directly in API routes
- creating review cases from ad hoc UI logic
- allowing completion as a side effect of partial review actions
- allowing export from non-finalized run state
- mixing historical review records with active blocking review state
- weakening invoice-level review orchestration into ambiguous match-row behavior

---

## 11. Closure Criteria

EPIC 13 implementation is only complete when:

- ReviewRequirementEvaluator exists and is covered by deterministic tests
- ReviewCase generation is idempotent and invoice-level
- RunOrchestrationService governs post-match and post-review progression
- Run finalization is impossible while blocking review work exists
- Export readiness is enforced only after valid completion
- Product/read-model outputs remain consistent with orchestration truth
- full orchestration flow is validated by unit + integration + contract tests