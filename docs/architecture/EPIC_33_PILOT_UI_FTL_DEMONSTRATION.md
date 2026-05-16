
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
