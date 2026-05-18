
Mini-EPIC 33.1 — Pilot UI Product Architecture & FTL Surface Definition

Mini-EPIC 33.1 establishes the architecture foundation required before any direct Pilot UI implementation in Base44 begins.

This mini-epic defines how EPIC 33 will remain product-valid, backend-authoritative, and migration-safe while exposing the Financial Truth Layer through a pilot-facing interface.

The first deliverable completed under this mini-epic is:

PILOT_UI_PRODUCT_ARCHITECTURE.md

This document formally establishes that:

Base44 is a Pilot UI Layer only
the backend remains the sole source of product truth
the UI may display backend truth and submit operator intent, but may not create financial truth
matching logic, finalization logic, tenant rules, audit trail generation, export logic, and core persistence remain strictly backend-owned
read flows and write flows must be separated by explicit backend-authoritative contracts
tenant/user context, trust states, error states, and permission states must be presented deliberately in the UI
the Pilot UI must visibly reveal the Financial Truth Layer lifecycle from raw intake through finalized truth and export readiness

Mini-EPIC 33.1 does not authorize actual Base44 page construction, API wiring, backend redesign, Scenario 15 execution, regression reruns, or any production release behavior.

Its role is to ensure that EPIC 33 becomes a coherent product demonstration layer rather than a loose collection of disconnected UI screens.

Mini-EPIC 33.1 Deliverable Added — Pilot Screen Inventory and Responsibility Map

The following architecture deliverable has now been added:

PILOT_SCREEN_INVENTORY_AND_RESPONSIBILITY_MAP.md

This document defines the full required Pilot UI screen set for EPIC 33 and assigns an explicit product responsibility to each screen.

It establishes:

the core screen inventory for the Pilot UI
each screen's product purpose
each screen's backend data dependency
permitted operator actions
forbidden frontend responsibilities
screen-level exposure of the Financial Truth Layer
the operator journey from intake through review, correction, finalized truth, and export readiness

This deliverable reinforces that EPIC 33 must be implemented as a coherent product flow, not as an ad hoc collection of pages.

Mini-EPIC 33.1 Deliverable Added — FTL Surface Definition

The following architecture deliverable has now been added:

FTL_SURFACE_DEFINITION.md

This document defines how the Financial Truth Layer must become visibly understandable through the Pilot UI.

It establishes:

the visible lifecycle from raw financial input to finalized truth
the distinction between raw input, normalized processing, proposed system interpretation, evidence, human review, finalized truth, lineage, audit linkage, and export readiness
the UI surfaces responsible for exposing each Financial Truth Layer stage
the backend-derived truth required for each visible surface
forbidden frontend shortcuts that would weaken or falsify the FTL narrative
the standard that the Pilot UI must reveal FTL as a controlled product lifecycle, not as a vague internal term

This deliverable ensures that EPIC 33 can later implement Pilot UI screens that make the Financial Truth Layer concrete, inspectable, and product-visible.

Mini-EPIC 33.1 Deliverable Added — Initial API-to-Screen Mapping Framework

The following architecture deliverable has now been added:

INITIAL_API_TO_SCREEN_MAPPING_FRAMEWORK.md

This document defines the initial backend API contract framework required to support the Pilot UI screens without transferring business-rule ownership to Base44.

It establishes:

the required read API categories for each Pilot UI surface
the required write/action API categories for governed operator decision flows
the separation between screen reads and intent-based backend actions
backend-owned semantic states such as review status, finalization state, export readiness, blocker reasons, trust states, and permitted actions
frontend derivation prohibitions that prevent Base44 from reconstructing product truth
shared response-state requirements for ready, empty, blocked, degraded, failed, permission-denied, and stale/conflict conditions
the design balance that backend contracts should return product semantics without becoming presentation-coupled

This deliverable ensures that later EPIC 33 implementation can define exact endpoint routes and payloads on top of a clear contract architecture rather than inventing API behavior page-by-page.

