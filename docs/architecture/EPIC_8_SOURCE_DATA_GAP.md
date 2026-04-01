# EPIC 8 - Source Data Contract Gap

## 1. Objective

Document the source-data gaps that currently block a trustworthy FinalizedResult projection for export.

---

## 2. Current Source Model

Current invoice and payment ingestion provides:

- id
- date
- amount
- reference

Current source data does NOT provide:

- currency
- vendor_name
- explicit invoice_number field separate from reference
- payment currency

---

## 3. Why This Is a Blocker

The EPIC 8 export contract currently requires:

- invoice currency
- payment currency

These fields are mandatory in the current export domain models.

Because source ingestion does not provide them, FinalizedResult cannot be constructed truthfully without:

- guessing
- hardcoding
- weakening the export contract

All three are unacceptable for a trustworthy financial export layer.

---

## 4. Confirmed Gap

### Export contract requires:
- FinalizedInvoiceRef.currency
- FinalizedPaymentRef.currency

### Source contract currently provides:
- no currency field at invoice level
- no currency field at payment level

This is a hard source-schema gap.

---

## 5. Recommended Resolution

Preferred option:

### Evolve source schema
Add the following fields to source ingestion:

Invoice CSV:
- currency

Payment CSV:
- currency

Optional future improvement:
- vendor_name
- explicit invoice_number field if reference is not sufficient

---

## 6. Non-Recommended Resolution

The following options are explicitly discouraged:

- guessing currency
- hardcoding a default currency
- making export currency optional only to unblock implementation

These would reduce export trustworthiness.

---

## 7. Immediate Impact on EPIC 8

Phase 8 implementation of finalized projection should NOT begin until this gap is resolved or explicitly re-scoped.

Current status:

- export architecture: defined
- projection contract: defined
- source data contract: insufficient

---

## 8. Next Step

Before implementing finalized projection:

1. decide whether source schema will be extended
2. if yes, update ingestion and source models
3. then implement finalized projection
