# EPIC 5 - Review & Audit System

## Goal
Define a controlled review layer between human corrections and the learning system so that feedback cannot directly influence matching behavior without validation, traceability, and auditability.

## Scope
- Review session model for grouping correction decisions
- Reviewer action model: approve, reject, modify, defer
- Audit trail for all reviewer decisions
- Feedback gating before learning eligibility
- Decision traceability for correction-to-learning flow
- Review outcome persistence requirements
- Minimal policy boundaries for trusted vs untrusted feedback

## Non-Goals
- Full learning-weight adaptation logic
- Rule promotion / rollback governance
- Replay and evaluation engine design
- Tenant-specific reviewer permission model
- Full enterprise compliance program

## Problem Statement
The system currently captures or plans to capture human feedback and correction signals, but without a formal review layer this creates a direct path from human input to model or rule adaptation.

That is unsafe.

Unreviewed feedback can be:
- incorrect
- inconsistent
- low-context
- duplicated
- biased by a single reviewer
- operationally untraceable later

A review architecture is required so that only validated feedback becomes eligible for downstream learning or rule consideration.

## Core Principles
- No correction becomes learning-eligible without review.
- Every review action must be traceable.
- Review decisions must be reproducible from persisted evidence.
- A reviewer may approve, reject, modify, or defer a correction.
- Review output must be structurally separate from raw feedback input.
- Auditability is required even when learning is not yet triggered.

## Domain Model

### Raw Feedback
A user-originated correction or action captured from the reconciliation workflow.

### Review Session
A bounded review unit that groups one or more related corrections for evaluation.

### Review Item
A single correction or feedback record under review.

### Reviewer Decision
The explicit outcome applied to a review item:
- APPROVED
- REJECTED
- MODIFIED
- DEFERRED

### Learning Eligibility
A downstream state assigned only after a reviewed item satisfies policy requirements.

### Audit Event
An immutable record of a review action, including actor, timestamp, decision, and reason context.

## Proposed Workflow
1. A raw correction is captured from user interaction.
2. The correction is stored as unreviewed feedback.
3. A review item is created or queued.
4. A reviewer evaluates the item in context.
5. The reviewer selects one of:
   - approve
   - reject
   - modify
   - defer
6. The decision is written to the review record.
7. An audit event is written.
8. Only approved or policy-qualified modified items become learning-eligible.
9. Rejected or deferred items remain excluded from learning.

## Review Decisions

### APPROVED
The correction is accepted as valid and may become learning-eligible.

### REJECTED
The correction is not trusted and must not affect learning.

### MODIFIED
The original correction is adjusted during review. The modified output, not the raw input, becomes the candidate reviewed signal.

### DEFERRED
The correction is neither accepted nor rejected yet. Additional context or another review pass is required.

## Required Data Boundaries

### Raw Feedback Store
Stores user-submitted corrections exactly as captured.

### Review Store
Stores review sessions, review items, reviewer actions, and decision metadata.

### Audit Store
Stores append-only audit events for all review actions.

### Learning Eligibility Output
A derived state or record that marks reviewed items as eligible or ineligible for downstream learning.

## Minimum Review Record Fields
Each review item should be able to capture at least:
- review_item_id
- feedback_id
- review_session_id
- reviewer_id
- decision
- decision_reason
- modified_payload (nullable)
- reviewed_at
- source_context_reference
- learning_eligible
- audit_event_id or equivalent linkage

## Audit Requirements
Every review action must record:
- who acted
- when they acted
- what decision they made
- what item was affected
- whether the reviewed payload differs from the original payload
- why the decision was made, where feasible

Audit records must be append-only from a business-logic perspective.

## Trust Policy Baseline
The first policy baseline should be conservative:
- raw feedback is untrusted by default
- only reviewed feedback can become learning-eligible
- rejected feedback is permanently excluded unless re-opened explicitly
- deferred feedback is excluded until resolved
- modified feedback is treated as a new reviewed output, not as raw feedback reuse

## Deliverables
- REVIEW_SYSTEM_ARCHITECTURE.md
- review session data model
- review decision state model
- audit event requirements
- feedback-to-learning gating definition

## Exit Criteria
This EPIC can be considered complete only when:
- a formal review workflow is defined
- reviewer decisions are explicit and finite
- audit trail requirements are documented
- no raw feedback can bypass review in the system design
- learning eligibility is structurally separated from raw feedback

## Risks
- Overly weak review policy allows bad learning input
- Overly strict review policy slows operational throughput
- Missing audit detail weakens enterprise trust
- Review data model may be too thin for future governance needs
- Deferral handling may become a backlog sink if not managed

## Dependencies
- EPIC 4 feedback capture structures
- persistence layer support for review and audit records
- future governance layer in EPIC 6
- future replay/evaluation capabilities in EPIC 7

## Notes
This EPIC is not about making the system smarter first.
It is about making the system safer before it becomes smarter.