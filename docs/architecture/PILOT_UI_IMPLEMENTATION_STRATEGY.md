# Pilot UI Implementation Strategy

## Mini-EPIC 33.2 — Pilot UI Implementation Planning & Base44 Construction Boundary

## 1. Purpose

This document defines the controlled implementation strategy for constructing the InvoMatch Pilot UI in Base44 during EPIC 33.

Mini-EPIC 33.1 established the architecture foundation of the Pilot UI:

- Base44 is limited to the Pilot UI Layer.
- The backend remains the only source of product truth.
- The core Pilot UI screen inventory is defined.
- Financial Truth Layer presentation surfaces are identified.
- Operator workflow and Pilot Demo Narrative are formalized.

Mini-EPIC 33.2 does not begin actual UI construction.

Instead, it defines how implementation must proceed so that Base44 construction follows the approved architecture rather than improvising, expanding scope informally, or reinterpreting product boundaries.

The purpose of this strategy is to ensure that the Pilot UI is built:

- in a controlled sequence;
- around a coherent operator workflow;
- with strict frontend/backend responsibility boundaries;
- without creating fake product truth in the UI;
- in a form that progressively supports the official EPIC 33 Pilot Demo Narrative.

---

## 2. Core Implementation Principle

> Implementation must follow architecture, not reinterpret it.

The Base44 Pilot UI must be constructed as an execution of the architecture established in Mini-EPIC 33.1.

Base44 implementation is not permitted to:

- redefine workflow logic;
- invent frontend-owned business meaning;
- simulate backend acceptance as truth;
- derive financial truth independently;
- collapse placeholder states into product claims.

The implementation strategy must therefore prioritize:

workflow coherence;
truthful state presentation;
visible demo value;
dependency-aware construction;
strict deferral of unsupported functionality.

---

## 3. Why Pilot UI Implementation Must Be Staged

A staged implementation model is required because the Pilot UI includes screens with different levels of readiness, dependency, and product-criticality.

Attempting to construct all screens at once would create several problems.

### 3.1 Loss of Product Priority

Without a staged plan, UI work may follow what is easiest to build visually rather than what is most important to demonstrate the product workflow.

### 3.2 Scope Inflation

Early Pilot UI construction can become overloaded with secondary screens, complete visual systems, or premature edge-case paths before the primary workflow is visible and reviewable.

### 3.3 Backend Ambiguity

Some screens can be built as structural shells immediately.

Others depend on confirmed backend response semantics and must not be treated as product-complete until those semantics are available.

### 3.4 Demo Narrative Drift

EPIC 33 is not merely about creating pages.

It is about making the Financial Truth Layer demonstration path visible and defensible.

The construction order must make that path observable as early as possible.

---

## 4. Strategic Goal of the First Implementation Cycle

The first implementation cycle must aim to produce a coherent Pilot UI slice, not a scattered set of screens.

The target is not maximum page count.

The target is:

> the smallest controlled UI path that visibly communicates how InvoMatch moves from operational review to evidence-backed financial truth presentation.

This first implementation cycle must support, at minimum, the user's ability to conceptually understand:

- where the operator begins;
- how review work is surfaced;
- how one item is inspected;
- how the UI presents evidence and status without inventing truth;
- how correction and finalized truth surfaces fit into the wider Pilot flow.

---

## 5. Strategic Construction Priorities

Pilot UI construction should follow the priority order below.

### Priority 1 — Establish the Product Frame

Before individual workflows are built, the Pilot UI needs a stable application frame:

- global shell;
- navigation;
- page hierarchy;
- shared layout logic;
- tenant/user context surface position;
- common display area patterns.

This ensures later screens are placed into a coherent product structure rather than built as isolated mockups.

### Priority 2 — Make the Core Review Path Visible

The first workflow-facing construction should focus on the review journey:

- Pilot Dashboard;
- Reconciliation Review Queue;
- Match Detail / Evidence View.

This is the center of the Pilot Demo Narrative and should appear before lower-priority surfaces.

### Priority 3 — Introduce Controlled Human Action Surfaces

Once review visibility exists, the UI should present the human intervention layer:

- Human Correction Screen;
- correction action areas;
- correction state presentation;
- backend-bound action points or explicitly labeled mock-bound placeholders.

This should be constructed only in ways that preserve the rule that the UI does not determine acceptance truth.

### Priority 4 — Surface Financial Truth Outcomes

The Pilot UI must eventually show the downstream consequence of governed operator review:

- Finalized Truth Record;
- Export Readiness presentation;
- audit-oriented state visibility.

