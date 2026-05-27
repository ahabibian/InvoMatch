
# Mini-EPIC 33.13.P-S — Controlled Review Queue Frontend Binding Plan
## Status

Planned.

Mini-EPIC 33.13.P-S defines the controlled frontend binding plan for connecting the Pilot UI Review Queue to the backend-validated GET /api/review/queue contract.

This mini-epic is a planning and boundary document only.

It does not modify Base44.

It does not perform live binding.

It does not validate live rendering.

It does not create UI evidence.

It does not claim Review Queue to Match Detail end-to-end completion.

It does not claim Scenario 15 completion.

Scenario 15 remains incomplete.

Base44 binding remains blocked until a later explicitly scoped live binding execution mini-epic.

## Baseline

Mini-EPIC 33.13.P-S starts only after Mini-EPIC 33.13.P-R authorized controlled frontend binding planning.

The backend contract baseline is the validated GET /api/review/queue row collection contract.

The frontend binding target is the Pilot UI Review Queue surface only.

The backend remains the sole owner of review queue truth.

The frontend may display backend-owned values but must not derive, repair, infer, complete, or manufacture product truth.

## Objective

Define the controlled plan for a later live binding execution mini-epic that connects the Pilot UI Review Queue to GET /api/review/queue.

This plan must specify:

The Base44 binding boundary.
The allowed display fields.
The forbidden frontend-truth behaviors.
The match_id navigation handoff rules.
The loading, error, and empty-state behavior.
The backend ownership rules.
The acceptance criteria for a later live binding execution mini-epic.
## Base44 Binding Boundary

Base44 may only act as a Pilot UI presentation layer for backend-owned review queue rows.

Base44 may request the backend review queue collection.

Base44 may render rows returned by the backend.

Base44 may show backend-provided row status, reason, identifiers, confidence values, availability signals, and navigation targets when present in the contract.

Base44 must not become the source of review queue truth.

Base44 must not generate review queue rows locally.

Base44 must not construct synthetic review queue cases.

Base44 must not decide whether a review item is open, closed, terminal, actionable, blocked, unavailable, or reviewable.

Base44 must not modify row status locally.

Base44 must not fabricate missing match_id values.

Base44 must not invent evidence availability.

Base44 must not infer trust, risk, or error semantics beyond backend-provided values.

Base44 must not treat a successful table render as product completion.

## Allowed Display Fields

The later live binding execution mini-epic may bind only fields that are present in the backend-validated GET /api/review/queue contract.

The allowed display field categories are:

Backend-provided review row identifier.
Backend-provided match_id or match navigation identifier.
Backend-provided review status.
Backend-provided review reason or review category.
Backend-provided confidence or score value when present.
Backend-provided amount/date/invoice/reference display values when present.
Backend-provided availability or actionability flags when present.
Backend-provided tenant-safe display fields.
Backend-provided created/updated timestamps when present.
Backend-provided error or unavailable-state fields when present.

The frontend must render these values as received.

Formatting is allowed only for presentation readability and must not change the meaning of the backend value.

Examples of allowed formatting:

Date formatting for readability.
Currency display formatting when the backend value and currency are present.
Truncation of long identifiers for visual layout while preserving a full value in accessible text or detail context.
Badge styling for backend-provided status values.

Formatting must not create new domain meaning.

## Forbidden Frontend-Truth Behaviors

The frontend must not perform any of the following behaviors:

Create review queue rows from local state.
Hide backend rows because they appear incomplete to the frontend.
Add rows that were not returned by the backend.
Reclassify backend status values.
Convert unknown values into accepted values.
Treat missing values as valid values.
Derive review status from amount, date, confidence, or local UI state.
Derive action availability from frontend-only rules.
Invent match detail navigation targets.
Invent evidence presence.
Infer tenant access permissions.
Infer whether a review row is safe to resolve.
Infer export readiness from the review queue table.
Claim review completion based on row rendering.
Claim Review Queue to Match Detail completion based on link visibility alone.
Claim Scenario 15 completion.

Any unknown, unsupported, missing, or contract-breaking value must be surfaced through controlled loading/error/empty/unavailable behavior rather than repaired by the frontend.

## match_id Navigation Handoff Rules

The Review Queue may provide navigation handoff to Match Detail only through backend-provided match_id or an explicitly contract-approved match navigation identifier.

The Review Queue must not synthesize match_id.

The Review Queue must not transform row identifiers into match_id unless the backend contract explicitly defines that mapping.

If a row has a valid backend-provided match_id, the later live binding execution mini-epic may route the operator to the Match Detail surface using that value.

If a row does not have a valid backend-provided match_id, the row must not expose an active Match Detail navigation action.

If a row has unavailable match detail access, the frontend must show a controlled unavailable state rather than generating a fallback route.

A visible Review Queue to Match Detail link is not enough to claim end-to-end completion.

Review Queue to Match Detail end-to-end completion requires separately validated live binding, rendering, route handoff, Match Detail load, evidence availability, and acceptance evidence under a later explicitly scoped execution mini-epic.

## Loading State Behavior

The Review Queue must show a controlled loading state while waiting for GET /api/review/queue.

The loading state must not show fake rows.

The loading state must not show placeholder values that look like backend truth.

Skeletons may be used only as visual loading placeholders.

Skeletons must not contain realistic invoice numbers, amounts, names, statuses, confidence values, or match identifiers.

