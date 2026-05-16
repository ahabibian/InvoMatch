
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