These screens should be positioned as display surfaces of backend-owned truth, not as frontend-calculated completion states.

### Priority 5 — Complete Supporting Entry and Trust States

After the core review-to-truth path is established, the Pilot UI can be extended with:

- Intake Workspace;
- trust/error/permission presentation patterns;
- loading/empty/blocked/unavailable states;
- broader visual consistency.

These are important, but they should not outrank the core demonstration path.

---

## 6. Recommended Controlled Construction Sequence

The Pilot UI should be constructed in the following staged sequence.

### Stage 1 — Pilot Shell and Navigation Foundation

Build the structural product frame:

- shared layout;
- navigation model;
- top-level screen routing;
- location for tenant/user context;
- basic consistent page title/header behavior.

### Stage 2 — Operator Entry and Overview

Construct:

- Tenant / User Context Surface;
- Pilot Dashboard.

Purpose:

- establish who is acting;
- establish the current operational view;
- prepare the transition into review work.

### Stage 3 — Core Review Workflow

Construct:

- Reconciliation Review Queue;
- Match Detail / Evidence View.

Purpose:

- make the review path visible;
- show how operational items are examined;
- present evidence without allowing the UI to define financial truth.

### Stage 4 — Human Correction Workflow

Construct:

- Human Correction Screen;
- controlled correction form / decision surface;
- response-state placeholders where necessary.

Purpose:

- show how the operator can intervene;
- maintain a strict backend-dependent action model;
- avoid simulating backend acceptance as a UI-owned fact.

### Stage 5 — Financial Truth Presentation

Construct:

- Finalized Truth Record;
- Export Readiness display surface.

Purpose:

- show the result of backend-trusted state progression;
- demonstrate the Financial Truth Layer concept visibly;
- avoid frontend derivation of finalized or export-ready status.

### Stage 6 — Intake and Shared Trust-State Completion

Construct:

- Intake Workspace;
- error presentation states;
- permission-denied presentation;
- not-ready / blocked / unavailable states;
- shared trust communication patterns.

Purpose:

- complete the broader Pilot experience;
- reinforce enterprise-grade trust and clarity;
- prepare the UI for later backend binding and demo stabilization.

---

## 7. Definition of the First Usable Pilot Slice

The first usable Pilot UI slice should be a review-centered demonstration slice.

### 7.1 Included in the First Slice

The first slice should include:

Pilot Shell / Navigation;
Tenant / User Context Surface;
Pilot Dashboard;
Reconciliation Review Queue;
Match Detail / Evidence View;
Human Correction Screen, at least as a controlled backend-bound or explicitly placeholder-labeled action surface;
Finalized Truth / Export Readiness display shell, at least enough to communicate where governed backend truth will be surfaced.

### 7.2 Excluded from the First Slice

The first slice should not require:

- full Intake Workspace implementation;
- complete visual design refinement;
- complete trust/error state library;
- live backend API connectivity;
- fully executable correction persistence;
- real export flow execution;
- production-grade edge-case handling.

These elements remain important, but they should not delay the first coherent Pilot UI slice.

---

## 8. Foundation Screens vs. Dependent Screens

### 8.1 Foundation Screens

These screens create the structural and narrative basis of the Pilot UI:

- Pilot Shell / Navigation Frame;
- Tenant / User Context Surface;
- Pilot Dashboard;
- Reconciliation Review Queue.

They should be implemented first because later screens either branch from them or derive their demo meaning from them.

### 8.2 Workflow Detail Screens

These screens deepen the operator review path:

- Match Detail / Evidence View;
- Human Correction Screen.

They depend on the review queue and should be implemented immediately after the primary queue structure is stable.

### 8.3 Outcome / Truth Presentation Screens

These screens communicate the result of backend-governed workflow progression:

- Finalized Truth Record;
- Export Readiness Surface.

They are critical to EPIC 33's narrative, but their content must remain contract-aware and must not be prematurely overbuilt.

### 8.4 Supporting / Completion Screens

These screens complete the wider Pilot experience:

- Intake Workspace;
- Shared Trust / Error / Permission Presentation Layer.

They should come after the core review-to-truth path is visible.

---

## 9. Strategy for Placeholder Use During Implementation

Controlled placeholders may be used only when they help construct UI structure before backend contracts are fully connected.

Placeholder usage is acceptable only when:

- the placeholder is explicitly documented;
- the placeholder does not assert product truth;
- the UI clearly distinguishes static/demo data from backend-derived state;
- the placeholder represents a future backend binding point, not a frontend-owned substitute.

