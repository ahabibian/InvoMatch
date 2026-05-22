
Base44 Match Detail Binding Prompt Boundary
Mini-EPIC

Mini-EPIC 33.13.M — Controlled Base44 Match Detail Binding Prompt Boundary

Purpose

This document defines the controlled Base44 binding prompt boundary for the repaired Match Detail backend data-binding path.

The purpose is to convert the verified backend contract into frontend-safe Base44 implementation instructions without performing live Base44 wiring.

This document is a prompt and contract instruction boundary only.

Scope

This mini-epic defines:

which backend endpoint Base44 must call for Match Detail data
which fields may be displayed by Base44
which fields must remain display-only
which frontend behaviors are forbidden
how missing, failed, unauthorized, or incomplete backend responses must be rendered
which acceptance checks must pass before Base44 wiring can be authorized later
Non-Scope

This mini-epic does not:

connect Base44 to the live backend
modify Base44 screens
implement frontend data binding
create frontend fallback logic
generate frontend evidence
merge backend evidence on the frontend
calculate match confidence on the frontend
synthesize financial truth on the frontend
claim Scenario 15 completion
authorize production UI behavior
Binding Principle

Base44 is a display surface only.

The backend remains the source of truth for Match Detail data, evidence, trust state, permission state, match state, correction state, and export readiness.

Base44 must request already-prepared backend data and render it without reinterpretation.

Required Endpoint Usage

Base44 must call the backend Match Detail contract endpoint defined by the repaired backend binding path.

The endpoint must return a complete Match Detail payload prepared by the backend.

Base44 must not call multiple backend endpoints and assemble a Match Detail truth object on the frontend.

Base44 must not derive missing evidence, confidence, trust labels, correction state, or export readiness from partial data.

Display-Only Field Mapping

Base44 may display only fields returned by the backend contract.

The following categories are display-only:

match identity
tenant-visible match reference
invoice summary fields
payment summary fields
match state
confidence or trust state, if supplied by backend
evidence items, if supplied by backend
mismatch reasons, if supplied by backend
correction availability, if supplied by backend
finalized truth status, if supplied by backend
export readiness status, if supplied by backend
backend-generated timestamps
backend-generated audit or trace references

Base44 must not mutate, normalize, enrich, combine, or reinterpret these fields.

Forbidden Frontend Behavior

Base44 must not:

create evidence
merge evidence
calculate evidence weight
calculate match confidence
infer match status
infer correction status
infer finalization status
infer export readiness
fabricate missing backend values
use mock truth as fallback
silently replace failed backend data with static sample data
implement local financial decision rules
implement tenant permission rules
implement frontend-only trust logic
implement frontend-only error recovery that changes business meaning
Placeholder Discipline

If backend data is unavailable, Base44 may show an explicit bounded placeholder only when the placeholder clearly states that backend data is not available.

A placeholder must never appear as real evidence, real match truth, real audit state, or real export readiness.

A placeholder must not be used to claim Scenario 15 readiness.

Error and Failure Rendering Rules

If the backend response fails, Base44 must render a visible failure state.

If the backend returns unauthorized or forbidden, Base44 must render a permission failure state.

If the backend returns not found, Base44 must render a match-not-found state.

If the backend returns incomplete or invalid contract data, Base44 must render a contract failure state.

Base44 must not recover from these failures by manufacturing frontend truth.

Scenario 15 Boundary

This mini-epic does not complete Scenario 15.

Scenario 15 remains blocked until controlled Base44 wiring is performed and validated against the backend contract in a later implementation mini-epic.

No Scenario 15 completion claim is authorized by this document.

Acceptance Checks

This document is acceptable only if it confirms:

Base44 remains a display-only pilot UI surface
backend remains the source of truth
endpoint usage is defined at contract level only
display-only field mapping is defined
forbidden frontend behavior is explicit
error and failure rendering rules are explicit
no Base44 live wiring occurs
no Scenario 15 completion claim is made
no frontend-generated evidence is authorized
no frontend truth synthesis is authorized
Closure Statement

Mini-EPIC 33.13.M defines a controlled Base44 Match Detail binding prompt boundary only.

It prepares frontend-safe implementation instructions for a later Base44 wiring step but does not perform that wiring.

The repaired backend contract remains the authority.

Base44 remains blocked from manufacturing evidence, confidence, trust, permission, finalization, or export readiness.
