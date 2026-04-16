# REVIEW TAXONOMY ALIGNMENT

## 1. Problem Statement

The current system uses inconsistent reconciliation outcome taxonomies across runtime and orchestration layers.

### Runtime reconciliation taxonomy
The runtime reconciliation flow currently produces these match result statuses:

- `matched`
- `unmatched`
- `partial_match`
- `duplicate_detected`

These statuses are emitted by the reconciliation engine and persisted into the reconciliation report.

### Orchestration review taxonomy
The orchestration layer currently interprets review-required outcomes using a different vocabulary:

- `unmatched`
- `ambiguous`
- `low_confidence`
- `conflict`
- `forced_review`

This creates a semantic mismatch between:

- persisted runtime reconciliation output
- review requirement evaluation
- review case generation
- downstream run state transitions

---

## 2. Evidence

System Scenario 5 captured a real limitation:

- JSON input path produced a completed run
- runtime report status for the invoice was `unmatched`
- orchestration logic, when given runtime-derived outcomes, interpreted that status as review-required

This proves that runtime completion policy and orchestration review policy are not aligned by a single canonical outcome contract.

---

## 3. Architectural Decision

The runtime reconciliation taxonomy is the source of truth for orchestration decisions in this flow.

The orchestration layer must align to the runtime-produced statuses instead of introducing an independent vocabulary for the same product flow.

### Canonical reconciliation outcome statuses for this flow

- `matched`
- `unmatched`
- `partial_match`
- `duplicate_detected`

### Review requirement rules

#### Review-required
- `unmatched`
- `partial_match`
- `duplicate_detected`

#### Non-review
- `matched`

---

## 4. Why Runtime Taxonomy Wins

This choice is intentional.

The runtime layer is the origin of:
- reconciliation outcomes
- persisted report data
- completion vs review_required lifecycle behavior
- export-readiness dependencies

Allowing orchestration to interpret a different taxonomy would create:
- contract drift
- inconsistent run states
- fragile scenario behavior
- duplicated business semantics

The orchestration layer should consume runtime semantics, not redefine them.

---

## 5. Implementation Direction

The following components must align to the canonical runtime taxonomy:

- `src/invomatch/services/orchestration/review_requirement_evaluator.py`
- `src/invomatch/services/orchestration/review_case_generation_service.py`
- `src/invomatch/services/orchestration/review_case_factory.py`

Preferred approach:
- define one shared review-required status set
- reuse it across evaluator and generator
- preserve `source_status` in generated review cases for traceability

---

## 6. Handling Unknown Statuses

Unknown statuses must not be silently treated as review-neutral business outcomes.

For the current scope, unknown statuses should:
- not create review cases automatically
- remain visible in tests as explicit unsupported inputs where relevant

This prevents silent semantic drift.

---

## 7. Expected Outcome After Alignment

After alignment:

- runtime report taxonomy and orchestration review semantics will match
- review case generation will reflect actual reconciliation results
- system scenarios involving review-required outcomes will be contract-consistent
- future product flows will build on a stable outcome vocabulary

---

## 8. Scope Boundary

This alignment applies to the current reconciliation -> review orchestration flow.

It does not yet redefine:
- advanced matching taxonomy in other domains
- ingestion conflict taxonomy
- operational recovery taxonomy
- UI-specific wording

Those may later require translation layers, but they are out of scope here.

---

## 9. Closure Criteria

This mini-epic is complete only when:

1. architecture doc is committed
2. evaluator and generator align to runtime taxonomy
3. tests are updated to reflect canonical statuses
4. Scenario 5 is rerun successfully against the aligned behavior