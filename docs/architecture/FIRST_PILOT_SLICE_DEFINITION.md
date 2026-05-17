# First Pilot Slice Definition

## Mini-EPIC 33.2 — Pilot UI Implementation Planning & Base44 Construction Boundary

## 1. Purpose

This document formally defines the first controlled Pilot UI slice to be constructed later in EPIC 33.

Mini-EPIC 33.1 established the architectural foundation of the Pilot UI, including:

- Base44 as Pilot UI Layer only;
- backend ownership of product truth;
- approved screen inventory;
- Financial Truth Layer presentation surfaces;
- operator workflow;
- official Pilot Demo Narrative.

Mini-EPIC 33.2 now narrows that architecture into the first implementation target.

This document answers one central question:

> What is the smallest controlled Pilot UI slice that is limited enough to build coherently, but complete enough to demonstrate the core InvoMatch review-to-truth narrative?

---

## 2. First Pilot Slice Principle

The first Pilot UI slice must be:

- narrow in scope;
- coherent as a workflow;
- aligned with the official Pilot Demo Narrative;
- faithful to backend-owned truth boundaries;
- sufficient to communicate product direction without pretending to be a complete product.

> The first Pilot slice is not a full Pilot UI release. It is the first product-valid demonstration path.

This means the slice must show a meaningful operator journey, not merely static screens.

At the same time, it must not prematurely claim:

- live backend completion;
- finalized export functionality;
- complete intake coverage;
- full trust/error system completion;
- production-grade interaction depth.

---

## 3. Formal Definition of the First Pilot Slice

The first Pilot UI slice is defined as a review-centered demonstration path that makes the core Financial Truth Layer narrative visibly understandable.

The first slice includes:

1. Pilot Shell / Navigation Frame
2. Tenant / User Context Surface
3. Pilot Dashboard
4. Reconciliation Review Queue
5. Match Detail / Evidence View
6. Human Correction Screen as a bounded action surface
7. Finalized Truth Record as a controlled downstream truth display shell
8. Export Readiness Surface as a controlled downstream readiness display shell

Together, these surfaces must allow the Pilot UI to communicate the following conceptual journey:

Operator enters a tenant-aware Pilot UI
> sees review-oriented operational context
> opens a reconciliation queue
> inspects one item and its evidence
> reaches a bounded correction surface
> sees where backend-owned finalized truth is surfaced
> sees where export readiness is presented without the frontend calculating it

---

## 4. Why This Slice Is the Correct First Implementation Target

### 4.1 It Follows the Product Narrative

The first slice aligns directly with the EPIC 33 Pilot Demo Narrative.

It prioritizes:

- operator review;
- evidence inspection;
- controlled human intervention;
- downstream Financial Truth Layer visibility.

This is more valuable than starting with intake, generic dashboards, or visual polish.

### 4.2 It Avoids Overbuilding

The first slice deliberately excludes broad completion work that would inflate scope before the central Pilot workflow is visible.

It does not attempt to build:

- every possible Pilot screen in a functionally complete state;
- every error state;
- every backend binding;
- every intake flow;
- every final export interaction.

This keeps implementation focused and reviewable.

### 4.3 It Preserves Truth Boundaries

The slice allows Finalized Truth and Export Readiness surfaces to appear only as controlled display shells or backend-dependent presentation surfaces.

It does not allow Base44 to:

- create finalized truth;
- calculate readiness;
- simulate backend acceptance;
- imply product completion where only UI construction exists.

### 4.4 It Enables Early Demo Coherence

The first slice becomes useful early because it can support a coherent walkthrough.

Even before full backend integration, it can demonstrate:

- what the operator sees;
- how the review path is structured;
- where evidence becomes visible;
- where corrections enter;
- where downstream truth surfaces belong.

This is a stronger Pilot direction than a collection of isolated individual pages.

---

## 5. Included Surfaces and Required Slice Role

### 5.1 Pilot Shell / Navigation Frame

Role in first slice:

- provides product frame;
- establishes routing between included screens;
- prevents the slice from becoming disconnected page mockups;
- makes the walkthrough feel like one Pilot UI environment.

Minimum slice expectation:

- stable shared application frame;
- navigation routes for included first-slice screens;
- consistent placement of page-level context.

### 5.2 Tenant / User Context Surface

Role in first slice:

- communicates that operator activity is tenant-aware;
- creates a visible context boundary;
- supports credibility of later tenant-aware backend binding.

Minimum slice expectation:

- visible tenant/user context area;
- explicitly presentation-level only unless backend-bound;
- no frontend-owned tenant enforcement logic.

### 5.3 Pilot Dashboard

Role in first slice:

- acts as the operator's starting point;
- summarizes that review work exists;
- creates a transition into the Reconciliation Review Queue.

Minimum slice expectation:

- review-oriented overview;
- at least one clear route into queue review;
- no analytics-heavy expansion that distracts from the core path.

### 5.4 Reconciliation Review Queue

Role in first slice:

- surfaces work requiring attention;
- becomes the central entry to item-level review;
- makes the operational workload visible.

Minimum slice expectation:

- table or queue structure;
- clear status/reason/action availability layout;
- documented placeholder use where backend data is not yet connected;
- no UI-derived review truth.

### 5.5 Match Detail / Evidence View

Role in first slice:

- exposes the selected reconciliation item;
- displays the evidence context;
- enables understanding of why human review exists.

Minimum slice expectation:

