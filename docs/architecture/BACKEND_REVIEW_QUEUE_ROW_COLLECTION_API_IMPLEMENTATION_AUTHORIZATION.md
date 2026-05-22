
Backend Review Queue Row Collection API Implementation Authorization
Mini-EPIC

Mini-EPIC 33.13.P-O — Backend Review Queue Row Collection API Implementation Authorization

Purpose

This document authorizes the backend-first implementation of a Review Queue row collection API required to unblock live Match Detail validation.

This authorization follows the backend Review Queue row collection API gap recorded in Mini-EPIC 33.13.P-NB.

This document authorizes a future backend implementation mini-epic.

This document does not implement the endpoint.

This document does not bind Base44.

This document does not create fake rows.

This document does not validate live Match Detail payload rendering.

This document does not claim Scenario 15 completion.

Source Gap

The source API gap document is:

docs/architecture/BACKEND_REVIEW_QUEUE_ROW_COLLECTION_API_GAP.md
Authorization Decision

Backend implementation is authorized for a controlled Review Queue row collection API.

The authorized implementation must be backend-first.

The authorized implementation must expose backend-owned Review Queue rows.

The authorized implementation must not depend on Base44-generated truth.

The authorized implementation must not rely on fake rows for live validation.

The authorized implementation must not move Scenario 15 to complete.

Authorized Endpoint

The authorized preferred endpoint is:

GET /api/review/queue

The endpoint must return a collection of backend-owned Review Queue rows.

The endpoint must not return Match Detail payloads.

The endpoint must not return raw evidence lists intended for Match Detail rendering.

The endpoint must not return frontend-ready synthesized truth.

Alternative Endpoint Constraint

A run-scoped endpoint may be used only if the project explicitly decides Review Queue is run-scoped.

The alternative run-scoped shape is:

GET /api/reconciliation/runs/{run_id}/review

If a run-scoped shape is used, the implementation must define how Base44 obtains a backend-owned run_id without frontend invention.

No frontend-created run_id may be used as live validation evidence.

Required Backend Row Source

The implementation should use existing backend review primitives where appropriate.

Candidate backend sources include:

ReviewIntegrationService active case behavior
ReviewService review item behavior
ReviewStore or SqliteReviewStore persisted review_items
existing run review API behavior where appropriate

The implementation must not create rows directly in the API layer as fake product truth.

The implementation must not hard-code demo rows as live validation rows.

Required Row Shape

Each returned row must include one backend-owned identifier.

Acceptable identifier fields include:

case_id
review_id
review_item_id
match_id
matchId
reviewId
match_id
review_id

The implementation must select a clear identifier strategy.

The selected identifier must be documented and tested.

The selected identifier must support Review Queue to Match Detail handoff.

Required Display-Only Fields

The row response may include only bounded display-only fields needed for operator recognition.

Allowed fields include:

id or case_id
run_id, if backend-owned and needed for context
match_id, if backend-owned and needed for Match Detail lookup
status
reason_code or review_reason
invoice_summary_label
payment_summary_label
amount_summary, if backend-computed
date_summary, if backend-computed
created_at or updated_at
trace_id or audit_reference

All row fields must be display-only from the Base44 perspective.

The frontend must not calculate, normalize, enrich, merge, or infer financial truth from these fields.

Prohibited Response Fields

The endpoint must not expose:

reviewed_payload
reviewed_by
backend-private audit internals
internal-only reviewer state
raw Match Detail evidence payloads
frontend-ready synthesized financial truth
frontend-created confidence
frontend-created export readiness
frontend-created permission conclusions
demo-only row data as live validation evidence
Required Failure Behavior

The implementation must define and test:

empty queue response
unauthorized response when authentication is missing or invalid
forbidden response where tenant or role access is not permitted
backend review store unavailable behavior
invalid or incomplete row shape behavior
unknown identifier behavior later handled by Match Detail

Base44 must be able to render these as visible empty or failure states.

Base44 must not replace failures with fake rows.

Tenant And Security Requirements

The endpoint must respect tenant isolation.

The endpoint must respect authenticated user context if authentication is enabled.

The endpoint must not leak rows across tenants.

The endpoint must not expose internal reviewer payloads to unauthorized users.

The endpoint must align with existing authentication, authorization, and security audit services where applicable.

Required Tests

The future backend implementation must include tests for:

successful row collection response
empty queue response
unauthorized response
forbidden or tenant-isolated response where applicable
row shape includes a backend-owned identifier
row shape excludes reviewed_payload
row shape excludes reviewed_by
row shape excludes backend-private audit internals
row identifier can be passed to Match Detail
endpoint response does not require frontend truth synthesis
endpoint response does not expose fake rows as live validation rows
Required Contract Assertions

The implementation tests must assert that:

every row has exactly the required identifier semantics
every row is backend-owned
no row is produced from frontend demo state
no row requires Base44 to assemble Match Detail payloads
no row contains evidence that belongs only in Match Detail
no row contains calculated frontend confidence
no row contains frontend-inferred export readiness
no row contains frontend-inferred permission conclusions
Base44 Boundary

Base44 binding remains blocked during this authorization mini-epic.

Base44 may not bind Review Queue to this endpoint until the backend endpoint is implemented and tested in a later mini-epic.

Base44 may not treat this authorization as a live endpoint.

Base44 may not treat this authorization as Scenario 15 readiness.

Scenario 15 Boundary

Scenario 15 remains incomplete.

Scenario 15 cannot be completed by implementation authorization.

Scenario 15 cannot be completed by a backend endpoint alone.

Scenario 15 may only move toward readiness after:

backend-owned Review Queue row endpoint is implemented and tested
Review Queue binds to backend-owned rows without frontend truth synthesis
Match Detail receives a real backend-owned identifier
Match Detail renders backend-provided payload display-only or backend-governed failure state
live validation evidence is recorded separately
Authorized Next Mini-EPIC

The next implementation mini-epic may implement the backend Review Queue row collection API within this authorization boundary.

The next implementation mini-epic must include code and tests.

The next implementation mini-epic must not modify Base44.

The next implementation mini-epic must not claim Scenario 15 completion.

Acceptance Checks

This document is acceptable only if it confirms:

backend-first implementation is authorized
preferred endpoint is GET /api/review/queue
endpoint must return backend-owned rows
endpoint must not return Match Detail payloads
endpoint must not return fake rows
required row identifier rules are explicit
allowed display-only fields are bounded
prohibited response fields are explicit
failure behavior is required
tenant and security requirements are explicit
required tests are explicit
Base44 binding remains blocked
Scenario 15 remains incomplete
no endpoint is implemented in this mini-epic
no fake row is authorized
no Base44 binding is authorized
no live Match Detail payload validation is claimed
no frontend-generated evidence is authorized
no frontend truth synthesis is authorized
Closure Statement

Mini-EPIC 33.13.P-O authorizes backend-first implementation of the Review Queue row collection API.

The preferred endpoint is GET /api/review/queue.

The endpoint must return backend-owned Review Queue rows only.

Base44 Review Queue binding remains blocked until implementation and tests are complete.

No endpoint was implemented.

No fake row was authorized.

No Base44 binding was authorized.

No live Match Detail payload validation was claimed.

No Scenario 15 completion claim was made.

No frontend-generated evidence was authorized.

No frontend truth synthesis was authorized.
