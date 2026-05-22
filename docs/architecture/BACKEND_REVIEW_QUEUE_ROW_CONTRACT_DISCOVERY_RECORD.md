
Backend Review Queue Row Contract Discovery Record
Mini-EPIC

Mini-EPIC 33.13.P-N.1 — Backend Review Queue Row Contract Discovery Record

Purpose

This document records the refined backend discovery result for Review Queue row availability.

The purpose is to distinguish existing backend review primitives from a confirmed Base44-facing Review Queue row collection contract.

This is a discovery record only.

This document does not implement a backend endpoint.

This document does not bind Base44 to backend Review Queue rows.

This document does not create fake rows.

This document does not validate live Match Detail payload rendering.

This document does not claim Scenario 15 completion.

Source Boundary

The source availability boundary is:

docs/architecture/BACKEND_OWNED_REVIEW_QUEUE_ROW_AVAILABILITY_BOUNDARY.md
Discovery Input

A focused repository discovery scan was performed across src and tests.

The scan looked for:

backend Review Queue row APIs
review service contracts
review item models
review store behavior
Match Detail identifier linkage
product contract tests related to review rows
run review API behavior

The scan made no repository changes.

The working tree remained clean after discovery.

Confirmed Backend Review Primitives

The backend contains review-related primitives.

The discovery found evidence of:

review API behavior for a reconciliation run
review item creation through ReviewService
review feedback records
review sessions
audit events for review item creation
active review case mapping through ReviewIntegrationService
SQLite persistence for review_items
tests around review API behavior
tests around review service behavior
tests around review integration behavior
tests around SQLite review store persistence
Confirmed Run Review API Behavior

The discovery found tests for a run-scoped review API.

The tested behavior includes:

unauthorized requests return 401
missing review case returns 404
a product review case can be returned for a run
returned response includes case_id
returned response includes run_id
returned response includes status
returned response includes reason_code
returned response includes match_id
returned response includes explanation
returned response does not expose reviewed_payload
returned response does not expose reviewed_by

This indicates that a backend-governed run review case contract exists.

It does not by itself prove that a Base44-facing Review Queue row collection endpoint exists.

Confirmed Review Service Behavior

The discovery found ReviewService behavior for:

creating review sessions
creating review items
queueing feedback for review
emitting audit events
starting review
applying decisions
marking review items approved or rejected
setting learning eligibility

This confirms that the backend has review domain machinery.

It does not by itself prove that Review Queue can list backend-owned rows for Base44.

Confirmed Review Integration Behavior

The discovery found ReviewIntegrationService behavior for:

creating review cases from orchestration cases
persisting feedback, sessions, review items, and audit records
returning active pending cases through get_active_cases
excluding terminal review items from active cases
idempotent case creation for repeated run and invoice scope

This is the strongest discovered candidate for a Review Queue row source.

However, discovery did not confirm a Base44-facing API endpoint exposing this collection contract.

Confirmed Persistence Behavior

The discovery found SQLite review store behavior for:

creating review_sessions table
creating review_items table
saving and loading review sessions
saving and loading review items
saving and loading audit events

This confirms that backend-owned review rows can be persisted.

It does not by itself expose those rows to Base44.

Discovery Decision

The discovery result is partial.

Outcome A is not fully satisfied because a Base44-facing Review Queue row collection endpoint was not confirmed.

Outcome B is not fully satisfied because backend review primitives and candidate row-source services do exist.

The correct classification is:

Partial backend row foundation exists, but Base44-facing Review Queue row collection contract remains unconfirmed.

Current Product Meaning

The project has enough backend review infrastructure to justify a targeted backend contract gap analysis.

The project does not yet have enough confirmed contract evidence to bind Base44 Review Queue to real backend-owned rows.

The project must not treat demo handoff behavior as live backend validation.

The project must not treat internal review service primitives as an already validated Base44-facing row contract.

Required Next Step

The next mini-epic must define the backend Review Queue row collection API gap or confirm an existing endpoint with stronger evidence.

The next mini-epic should answer:

Should Base44 Review Queue use a collection endpoint such as GET /api/review/queue?
Should Base44 Review Queue remain run-scoped and use GET /api/reconciliation/runs/{run_id}/review?
Should ReviewIntegrationService.get_active_cases be exposed through an API endpoint?
Which identifier should Review Queue pass to Match Detail: case_id, review_id, review_item_id, match_id, or run_id plus match_id?
Which fields are allowed in the Review Queue row contract?
Which fields must remain absent from the Review Queue row contract?
How should empty, not-found, unauthorized, and contract failure states be represented?
Forbidden Interpretation

This discovery must not be interpreted as:

live backend validation passed
real backend-owned Review Queue row validated
Base44 Review Queue binding authorized
Match Detail payload validation passed
Scenario 15 complete
demo handoff equivalent to backend row validation
internal service availability equivalent to product API availability
Scenario 15 Boundary

Scenario 15 remains incomplete.

Scenario 15 cannot be completed from discovery evidence.

Scenario 15 cannot be completed from internal backend primitives alone.

Scenario 15 can only move toward readiness after a real Base44-facing backend-owned Review Queue row contract is confirmed or implemented, and after Match Detail backend-bound behavior is validated.

Acceptance Checks

This document is acceptable only if it confirms:

backend review primitives exist
run review API behavior exists
ReviewIntegrationService active case behavior exists
SQLite review persistence exists
Base44-facing Review Queue row collection endpoint is not yet confirmed
discovery outcome is partial, not complete
next step is backend contract gap analysis or endpoint confirmation
no fake row is authorized
no Base44 binding is authorized
no live Match Detail payload validation is claimed
no Scenario 15 completion claim is made
no frontend-generated evidence is authorized
no frontend truth synthesis is authorized
Closure Statement

Mini-EPIC 33.13.P-N.1 records the backend Review Queue row contract discovery result.

Backend review primitives exist.

A candidate row-source service exists through active review case behavior.

A Base44-facing Review Queue row collection contract remains unconfirmed.

No fake row was authorized.

No Base44 binding was authorized.

No live backend payload validation was claimed.

No real backend-owned row validation was claimed.

No Scenario 15 completion claim was made.

No frontend-generated evidence was authorized.

No frontend truth synthesis was authorized.
