# EPIC 8 - Finalized Result Projection Contract

## 1. Objective

Define a deterministic, auditable, and product-aligned projection layer that produces export-ready FinalizedResult objects from:

- ReconciliationReport (matching output)
- Source data (invoice and payment CSV)
- Review domain outcomes (feedback and decisions)

This projection is the single source of truth for export.

---

## 2. Core Principle

Export must reflect:

"What the system believes after review is complete"

NOT:
- raw matching output
- partial or pending review state
- inferred or guessed data

---

## 3. Data Sources

### 3.1 Matching Layer (ReconciliationReport)

Provides:
- invoice_id
- match_result.status
- payment_ids or payment_id
- confidence_score

Limitations:
- no invoice or payment details
- no currency
- no vendor info

### 3.2 Source Data (CSV)

Provides:
- invoice fields (id, date, amount, reference)
- payment fields (id, date, amount, reference)

Rule:
Source data is the authoritative base for financial fields.

### 3.3 Review Layer

Provides:
- final decision (APPROVE, MODIFY, REJECT, DEFER)
- reviewed_payload (for MODIFY)
- reviewer identity and timestamp

Rule:
Review overrides matching output when applicable.

---

## 4. Binding Rules

### 4.1 Result Identity

Each FinalizedResult is anchored by:

- invoice_id (primary key)

Mapping:
- ReconciliationResult.invoice_id == Invoice.id

### 4.2 Review Binding

FeedbackRecord.source_reference MUST equal:

- invoice_id

ReviewItem.feedback_id -> FeedbackRecord -> source_reference

Rule:
Review applies to a specific invoice result.

---

## 5. Decision Resolution

### 5.1 APPROVE

- Accept match_result as-is
- No overrides
- Derive final decision type from approved match_result

### 5.2 MODIFY

- Use reviewed_payload as override
- reviewed_payload MAY define:
  - payment_ids
  - matched_amount

Rule:
reviewed_payload does NOT directly set decision_type

Final decision_type MUST be derived from matched_amount relative to invoice.amount:
- matched_amount == 0 -> UNMATCHED
- 0 < matched_amount < invoice.amount -> PARTIAL
- matched_amount == invoice.amount -> MATCH

### 5.3 REJECT

- Force decision_type = UNMATCHED
- Ignore payment_ids
- matched_amount = 0

### 5.4 DEFER or PENDING

Rule:
NOT EXPORTABLE

These results MUST NOT appear in export.

---

## 6. Source Reconstruction

### 6.1 Invoice

Construct from CSV:
- invoice_id
- invoice_date
- amount
- reference -> invoice_number

### 6.2 Payments

Construct from CSV using payment_ids from:
- match_result, or
- reviewed_payload override

---

## 7. Currency Rule

Rule:
All results in a run MUST share a single currency.

If violated:
- export must fail with integrity error

---

## 8. Determinism Rules

### 8.1 Result Ordering

Sort by:
1. invoice_date (None last)
2. invoice_id

### 8.2 Payment Ordering

Sort by:
1. payment_date (None last)
2. payment_id

---

## 9. Export Eligibility

A run is exportable ONLY if:

- run.status == "completed"
- all review items relevant to that run are in terminal states:
  - APPROVED
  - REJECTED
  - MODIFIED

If any relevant review item is:
- PENDING
- IN_REVIEW
- DEFERRED

export MUST fail.

---

## 10. Integrity Constraints

For each result:

- MATCH:
  matched_amount == invoice.amount

- PARTIAL:
  matched_amount > 0
  matched_amount < invoice.amount

- UNMATCHED:
  matched_amount == 0

All:
- payment currency must match invoice currency

---

## 11. Output Guarantee

FinalizedResult must be:
- deterministic
- reproducible
- auditable
- independent of runtime ambiguity

---

## 12. Non-Goals

This layer does NOT:
- read from API
- perform matching
- infer missing financial data
- guess review outcomes

---

## 13. Next Step

Implement:
- finalized_result_projection.py
- concrete FinalizedResultReader

Based strictly on this contract.

No deviations allowed.
