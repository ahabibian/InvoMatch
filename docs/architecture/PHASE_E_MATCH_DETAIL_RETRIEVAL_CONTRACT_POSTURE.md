
Phase E Match Detail Retrieval Contract Posture
Purpose

This document defines the product-facing retrieval posture for Match Detail.

Authoritative Read Path

Match Detail must be retrieved through a backend-owned product-facing read path.

The read path may be implemented as an existing endpoint or a newly defined endpoint, but the contract posture is the same:

the backend owns the match detail payload
the backend owns match identity resolution
the backend owns source linkage
the backend owns evidence availability
the backend owns error and not-found semantics
Input Identifier

The authoritative input identifier for Match Detail retrieval is match_id.

match_id is the handoff identifier from Review Queue to Match Detail.

Review Queue may show a row-level match summary, but it must not be treated as the source of complete detail truth.

Review-to-Detail Handoff

The review-to-detail handoff is:

Review Queue row -> match_id -> Match Detail retrieval -> backend-owned detail payload

The UI must not use invoice_id, payment_id, row index, table position, or client-side composite keys as substitutes for match_id.

Expected Response Envelope

The Match Detail response envelope should support the following product-facing shape:

match_id
invoice_id
payment_id
status
confidence
explanation
evidence
traceability
availability
errors or warnings when applicable
Contract Rule

A Review Queue row is a navigation and summary surface.

A Match Detail response is the authoritative detail surface.

The frontend may not reconstruct missing detail from Review Queue data.
The frontend may not enrich detail using local assumptions.
The frontend may not silently downgrade missing backend fields into successful display state.

Readiness Posture

The contract is sufficient for controlled Phase E reconsideration only if the next execution boundary confirms that Base44 binds to backend-owned detail retrieval and does not synthesize missing detail client-side.
