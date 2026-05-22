
Base44 Match Detail Paste-Ready Prompt Package
Mini-EPIC

Mini-EPIC 33.13.N — Base44 Match Detail Paste-Ready Prompt Package Boundary

Purpose

This document converts the controlled Match Detail binding prompt boundary into a paste-ready Base44 instruction package.

This document prepares the exact Base44-facing prompt text for a later controlled Match Detail screen wiring step.

This document does not connect Base44 to the backend.

This document does not modify the live Base44 UI.

This document does not execute any endpoint.

This document does not perform implementation.

This document does not claim Scenario 15 completion.

Source Boundary

This prompt package is derived from:

docs/architecture/BASE44_MATCH_DETAIL_BINDING_PROMPT_BOUNDARY.md

The source boundary remains authoritative.

If this prompt package conflicts with the source boundary, the source boundary wins.

Paste-Ready Base44 Instruction Package

The following prompt is intended to be pasted into Base44 only during a later authorized wiring mini-epic.

Do not paste or execute this prompt until a later mini-epic explicitly authorizes live Base44 wiring.

BEGIN BASE44 PROMPT PACKAGE

You are updating the InvoMatch Match Detail screen as a display-only frontend surface.

You must bind the Match Detail screen to the backend-provided Match Detail contract.

The backend is the only source of truth.

Base44 must not create, infer, calculate, merge, synthesize, or repair financial truth.

Required Backend Call

Use the backend Match Detail contract endpoint provided by the InvoMatch backend.

The screen must request one complete Match Detail payload from the backend.

Do not call multiple backend endpoints and assemble a synthetic Match Detail object on the frontend.

Do not combine independent backend responses into frontend-generated truth.

Do not use sample data as a fallback for failed backend data.

Display-Only Rendering Rule

Render only fields returned by the backend payload.

All rendered fields are display-only unless the backend contract explicitly provides an action affordance.

The frontend must not mutate, normalize, enrich, combine, recalculate, or reinterpret backend fields.

Allowed Display Categories

The Match Detail screen may display backend-provided values from these categories only:

match identity
tenant-visible match reference
invoice summary
payment summary
match state
backend-provided confidence or trust state
backend-provided evidence items
backend-provided mismatch reasons
backend-provided correction availability
backend-provided finalized truth status
backend-provided export readiness status
backend-generated timestamps
backend-generated audit references
backend-generated trace references

If a field is not returned by the backend payload, do not invent it.

If a label is unclear, display a neutral missing-data state rather than inventing meaning.

Forbidden Frontend Behavior

Do not create evidence.

Do not merge evidence.

Do not calculate evidence weight.

Do not calculate match confidence.

Do not infer match status.

Do not infer correction status.

Do not infer finalization status.

Do not infer export readiness.

Do not fabricate missing backend values.

Do not use mock truth as fallback.

Do not silently replace failed backend data with static sample data.

Do not implement local financial decision rules.

Do not implement tenant permission rules.

Do not implement frontend-only trust logic.

Do not implement frontend-only error recovery that changes business meaning.

Do not generate financial truth on the frontend.

Error-State Rendering

If the backend request fails, show a visible backend failure state.

If the backend returns unauthorized or forbidden, show a visible permission failure state.

If the backend returns not found, show a visible match-not-found state.

If the backend returns incomplete or invalid contract data, show a visible contract failure state.

Do not recover from these failures by manufacturing frontend truth.

Do not hide backend failures behind sample content.

Do not show fake evidence during failure states.

Placeholder Rule

Placeholders are allowed only as explicit bounded UI placeholders.

A placeholder must clearly say that backend data is unavailable or not yet connected.

A placeholder must never appear as real evidence.

A placeholder must never appear as real match truth.

A placeholder must never appear as real audit state.

A placeholder must never appear as real export readiness.

A placeholder must not be used to claim Scenario 15 readiness.

Scenario 15 Boundary

Do not mark Scenario 15 as complete.

Do not state that the Match Detail flow is live-validated.

Do not state that Base44 wiring is complete unless a later implementation mini-epic explicitly validates it.

This prompt prepares frontend instructions only.

Acceptance Criteria For Later Wiring

The later wiring step is acceptable only if:

Base44 requests backend-provided Match Detail data
Base44 renders backend fields display-only
Base44 does not create evidence
Base44 does not merge evidence
Base44 does not calculate confidence
Base44 does not synthesize match truth
Base44 does not infer permission state
Base44 does not infer export readiness
Base44 shows visible backend failure states
Base44 shows visible permission failure states
Base44 shows visible contract failure states
Base44 uses placeholders only as explicit non-truth placeholders
Scenario 15 remains incomplete until separately validated
END BASE44 PROMPT PACKAGE
Governance Boundary

This mini-epic creates a paste-ready Base44 prompt package only.

It does not authorize using the prompt inside Base44 yet.

It does not authorize live frontend binding.

It does not authorize endpoint execution.

It does not authorize Base44-generated evidence.

It does not authorize Base44-generated truth.

It does not authorize Scenario 15 completion.

Acceptance Checks

This document is acceptable only if it confirms:

the package is derived from the controlled 33.13.M boundary
the package is paste-ready but not yet authorized for live use
the backend remains the only source of truth
Base44 remains display-only
frontend evidence generation is forbidden
frontend evidence merging is forbidden
frontend confidence calculation is forbidden
frontend truth synthesis is forbidden
frontend fallback truth is forbidden
frontend permission inference is forbidden
frontend export readiness inference is forbidden
failure-state rendering rules are included
placeholder restrictions are included
no live Base44 wiring occurs
no Scenario 15 completion claim is made
Closure Statement

Mini-EPIC 33.13.N prepares a paste-ready Base44 Match Detail instruction package only.

It is a controlled prompt package boundary, not an implementation step.

The prompt package may be used only by a later authorized Base44 wiring mini-epic.

No Base44 live wiring occurred.

No live UI was modified.

No endpoint was executed.

No Scenario 15 completion claim was made.

No frontend-generated evidence was authorized.

No frontend truth synthesis was authorized.
