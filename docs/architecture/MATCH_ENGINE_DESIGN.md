# MATCH_ENGINE_DESIGN.md

## Purpose

This document defines the architecture of the InvoMatch matching intelligence engine.

The engine is responsible for transforming invoice/payment candidate pairs into deterministic, explainable, versioned reconciliation decisions. It is designed for auditability first, then scalability, then future learning.

---

## Scope

This EPIC covers:

- reconciliation rule engine
- confidence scoring
- explainability layer
- mismatch taxonomy
- correction learning direction

This document reflects the implemented architecture boundary reached in EPIC 3.

---

## Architectural Position

The matching engine is not a boolean matcher.

It is a governed decision system with five layers:

1. decision model
2. feature extraction
3. rule evaluation
4. decision building
5. taxonomy and explanation assembly

This separation is intentional. Feature extraction must remain deterministic and fact-oriented. Rule evaluation must remain explainable. Decision building must remain policy-bound. Taxonomy and summaries must remain stable and portable across API, UI, audit, and analytics layers.

---

## Layer 1 — Decision Model

The decision model defines the canonical output object for reconciliation outcomes.

Core types:

- `DecisionType`
- `DecisionStatus`
- `ConfidenceLevel`
- `MatchExplanation`
- `DecisionProvenance`
- `MatchDecision`

### Decision principles

- decision type is separate from workflow status
- explanation is a first-class object, not an afterthought
- provenance is mandatory for regression analysis and audit
- domain invariants are enforced at the model layer

### Supported decision types

- `one_to_one`
- `one_to_many`
- `many_to_one`
- `many_to_many`
- `unmatched`
- `ambiguous`
- `review_required`

### Supported statuses

- `proposed`
- `auto_approved`
- `user_confirmed`
- `user_corrected`
- `rejected`

---

## Layer 2 — Feature Extraction

The feature layer converts canonical invoice and payment records into deterministic feature vectors.

Core types:

- `InvoiceRecord`
- `PaymentRecord`
- `MatchFeatures`

### Feature design rules

- no scoring in feature extraction
- no business thresholds in feature extraction
- no hidden side effects
- all features must be testable and explainable

### Current feature groups

#### Amount
- exact match
- absolute delta
- percentage delta

#### Currency
- exact normalized currency match

#### Dates
- date delta
- payment before invoice
- payment after due date

#### Invoice number / reference
- normalized invoice number match
- invoice number found in payment reference
- token overlap score
- combined reference signal score

#### Counterparty
- supplier exact match
- supplier normalized match

#### Data quality
- OCR low confidence flag
- duplicate risk flag

The feature layer currently works at pair level. Candidate generation and grouped allocation remain future work.

---

## Layer 3 — Rule Evaluation

The rule engine transforms feature vectors into explainable score outputs.

Core types:

- `RuleEffect`
- `RuleResult`
- `ScoreResult`
- `RuleEngine`

### Rule categories

#### Positive rules
Examples:
- exact amount match
- near amount match
- normalized invoice number match
- supplier exact match
- close payment date
- strong or weak reference overlap

#### Negative rules
Examples:
- duplicate risk
- OCR low confidence
- payment before invoice
- payment after due date
- high amount drift
- far payment date

#### Hard-block rules
Examples:
- currency mismatch

### Output contract

`ScoreResult` carries:

- raw score
- normalized score
- all rule hits
- positive reason codes
- penalty codes
- hard-block codes
- extracted facts for downstream explainability

### Important principle

A policy rejection is not just a low score.  
That distinction is preserved through explicit hard-block support.

---

## Layer 4 — Decision Building

The decision builder converts score output plus candidate context into a `MatchDecision`.

Core types:

- `CandidateContext`
- `DecisionBuilder`

### Why candidate context exists

Ambiguity does not come from one candidate alone.  
It comes from competition across candidates.

The decision builder therefore consumes:

- `ScoreResult`
- `CandidateContext`

Where context includes:

- candidate count
- competing candidate count
- top score gap

### Current decision policy

#### Auto-approve
Triggered only when:
- score is high
- no hard block exists
- candidate separation is sufficient
- confidence is high

#### Ambiguous
Triggered when:
- there are competing candidates
- top score gap is too small
- score is otherwise strong enough to matter

#### Review required
Triggered when:
- score is meaningful
- but confidence is not strong enough for auto-approval

#### Unmatched
Triggered when:
- score is too weak
- or a hard-block policy rejection exists

### Confidence mapping

- `high` for strong dominant matches
- `medium` for review and ambiguous outcomes
- `low` for weak unmatched outcomes
- `rejected` for hard-block policy rejection

---

## Layer 5 — Explainability and Taxonomy

The final layer stabilizes the engine’s outward explanation and mismatch classification.

Core elements:

- `MismatchCode`
- `TaxonomyResult`
- `build_decision_summary(...)`

### Explainability rules

The engine produces explanation primitives directly.

Each decision carries:

- summary
- reasons
- penalties
- key facts
- competing candidate count
- score gap

The UI must not invent explanations on top of raw score data.

### Taxonomy principles

A mismatch must be classified into stable operational categories.

Current primary codes include:

- `CURRENCY_POLICY_REJECTED`
- `POLICY_REJECTED`
- `AMBIGUOUS_MULTIPLE_PAYMENTS`
- `WEAK_MATCH_SIGNAL`
- `NO_CANDIDATE_AMOUNT`
- `NO_CANDIDATE_DATE`
- `WEAK_REFERENCE_SIGNAL`

Current secondary codes include:

- `LOW_TOP_SCORE_GAP`
- `HIGH_AMOUNT_DRIFT`
- `EXCESSIVE_DATE_DRIFT`
- `OCR_LOW_CONFIDENCE`

This taxonomy is intentionally compact in v1. It is designed to be operationally useful without becoming noisy.

---

## Versioning Strategy

The engine stores explicit provenance:

- `match_engine_version`
- `rule_set_version`
- `confidence_policy_version`
- `taxonomy_version`
- `feature_schema_version`

This is mandatory for:

- audit
- regression analysis
- change control
- enterprise trust

Without provenance, future rule changes would make historical outcomes unverifiable.

---

## Correction Learning Direction

This EPIC does not implement adaptive learning, but the architecture is prepared for it.

### Correct direction

User corrections should first be captured as immutable events and analyzed offline.

That enables:

- false-positive analysis
- false-negative analysis
- rule weakness detection
- threshold tuning proposals
- supplier-specific pattern discovery

### Wrong direction

The engine must not mutate live weights directly from user corrections in real time.  
That would break auditability and version control.

So the correct path is:

1. correction capture
2. offline analysis
3. approved rule/policy revision
4. versioned rollout

---

## Current Limitations

The current implementation intentionally does not yet include:

- candidate generation at scale
- one-to-many allocation logic
- many-to-many optimization
- FX conversion handling beyond rejection
- supplier-specific adaptive policies
- learned ranking models
- correction event store

These are future EPIC concerns, not omissions inside this EPIC.

---

## Exit Assessment

EPIC 3 is considered structurally complete when:

- decision model exists and is validated
- feature extraction exists and is deterministic
- rule engine exists and is explainable
- decision builder exists and is policy-bound
- mismatch taxonomy exists
- explanation summary exists
- tests for all layers pass

At the current state, those conditions are satisfied for the v1 pair-based engine architecture.

---

## Final Position

InvoMatch should continue treating matching as a governed reconciliation decision engine, not a loose collection of heuristics.

The moat is not “AI” in the abstract.

The moat is:

- deterministic evidence extraction
- explainable rule evaluation
- disciplined confidence policy
- stable mismatch taxonomy
- strict provenance
- safe path toward learning