Mini-EPIC 33.1 Deliverable Added — Operator Workflow Definition

The following architecture deliverable has now been added:

OPERATOR_WORKFLOW_DEFINITION.md

This document defines the end-to-end operator journey that the Pilot UI must support.

It establishes:

the core operator flow from dashboard visibility through review, evidence inspection, governed human decision, finalized truth, and export readiness visibility
the role of each Pilot UI screen within that workflow
required backend truth at each stage
transition paths between workflow stages
blocked, permission-denied, unresolved, and evidence-incomplete branches
mandatory backend state refresh after operator action
the distinction between operator intent submission and backend-owned truth mutation
alignment between the Pilot UI workflow and the Financial Truth Layer lifecycle

This deliverable ensures that EPIC 33 implementation proceeds from a product-valid operational journey rather than from disconnected page construction.

Mini-EPIC 33.1 Deliverable Added — Trust, Error, and Permission Presentation Rules

The following architecture deliverable has now been added:

TRUST_ERROR_AND_PERMISSION_PRESENTATION_RULES.md

This document defines how the Pilot UI must present backend-derived uncertainty, workflow blockers, operational failures, degraded states, and permission restrictions without exposing raw internals or misleading the operator.

It establishes:

the trust-state categories required across the Pilot UI
presentation rules for validation errors, permission denials, export-not-ready conditions, failed runs, degraded health, recovery in progress, missing evidence, unresolved review state, stale/conflict state, and unavailable resources
user-safe message expectations that explain what happened, what is affected, whether the operator can continue, and what valid next step exists
global versus local trust presentation boundaries
screen-level trust/error expectations for dashboard, intake, queue, detail, correction, finalized truth, and tenant/user context surfaces
forbidden frontend patterns such as optimistic truth mutation, raw backend error display, hidden blockers, and false readiness claims

This deliverable ensures that EPIC 33 demonstrates a trust-preserving Financial Truth Layer product rather than a superficial happy-path-only interface.

Mini-EPIC 33.1 Deliverable Added — Pilot Demo Narrative

The following architecture deliverable has now been added:

PILOT_DEMO_NARRATIVE.md

This document defines the official product demonstration story for the EPIC 33 Pilot UI.

It establishes:

the canonical demo sequence from intake context through review queue, evidence inspection, governed human decision, backend-confirmed state refresh, finalized truth record, and export readiness visibility
the exact product meaning that each screen contributes to the demonstration
the preferred main demo path and a valid blocker-focused alternative path
the expected audience takeaway at each stage
the language discipline required to avoid overstating automation or falsely implying completed export capability
the core narrative that the Pilot UI must demonstrate Financial Truth Layer value through visible, traceable product flow rather than static screen polish

This deliverable ensures that later EPIC 33 implementation and demo execution remain anchored to a fixed, product-valid Financial Truth Layer story.

Mini-EPIC 33.1 — Architecture Foundation Completed and Ready for Closure

Mini-EPIC 33.1 has now completed its full architecture-definition scope for the EPIC 33 Pilot UI and Financial Truth Layer demonstration foundation.

The following deliverables are complete:

PILOT_UI_PRODUCT_ARCHITECTURE.md
PILOT_SCREEN_INVENTORY_AND_RESPONSIBILITY_MAP.md
FTL_SURFACE_DEFINITION.md
INITIAL_API_TO_SCREEN_MAPPING_FRAMEWORK.md
OPERATOR_WORKFLOW_DEFINITION.md
TRUST_ERROR_AND_PERMISSION_PRESENTATION_RULES.md
PILOT_DEMO_NARRATIVE.md

Together, these documents formally establish:

Base44 as a Pilot UI Layer only
backend as the sole source of product truth
the fixed responsibility boundary between UI and backend
the Pilot UI screen inventory and role of each surface
the Financial Truth Layer lifecycle as a visibly demonstrable product flow
the initial API-to-screen mapping framework
the governed operator workflow from dashboard to finalized truth and export readiness
the trust, error, blocker, and permission presentation rules
the canonical Pilot Demo Narrative for later implementation and demonstration