- detail layout tied to a selected queue item conceptually;
- evidence presentation regions;
- room for reason/status display;
- no frontend-derived truth verdict.

### 5.6 Human Correction Screen

Role in first slice:

- demonstrates where bounded human intervention belongs;
- shows that review can lead to corrective operator action;
- preserves the distinction between UI entry and backend-confirmed outcome.

Minimum slice expectation:

- correction-entry structure;
- backend-bound or explicitly placeholder-labeled submission area;
- no simulated authoritative acceptance result;
- no local UI transition falsely implying final product truth.

### 5.7 Finalized Truth Record

Role in first slice:

- communicates where governed finalized truth will be displayed;
- links operator review to downstream trusted record visibility;
- supports the Financial Truth Layer demonstration narrative.

Minimum slice expectation:

- display shell or backend-dependent surface;
- clear separation from review state;
- no UI-generated finalization claim.

### 5.8 Export Readiness Surface

Role in first slice:

- communicates where downstream export readiness is presented;
- demonstrates that export readiness is a distinct backend-owned state;
- completes the review-to-truth-to-readiness narrative.

Minimum slice expectation:

- readiness display shell or backend-dependent surface;
- placeholder readiness labels only if explicitly documented;
- no frontend-calculated readiness logic.

---

## 6. Explicitly Excluded from the First Pilot Slice

The following items are intentionally excluded from the first Pilot slice:

- full Intake Workspace implementation;
- complete file upload / ingestion workflow;
- full trust-state catalog;
- complete error-state implementation;
- full permission-state implementation;
- production-ready design system refinement;
- live backend API integration;
- real correction persistence;
- real finalization execution;
- real export implementation;
- operational reporting or analytics expansion;
- Scenario 15 execution;
- regression reruns;
- deployment or release behavior.

These exclusions are deliberate.

> The first Pilot slice must prove the core review-to-truth narrative before broadening into full Pilot completeness.

---

## 7. Included vs. Excluded Decision Table

| Surface or Capability | Included in First Slice | Required State in First Slice |
|---|---|---|
| Pilot Shell / Navigation | Yes | Structural and navigable |
| Tenant / User Context | Yes | Visible presentation surface |
| Pilot Dashboard | Yes | Review-oriented operator entry |
| Reconciliation Review Queue | Yes | Structured workflow surface |
| Match Detail / Evidence View | Yes | Evidence-oriented inspection surface |
| Human Correction Screen | Yes | Bounded action shell or backend-bound form surface |
| Finalized Truth Record | Yes | Controlled downstream truth display shell |
| Export Readiness Surface | Yes | Controlled readiness display shell |
| Intake Workspace | No | Deferred beyond first slice |
| Full Trust / Error / Permission Layer | No | Deferred beyond first slice |
| Live API Integration | No | Explicitly out of scope |
| Real Export Execution | No | Explicitly out of scope |

---

## 8. Product-Validity Criteria for the First Slice

The first Pilot slice is product-valid only if it satisfies all of the following criteria:

1. It represents a coherent operator path rather than disconnected page shells.
2. It visibly preserves tenant/user context as part of the Pilot experience.
3. It places Reconciliation Review Queue and Match Detail / Evidence View at the center of the slice.
4. It shows Human Correction as a bounded action surface, not as frontend-owned truth mutation.
5. It includes Finalized Truth Record and Export Readiness only in a way that preserves backend ownership of truth.
6. It avoids over-expanding into intake, full trust-state completion, or live backend integration.
7. It supports the official EPIC 33 Pilot Demo Narrative without distorting the architecture of Mini-EPIC 33.1.
8. It remains compatible with later staged implementation and backend binding.

---

## 9. First Slice Must Not Be Misclassified

The first Pilot slice must not be described as:

- production-ready UI;
- fully integrated Pilot environment;
- finalized export workflow;
- complete correction engine;
- complete tenant-aware security implementation;
- fully backend-connected Financial Truth Layer;
- feature-complete EPIC 33 delivery.

The correct classification is:

> a controlled, product-valid, review-centered first Pilot UI implementation slice.

---

## 10. Relationship to Later EPIC 33 Construction

The first slice creates the implementation foundation for later work, including:

- deeper Base44 page construction;
- screen-level acceptance criteria application;
- placeholder discipline enforcement;
- backend contract binding;
- intake completion;
- trust / error / permission layer completion;
- Pilot Demo stabilization.

Later phases may broaden functionality.

They may not rewrite the first-slice principle retroactively or claim that the first slice already authorized full Pilot implementation.

---

## 11. Out of Scope

This document does not:

- build actual Base44 pages;
- generate direct Base44 prompts;
- execute implementation phases;
- connect live APIs;
- perform backend contract redesign;
- implement matching logic;
- implement finalization logic;
- implement export logic;
- execute Scenario 15;
- rerun regression suites;
- authorize deployment or release behavior.

---

## 12. Closing Slice Statement

> The first Pilot UI slice must be small enough to control, but complete enough to demonstrate the product's central review-to-truth story.

It is intentionally not the full Pilot UI.

It is the first coherent implementation target that makes EPIC 33 demonstrable without violating:

- Base44 construction boundaries;
- backend-owned truth rules;
- approved screen sequencing;
- the Pilot Demo Narrative;
- the Financial Truth Layer architecture.

This slice defines the correct starting point for controlled Pilot UI construction in later EPIC 33 work.