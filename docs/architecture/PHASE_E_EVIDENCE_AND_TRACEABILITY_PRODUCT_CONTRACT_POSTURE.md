
Phase E Evidence and Traceability Product Contract Posture
Purpose

This document defines the product-facing evidence and traceability posture for Match Detail / Evidence.

Evidence Posture

Evidence is backend-defined.

Evidence is not the same as explanation.

Explanation may describe why a match exists.
Evidence must identify the backend-owned facts, fields, comparisons, or source references that support the match.

Evidence Payload

Evidence may be embedded in the Match Detail response or retrieved through a dedicated backend-owned evidence path.

For the first controlled Phase E slice, embedded evidence is preferred unless a separate retrieval path already exists and is explicitly documented.

Evidence Item Shape

Each evidence item should support a bounded product-facing shape:

evidence_id or stable evidence reference
evidence_type
label
source_field
source_value
compared_field
compared_value
result
confidence_impact or relevance posture when available
source_reference when available
availability state
Evidence Classification

Evidence may include:

invoice number comparison
amount comparison
date comparison
counterparty or reference comparison
invoice-to-payment linkage
persisted match explanation support
backend-generated trace reference

Evidence does not include:

frontend formatting
UI labels alone
table row position
client-side guesses
explanation text without supporting backend fields
user-facing copy invented by Base44
Traceability Posture

Traceability must be product-facing only to the degree required for the pilot UI.

The first controlled slice requires enough traceability to show:

which invoice is linked
which payment is linked
which match record is being displayed
which evidence items support the match
whether supporting evidence is complete, missing, unavailable, or partially available

Advanced audit-chain, export-chain, and finalized-truth traceability remain outside this Mini-EPIC unless already available through backend read models.

Frontend Display Rule

The frontend may display evidence and traceability.

The frontend may not reinterpret evidence.
The frontend may not generate new evidence.
The frontend may not claim traceability that is not present in the backend payload.
The frontend may not convert explanation into evidence.