Mini-EPIC 33.1 remains strictly definition-only.

It does not:

build actual Base44 pages
implement Base44 API wiring
implement backend endpoint changes
redesign matching or finalization logic
implement export
execute export
execute Scenario 15
rerun regression scenarios
authorize deployment, release, or public artifact publication

With these deliverables complete, Mini-EPIC 33.1 is ready for formal closure through:

MINI_EPIC_33_1_CLOSURE.md
---

## Mini-EPIC 33.2 — Pilot UI Implementation Planning & Base44 Construction Boundary

Mini-EPIC 33.2 converts the architecture foundation established in Mini-EPIC 33.1 into a controlled Pilot UI implementation planning boundary.

Mini-EPIC 33.1 defined:

- Base44 as the Pilot UI Layer only;
- backend ownership of product truth;
- approved Pilot screen responsibilities;
- Financial Truth Layer presentation surfaces;
- initial API-to-screen mapping posture;
- operator workflow;
- trust, error, blocker, and permission presentation rules;
- the canonical Pilot Demo Narrative.

Mini-EPIC 33.2 does not build actual Pilot UI pages.

Instead, it defines how later Base44 construction must proceed without deviating from the architecture already approved in Mini-EPIC 33.1.

The following deliverables are complete:

- PILOT_UI_IMPLEMENTATION_STRATEGY.md
- BASE44_CONSTRUCTION_BOUNDARY.md
- PILOT_SCREEN_CONSTRUCTION_SEQUENCE.md
- FIRST_PILOT_SLICE_DEFINITION.md
- SCREEN_READINESS_CLASSIFICATION.md
- BACKEND_DEPENDENCY_AND_PLACEHOLDER_DISCIPLINE.md
- SCREEN_CONSTRUCTION_ACCEPTANCE_CRITERIA.md
- PILOT_UI_IMPLEMENTATION_PHASE_BOUNDARIES.md

Together, these documents formally establish:

- the staged implementation strategy for controlled Pilot UI construction;
- the non-negotiable Base44 construction boundary;
- the official screen construction sequence for later EPIC 33 implementation;
- the First Pilot Slice as a review-centered, product-valid demonstration path;
- the readiness classification of each Pilot UI screen and surface;
- the backend dependency and placeholder discipline required before backend binding;
- the acceptance criteria that later screen construction must satisfy;
- the implementation phase boundaries from shell construction through backend binding and demo stabilization.

Mini-EPIC 33.2 explicitly preserves the central architectural principle:

> Implementation must follow architecture, not reinterpret it.

Mini-EPIC 33.2 remains strictly planning-boundary work.

It does not:

- build actual Base44 pages;
- write direct Base44 page-generation prompts;
- execute UI implementation phases;
- connect live Base44 screens to backend APIs;
- redesign backend contracts;
- implement matching logic;
- implement correction execution;
- implement finalization execution;
- implement export readiness behavior;
- execute export;
- execute Scenario 15;
- rerun regression scenarios;
- authorize deployment, release, or public artifact publication.

With these deliverables complete, Mini-EPIC 33.2 is ready for formal closure through:

- MINI_EPIC_33_2_CLOSURE.md

Mini-EPIC 33.3 — Pilot UI Phase A Construction Authorization & Base44 Shell Execution Boundary

Mini-EPIC 33.3 begins the first controlled implementation step of EPIC 33 after the planning-boundary closure of Mini-EPIC 33.2.

This Mini-EPIC formally authorizes entry into:

Phase A — Base44 Shell and Navigation Foundation

Mini-EPIC 33.3 does not authorize the full Pilot UI workflow.

It authorizes only the controlled construction foundation required before later workflow screens may be implemented.

The initial Mini-EPIC 33.3 governance deliverables are:

PHASE_A_CONSTRUCTION_AUTHORIZATION.md
PHASE_A_EXECUTION_BOUNDARY.md
BASE44_PHASE_A_PROMPTING_BOUNDARY.md
PHASE_A_TARGET_SHELL_ARTIFACT_DEFINITION.md
PHASE_A_CONSTRUCTION_ACCEPTANCE_CRITERIA.md

Together, these documents establish:

the formal authorization to begin Phase A construction;
the exact allowed and prohibited work inside the Phase A boundary;
the prompting discipline required before giving Base44 a real Phase A construction instruction;
the target Base44 shell artifact that Phase A must produce;
the acceptance criteria that the actual shell output must satisfy before Mini-EPIC 33.3 may proceed toward closure.

Mini-EPIC 33.3 preserves the central implementation principle:

Phase A may establish the Pilot UI frame, but it may not begin the Pilot workflow itself.

Accordingly, Mini-EPIC 33.3 does not yet:

complete actual Base44 shell construction review;
record a completed Base44 execution outcome;
construct Pilot Dashboard behavior;
construct Reconciliation Review Queue behavior;
construct Match Detail / Evidence View behavior;
construct Human Correction behavior;
construct Finalized Truth Record behavior;
construct Export Readiness behavior;
construct Intake Workspace behavior;
bind live backend APIs;
introduce frontend-owned product truth;
execute Scenario 15;
rerun regression scenarios;
authorize deployment, release, or public artifact publication.

The remaining Mini-EPIC 33.3 deliverables will only become valid after actual Base44 construction and review occur:

PHASE_A_BASE44_SHELL_CONSTRUCTION_EXECUTION_RECORD.md
PHASE_A_POST_CONSTRUCTION_REVIEW.md
MINI_EPIC_33_3_CLOSURE.md

Mini-EPIC 33.3 — Phase A Base44 Shell Construction Executed, Reviewed, and Closed

Mini-EPIC 33.3 has now completed the first controlled real implementation step of EPIC 33:

Phase A — Base44 Shell and Navigation Foundation

The following execution and closure deliverables have now been completed:

PHASE_A_BASE44_SHELL_CONSTRUCTION_EXECUTION_RECORD.md
PHASE_A_POST_CONSTRUCTION_REVIEW.md
MINI_EPIC_33_3_CLOSURE.md

Actual Base44 construction was performed under the Phase A prompting boundary and produced a real Pilot UI shell foundation.

The generated artifact established:

InvoMatch Pilot application shell;
persistent navigation;
approved future Pilot area navigation slots;
shared layout frame;
main content canvas;
visible reserved tenant/user context area.

The initial artifact was reviewed as:

Accepted with Controlled Correction

A narrow ambiguity involving the visible default title Pilot Dashboard was corrected so that the final default shell surface now reads:

Pilot UI Shell

The final corrected artifact was reviewed as:

Accepted

Mini-EPIC 33.3 confirms that:

Phase A construction has been executed;
the final shell remains inside the authorized shell/navigation boundary;
no Pilot workflow screen has been prematurely implemented;
no fake product truth has been introduced;
no backend API binding has occurred;
later Pilot workflow construction remains reserved for later EPIC 33 phases.

Mini-EPIC 33.3 is therefore formally closed through:

MINI_EPIC_33_3_CLOSURE.md

Mini-EPIC 33.4 — Pilot UI Phase B Core Review Path Construction Authorization & Base44 Review-Surface Execution Boundary

Mini-EPIC 33.4 advances EPIC 33 from the accepted Phase A shell foundation into the second controlled implementation step:

Phase B — Core Review Path Construction

Mini-EPIC 33.4 formally authorizes and executes the first visible workflow-adjacent Pilot UI surfaces while preserving the core EPIC 33 doctrine:

Phase B may construct the visible review path, but it may not create review truth, correction authority, or downstream financial outcomes.

The following Mini-EPIC 33.4 governance and execution deliverables are now complete:

