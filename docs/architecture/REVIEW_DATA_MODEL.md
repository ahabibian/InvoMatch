# EPIC 5 - Review Data Model

## Purpose
Define the minimum data model required to support review-controlled feedback validation, auditability, and learning eligibility gating.

This model is intentionally conservative.
It prioritizes traceability and control over optimization.

---

## Design Principles
- Raw feedback must remain separate from reviewed output.
- Review decisions must be explicit and finite.
- Audit history must be append-only in business terms.
- Learning eligibility must be derived from reviewed state, not raw input.
- Modified review output must be distinguishable from original user-submitted feedback.

---

## Core Entities

### 1. FeedbackRecord
Represents raw feedback captured from user interaction.

#### Minimum Fields
- feedback_id
- run_id
- source_type
- source_reference
- feedback_type
- raw_payload
- submitted_by
- submitted_at
- feedback_status

#### Notes
- This is the raw, unreviewed input.
- It must not be treated as trusted learning input.

---

### 2. ReviewSession
Represents a bounded review unit that groups one or more related feedback items.

#### Minimum Fields
- review_session_id
- session_status
- created_by
- created_at
- assigned_reviewer_id
- assigned_at
- completed_at
- session_notes

#### Notes
- A session may contain one or more review items.
- A session may remain open while some items are deferred.

---

### 3. ReviewItem
Represents a single feedback record under review.

#### Minimum Fields
- review_item_id
- review_session_id
- feedback_id
- item_status
- current_decision
- decision_reason
- reviewed_payload
- reviewed_by
- reviewed_at
- requires_followup
- learning_eligible

#### Notes
- reviewed_payload is nullable unless the decision is MODIFIED.
- learning_eligible must never be true for unreviewed items.

---

### 4. ReviewDecisionEvent
Represents an explicit reviewer action applied to a review item.

#### Minimum Fields
- decision_event_id
- review_item_id
- decision_type
- actor_id
- decision_reason
- previous_state
- new_state
- decision_payload
- created_at

#### Notes
- One review item may have multiple decision events over time.
- This entity captures decision history, not just current state.

---

### 5. AuditEvent
Represents append-only audit evidence for review activity.

#### Minimum Fields
- audit_event_id
- entity_type
- entity_id
- action_type
- actor_id
- occurred_at
- context_reference
- event_payload

#### Notes
- AuditEvent is broader than ReviewDecisionEvent.
- It may include assignment, re-open, defer, or system-produced gating events.

---

### 6. LearningEligibilityRecord
Represents the downstream reviewed output that may be consumed by learning logic.

#### Minimum Fields
- eligibility_id
- review_item_id
- feedback_id
- eligibility_status
- eligibility_reason
- derived_payload
- created_at
- created_by_system
- invalidated_at

#### Notes
- This is a derived record.
- It exists only after review logic determines that the reviewed item is eligible or ineligible.

---

## Enumerations

### FeedbackStatus
- CAPTURED
- QUEUED_FOR_REVIEW
- UNDER_REVIEW
- REVIEWED
- CLOSED

### ReviewSessionStatus
- OPEN
- IN_PROGRESS
- PARTIALLY_RESOLVED
- COMPLETED
- CANCELLED

### ReviewItemStatus
- PENDING
- IN_REVIEW
- APPROVED
- REJECTED
- MODIFIED
- DEFERRED
- CLOSED

### DecisionType
- APPROVE
- REJECT
- MODIFY
- DEFER
- REOPEN

### EligibilityStatus
- ELIGIBLE
- INELIGIBLE
- PENDING
- INVALIDATED

---

## Entity Relationships

### FeedbackRecord -> ReviewItem
- One FeedbackRecord may map to zero or more ReviewItems over time.
- Initial assumption should be one active ReviewItem per active review path.

### ReviewSession -> ReviewItem
- One ReviewSession contains one or more ReviewItems.

### ReviewItem -> ReviewDecisionEvent
- One ReviewItem may produce many ReviewDecisionEvents.

### ReviewItem -> LearningEligibilityRecord
- One ReviewItem may produce zero or one active LearningEligibilityRecord at a time.

### ReviewDecisionEvent -> AuditEvent
- Review decisions should produce corresponding audit events.

---

## State Model

### Raw Feedback Lifecycle
CAPTURED -> QUEUED_FOR_REVIEW -> UNDER_REVIEW -> REVIEWED -> CLOSED

### Review Item Lifecycle
PENDING -> IN_REVIEW -> APPROVED
PENDING -> IN_REVIEW -> REJECTED
PENDING -> IN_REVIEW -> MODIFIED
PENDING -> IN_REVIEW -> DEFERRED
DEFERRED -> IN_REVIEW -> APPROVED / REJECTED / MODIFIED

### Learning Eligibility Lifecycle
PENDING -> ELIGIBLE
PENDING -> INELIGIBLE
ELIGIBLE -> INVALIDATED

---

## Normalization Boundaries

### Keep Separate
- raw user input
- reviewed output
- audit events
- learning eligibility

### Do Not Collapse Into One Table
The following should not be merged into a single overloaded record:
- feedback capture
- review current state
- review event history
- audit evidence
- learning eligibility result

That would destroy traceability and create update ambiguity.

---

## Minimum Persistence Rules
- Raw feedback must be persisted before review begins.
- Review decisions must be persisted as explicit events.
- Current review state may be materialized for fast reads, but event history must remain available.
- Audit events must be append-only in business terms.
- Learning eligibility must be derivable from reviewed state, not manually guessed.

---

## Integrity Constraints
- A ReviewItem cannot become learning-eligible before a valid review decision exists.
- REJECTED items must not produce ELIGIBLE outputs.
- MODIFIED items must preserve a link to both raw feedback and reviewed payload.
- DEFERRED items must remain ineligible until resolved.
- A closed session must not contain unresolved active items unless explicitly marked partial.

---

## Open Questions
- Should one feedback item support multi-review escalation?
- Should reviewer assignment be exclusive or pooled?
- Should eligibility invalidation be soft-only or also evented explicitly?
- How much source context should be duplicated versus referenced?
- Should review comments be modeled separately from decision_reason?

---

## Deliverable Outcome
This data model defines the minimum persistence shape required before implementing review storage, review APIs, or feedback gating logic.

It is not the full storage schema yet.
It is the architecture-level contract for the review domain.