Examples of acceptable placeholder use:

- sample review queue rows;
- structured detail-panel content shaped after an expected backend contract;
- disabled or labeled action controls pending backend binding;
- export readiness display sections marked as provisional UI surfaces.

Examples of unacceptable placeholder use:

- showing accepted states as though real backend acceptance occurred;
- presenting fake finalization as complete;
- fabricating tenant permissions as product state;
- calculating review outcomes in Base44 UI logic;
- presenting a polished static state as if it were a working product workflow.

---

## 10. Strategy for Backend-Dependent Surfaces

Each screen should be categorized during implementation planning according to its dependency profile.

### 10.1 Constructable Immediately

Screens that can be built now with clear architecture and low semantic risk:

- Pilot Shell;
- Navigation Frame;
- Dashboard structure;
- Review Queue shell;
- Match Detail layout structure.

### 10.2 Constructable as Controlled Shells

Screens that may be structurally created but cannot be declared product-complete without backend semantics:

- Human Correction Screen;
- Finalized Truth Record;
- Export Readiness Surface;
- Intake Workspace.

### 10.3 Backend-Contract-Dependent

Parts that require confirmed contract or response-state definitions before they can be treated as functionally valid:

- correction submission result states;
- finalized record status meanings;
- export readiness determination;
- permission logic;
- tenant-scoped operational visibility;
- exact backend-shaped reason codes or explanation models.

---

## 11. Pilot Demo Narrative Alignment

The implementation strategy must reinforce the Pilot Demo Narrative formalized in Mini-EPIC 33.1.

Therefore, screen construction must be evaluated against one central test:

> Does this implementation step make the official Pilot Demo Narrative more visibly demonstrable?

The correct construction order is not the one that produces the largest number of screens.

It is the one that most quickly exposes the product's core narrative:

operator enters a tenant-aware Pilot UI;
operational state is summarized;
a review item is selected;
evidence and reasoning are displayed;
human correction can be represented without falsifying backend truth;
finalized truth and readiness become visible as governed backend-owned outcomes.

Any construction work that does not strengthen this path should be deferred unless required for structural coherence.

---

## 12. Implementation Strategy Rules

The following rules govern all later Pilot UI construction work in EPIC 33.

### Rule 1 — Build by Workflow Importance, Not Visual Convenience

Screens are prioritized according to product narrative and dependency order, not ease of mockup generation.

### Rule 2 — Frontend Must Never Manufacture Truth

The UI may display truth, request truth, and host actions that lead toward truth.

It may not define truth itself.

### Rule 3 — Placeholder Use Must Be Explicit and Temporary

No placeholder may silently become a product claim.

### Rule 4 — Every Screen Must Have a Role in the Pilot Story

Screens without a clear purpose in the Pilot Demo Narrative should not enter the first implementation slice.

### Rule 5 — Backend Binding Points Must Be Designed Early

Even where live integration is deferred, the UI must be shaped so later backend binding does not require architectural reversal.

### Rule 6 — Implementation Must Remain Migration-Safe

Base44 should accelerate UI construction, not trap the product in a frontend-only logic model that cannot migrate cleanly later.

---

## 13. Strategic Non-Goals

This implementation strategy does not authorize:

- actual Base44 page creation;
- Base44 prompt drafting;
- direct UI generation;
- live API integration;
- backend endpoint redesign;
- visual system finalization;
- frontend-owned decision logic;
- implementation of matching, finalization, or export truth;
- regression reruns;
- Scenario 15 execution;
- deployment or release behavior.

Those actions remain outside the scope of Mini-EPIC 33.2.

---

## 14. Strategy Outcome

At the conclusion of this planning stage, EPIC 33 should have a clear answer to:

- what gets built first;
- what gets built later;
- what remains shell-only;
- what must wait for backend contract confirmation;
- how the first Pilot UI slice should look conceptually;
- how Base44 implementation remains faithful to the architecture of Mini-EPIC 33.1.

This strategy establishes the required bridge between:

> Pilot UI Architecture Foundation
> and
> Controlled Base44 Pilot UI Construction

---

## 15. Closing Principle

Mini-EPIC 33.2 does not build the Pilot UI.

It ensures that when the Pilot UI is built, it is built:

- in the correct order;
- for the correct reasons;
- with the correct truth boundaries;
- around the correct operator workflow;
- in service of the correct EPIC 33 demonstration narrative.

Without this planning discipline, Base44 construction risks becoming a collection of attractive but weakly governed screens.

With this strategy in place, EPIC 33 can move toward implementation without sacrificing architectural control.