PHASE_B_CONSTRUCTION_AUTHORIZATION.md
PHASE_B_EXECUTION_BOUNDARY.md
BASE44_PHASE_B_PROMPTING_BOUNDARY.md
PHASE_B_TARGET_CORE_REVIEW_PATH_ARTIFACT_DEFINITION.md
PHASE_B_CONSTRUCTION_ACCEPTANCE_CRITERIA.md
PHASE_B_BASE44_CORE_REVIEW_PATH_CONSTRUCTION_EXECUTION_RECORD.md
PHASE_B_POST_CONSTRUCTION_REVIEW.md

Together, these documents establish and record:

formal authorization to enter Phase B after successful closure of Phase A;
the exact allowed and prohibited construction scope for the Core Review Path;
the Base44 prompting discipline required to avoid fake metrics, fake records, fake evidence semantics, and later-phase leakage;
the target Core Review Path artifact expected from Phase B;
the acceptance criteria required before Phase B output may be accepted;
the actual Base44 Phase B construction execution;
the controlled correction steps applied during review;
the final post-construction review decision.

Actual Base44 Phase B construction was performed inside the previously accepted Phase A Pilot UI shell.

The constructed Phase B artifact now includes:

visible presentation-only Tenant / User Context surfaces;
Pilot Dashboard as a restrained review-path entry surface;
Reconciliation Review Queue as a structural, non-operational review surface;
Match Detail / Evidence View as a structural inspection-layout surface;
recognizable navigation continuity:
Dashboard → Review Queue;
Review Queue → Match Detail / Evidence View.

The Pilot Dashboard was accepted because it:

introduces the Phase B review path;
provides orientation without pretending to expose live operational metrics;
directs the user toward the Review Queue;
does not contain fake KPIs, fake counts, or fake reconciliation outcomes.

The Reconciliation Review Queue was initially reviewed as structurally valid but received a controlled semantic correction.

The correction removed avoidable workflow-state ambiguity by eliminating:

a Status control;
STATUS and ASSIGNED table columns.

The final queue posture now uses neutral structural labels:

Review Item;
Source Context;
Counterpart Context;
Period Context;
Evidence Entry.

The final Review Queue remains:

empty;
explicitly not backend-bound;
free of fake financial records;
free of fake review statuses;
free of fake operational assignments;
free of decision actions.

The Match Detail / Evidence View was also accepted after a controlled semantic-cleanup correction.

The final surface preserves four structural review-inspection zones:

Source Record Zone;
System Interpretation Zone;
Evidence Comparison Zone;
Review Context Zone.

The correction removed over-specific later-phase semantic labels and replaced them with neutral Phase B placeholders, ensuring that the Evidence View:

remains structural;
remains not yet bound;
does not imply active scoring;
does not imply workflow assignment;
does not imply audit-state completion;
does not fabricate evidence interpretation or backend reasoning.

The final Base44 Phase B output was reviewed as:

Accepted

Mini-EPIC 33.4 confirms that:

the accepted Phase A shell was preserved;
the Core Review Path was constructed visibly and coherently;
the Pilot Dashboard, Review Queue, and Match Detail / Evidence View now exist as controlled Phase B surfaces;
no fake dashboard metrics were introduced;
no fake queue records were introduced;
no fake evidence verdicts or confidence claims were introduced;
no Human Correction behavior was implemented;
no Finalized Truth Record surface was implemented;
no Export Readiness surface was implemented;
no Intake Workspace behavior was implemented;
no backend API binding occurred;
no live-data integration occurred;
no frontend-manufactured product truth entered the Pilot UI.

Mini-EPIC 33.4 does not authorize Phase C automatically.

It confirms only that EPIC 33 has successfully completed the controlled Phase B Core Review Path construction boundary and is now ready to proceed toward formal Mini-EPIC 33.4 closure through:

MINI_EPIC_33_4_CLOSURE.md
