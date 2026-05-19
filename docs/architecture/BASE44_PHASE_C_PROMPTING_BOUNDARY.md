
Base44 Phase C Prompting Boundary
Purpose

This document defines the mandatory prompting discipline for all Base44 construction work performed under:

Mini-EPIC 33.5 — Pilot UI Phase C Human Correction & Financial Truth Outcome Surface Construction Authorization and Base44 Controlled Review-to-Truth Execution Boundary

Phase C is the first EPIC 33 construction phase that introduces:

human correction posture
downstream finalized-truth visibility
downstream export-readiness framing

Because these concepts are easily misrepresented by UI generators, Base44 prompting must be unusually strict.

The goal is not to make the UI look operational.

The goal is to construct an honest, bounded, product-valid narrative surface that shows where later backend-governed outcomes will appear.

Core Prompting Principle

Base44 may construct Phase C presentation surfaces, but it must not invent, imply, or simulate correction outcomes, finalized financial truth, export readiness, or backend-confirmed product state.

Every prompt used in Mini-EPIC 33.5 must preserve this principle.

Global Phase C Prompting Rules

Every Base44 prompt for Phase C must explicitly instruct the following:

Preserve the existing approved pilot shell and Phase B review path.
Extend the visible workflow only through:
Match Detail / Evidence View
Human Correction
Finalized Truth Record
Export Readiness Surface
Treat all Phase C surfaces as:
structural
bounded
product-valid
non-operational
non-backend-bound
State clearly in the UI that real product confirmation depends on later backend integration.
Avoid any fake success state, fake resolved state, fake finalized state, or fake readiness state.
Avoid inserting plausible business data that could be mistaken for real product truth.
Avoid operational buttons unless they are explicitly non-operational explanatory placeholders.
Do not introduce backend binding, API simulation, persistence, or frontend-manufactured workflow outcomes.
Do not leak into Phase D or Phase E scope.
Keep wording precise, honest, and restrained.
Prompting Boundary for Human Correction Screen
Human Correction Must Be Prompted As

A bounded review-step surface showing where a reviewer will later prepare and submit a correction once backend-supported correction flow exists.

Prompts may request:

correction-entry layout
grouped fields or reserved correction areas
explanatory text about future backend-backed correction handling
provisional submission region
future result-state placeholder region
continuity from Match Detail / Evidence View
Human Correction Must Not Be Prompted As

An already-operational correction workflow.

Prompts must forbid:

save-success behavior
submitted confirmation
accepted correction state
review resolved state
approved / rejected outcomes
downstream finalized state changes
interactive logic that pretends a correction has been persisted
Prohibited Base44 Interpretations

Base44 must not invent:

“Correction saved”
“Changes submitted”
“Match approved”
“Issue resolved”
“Correction accepted”
“Review completed”
“Truth record updated”

These semantics are disallowed even when used merely as decorative badge text.

Prompting Boundary for Finalized Truth Record Surface
Finalized Truth Must Be Prompted As

A downstream display shell reserved for later backend-confirmed financial truth.

Prompts may request:

future truth summary region
source linkage region
finalized interpretation region
lineage / governance placeholder region
text clarifying that no finalized backend truth is rendered yet
Finalized Truth Must Not Be Prompted As

A populated or semi-populated real truth record.

Prompts must forbid:

concrete financial amounts
vendors
invoice identifiers
approval timestamps
audit-ready badges
finalized status chips
fake matched outputs
any sample data that looks like actual product truth
Prohibited Base44 Interpretations

Base44 must not invent:

“Finalized”
“Approved”
“Audit Ready”
“Confirmed Match”
“Final Amount”
“Verified Vendor”
“Completed Truth Record”

unless such wording appears only inside explanatory text clearly stating that these are future backend-governed concepts, not current UI results.

Prompting Boundary for Export Readiness Surface
Export Readiness Must Be Prompted As

A downstream visibility shell explaining where future backend-confirmed export readiness will be interpreted.

Prompts may request:

readiness overview placeholder
blockers / explanation placeholder
export eligibility placeholder
future handoff region
text clarifying that readiness is not yet calculated or confirmed
Export Readiness Must Not Be Prompted As

A readiness dashboard or export control surface.

Prompts must forbid:

ready / not ready verdicts
available export states
generated files
record counts
blocker-resolution claims
download controls
CSV / file generation actions
operational export buttons
Prohibited Base44 Interpretations

Base44 must not invent:

“Ready to Export”
“Not Ready”
“12 Records Ready”
“All blockers resolved”
“Export Available”
“Download CSV”
“Generate Export”
“Create File”

No such wording may appear as a status, badge, primary CTA, or operational-looking interaction.

Placeholder Discipline

Phase C placeholders must be:

visibly provisional
semantically honest
free from fake business results
clearly tied to future backend-confirmed behavior

Allowed placeholder styles include:

explanatory empty state
reserved section label
future backend result region
bounded note stating that output will appear after later backend integration

Disallowed placeholder styles include:

sample financial records
fake approval states
fake readiness indicators
fake success cards
numeric counters that look live
invented examples rendered as though they belong to the current review item
Button and CTA Discipline

Phase C prompts must be extremely careful with buttons.

Permitted Button Posture

If a button-like UI element is requested, it must be:

explicitly non-operational
clearly labeled as future or unavailable in the current Phase C pilot state
used only to explain workflow placement, never to simulate an executed action
Prohibited Button Posture

Prompts must not request:

active save buttons
active submit buttons
active approve / reject buttons
active resolve buttons
active finalize buttons
active export buttons

The default posture in Phase C should be explanatory region first, buttons only if strictly necessary and explicitly constrained.

Navigation Prompting Discipline

Base44 prompts may extend route continuity only through:

Match Detail / Evidence View → Human Correction → Finalized Truth Record → Export Readiness Surface

Prompts must preserve:

prior Pilot Shell structure
prior Dashboard entry surface
prior Review Queue surface
prior Match Detail / Evidence View surface

Prompts must not create:

detached truth pages
detached export pages
shortcut flows bypassing review
direct dashboard-to-export paths
direct queue-to-finalization paths
operational workflow jumps
No Backend Simulation Rule

Phase C prompts must explicitly forbid Base44 from creating:

fake API responses
simulated successful submissions
local persistence pretending to represent product truth
auto-progressed status transitions
frontend-generated finalization results
frontend-generated readiness results

Backend confirmation belongs to a later authorized phase and must not be imitated in Phase C.

No Phase D or Phase E Leakage Rule
Phase D Must Not Be Prompted

Do not ask Base44 to construct:

Intake Workspace
Shared Trust / Error / Permission completion
later-phase cross-surface stabilization work outside the Phase C scope
Phase E Must Not Be Prompted

Do not ask Base44 to construct:

API binding
live state wiring
backend request handling
backend response rendering
persistence behavior
real data-driven state
Required Review After Every Sensitive Prompt

After each Base44 construction output affecting:

Human Correction
Finalized Truth Record
Export Readiness Surface

the output must be reviewed for:

fake action semantics
fake finalized truth
fake readiness claims
misleading buttons
hidden backend simulation
route continuity errors
Phase D leakage
Phase E leakage

If any of these appear, a correction prompt is required before accepting the output.

Prompting Boundary Conclusion

Mini-EPIC 33.5 Base44 prompting must remain disciplined enough to construct a complete visible review-to-truth narrative while refusing to create the illusion that product truth already exists in the frontend.

The correct Phase C posture is:

show the future governed path, do not fake the governed outcome.