The loading state must clearly end only when backend data, an empty state, or an error state is available.

## Error State Behavior

If the backend request fails, the Review Queue must show a controlled error state.

The error state must not fall back to static sample data.

The error state must not hide the failure.

The error state must not claim that the queue is empty.

The error state must preserve backend ownership by making clear that review queue truth is unavailable until the backend responds successfully.

If the backend returns a contract-shaped error, the frontend may display the backend-provided error message or category if it is safe for operator display.

If the error is unexpected, the frontend must show a generic controlled failure message and must not expose internal implementation details.

## Empty State Behavior

If GET /api/review/queue returns a valid empty collection, the Review Queue may show an empty state.

The empty state must mean only that the backend returned no open review queue rows for the current context.

The empty state must not claim:

All work is complete.
Scenario 15 has reached a completed state.
The run is finalized.
Export is ready.
Match Detail is validated.
Review Queue to Match Detail end-to-end flow is complete.

The empty state must remain a backend-owned display outcome.

## Backend Ownership Rules

The backend owns:

Which review rows exist.
Which rows are returned in the queue.
Which rows are terminal and therefore excluded.
Which rows are actionable.
Which status values are valid.
Which match_id values are valid.
Which rows can navigate to Match Detail.
Which errors are contract-level failures.
Which tenant/user context is authorized.
Which data is safe to expose to the Pilot UI.
Which review queue state is current.

The frontend owns only:

Presentation layout.
Visual formatting.
Loading state display.
Controlled error state display.
Controlled empty state display.
Operator navigation handoff using backend-provided identifiers.
Non-truth UI affordances that do not change backend meaning.
## Tenant and Permission Boundary

The Review Queue frontend must not infer tenant scope.

The Review Queue frontend must not filter rows by tenant using local assumptions.

The Review Queue frontend must not expose cross-tenant data.

The backend contract must provide only tenant-authorized rows for the current request context.

If the backend returns an authorization or permission failure, the frontend must show a controlled permission/error state.

The frontend must not replace permission failures with empty states.

## Later Live Binding Execution Mini-Epic Requirements

A later live binding execution mini-epic may proceed only if it explicitly scopes and validates:

The actual Base44 binding target.
The actual backend endpoint URL or API client path.
The request context and authentication assumptions.
The exact response shape consumed by the UI.
The row rendering behavior.
The match_id handoff behavior.
The no-synthetic-row rule.
The no-frontend-truth rule.
Loading state behavior.
Error state behavior.
Empty state behavior.
Evidence that the Review Queue renders backend-owned rows.
Evidence that Base44 does not manufacture queue truth.

The later execution mini-epic must still not claim Scenario 15 completion unless it also validates the required end-to-end scope.

## Acceptance Criteria for Later Live Binding Execution

The later live binding execution mini-epic must satisfy all of the following before it can close:

GET /api/review/queue is called by the Pilot UI through the approved binding path.
The Review Queue renders only backend-returned rows.
No static demo rows remain active in the bound Review Queue surface.
No frontend-generated review rows exist.
Allowed display fields map directly to backend contract fields.
Unknown or missing fields are handled without frontend truth repair.
Loading state does not show fake truth.
Error state does not fall back to sample data.
Empty state does not claim completion.
match_id navigation is enabled only when backend-provided.
Rows without backend-provided match_id do not expose active Match Detail navigation.
Backend ownership of review queue truth is preserved.
Tenant and permission failures are not converted into empty states.
Review Queue to Match Detail end-to-end completion is not claimed unless separately validated.
Scenario 15 completion is not claimed unless live binding, rendering, navigation, and acceptance evidence are explicitly validated under the execution mini-epic scope.
## Explicit Non-Actions

Mini-EPIC 33.13.P-S does not modify Base44.

Mini-EPIC 33.13.P-S does not perform live binding.

Mini-EPIC 33.13.P-S does not validate live rendering.

Mini-EPIC 33.13.P-S does not create UI evidence.

Mini-EPIC 33.13.P-S does not create a Base44 prompt package.

Mini-EPIC 33.13.P-S does not execute Review Queue to Match Detail navigation.

Mini-EPIC 33.13.P-S does not validate Match Detail loading from a Review Queue row.

Mini-EPIC 33.13.P-S does not claim Review Queue to Match Detail end-to-end completion.

Mini-EPIC 33.13.P-S does not claim Scenario 15 completion.

Scenario 15 remains incomplete.

Base44 binding remains blocked until a later live binding execution mini-epic.

## Exit Criteria

Mini-EPIC 33.13.P-S may close only when:

This controlled frontend binding plan exists in the repository.
The plan defines the Base44 binding boundary.
The plan defines allowed display fields.
The plan defines forbidden frontend-truth behaviors.
The plan defines match_id navigation handoff rules.
The plan defines loading behavior.
The plan defines error behavior.
The plan defines empty-state behavior.
The plan defines backend ownership rules.
The plan defines tenant and permission boundary rules.
The plan defines acceptance criteria for a later live binding execution mini-epic.
The plan explicitly states that Base44 is not modified.
The plan explicitly states that live binding is not performed.
The plan explicitly states that live rendering is not validated.
The plan explicitly states that UI evidence is not created.
The plan explicitly states that Review Queue to Match Detail end-to-end completion is not claimed.
The plan explicitly states that Scenario 15 completion is not claimed.
The plan explicitly states that Scenario 15 remains incomplete.


