# Backend Dependency and Placeholder Discipline

## Mini-EPIC 33.2 — Pilot UI Implementation Planning & Base44 Construction Boundary

## 1. Purpose

This document defines the backend dependency discipline and placeholder usage rules for EPIC 33 Pilot UI construction.

Mini-EPIC 33.1 established that:

- Base44 is the Pilot UI Layer only;
- the backend remains the only source of product truth;
- Financial Truth Layer states must be displayed, not invented;
- Pilot UI surfaces must remain aligned with operator workflow and governed backend semantics.

Mini-EPIC 33.2 now formalizes how UI construction may proceed when some backend contracts, response semantics, or integration points are not yet fully bound into the Pilot UI.

This document answers four questions:

1. Which Pilot UI surfaces depend on backend-owned semantics?
2. Where may structured placeholders be used during controlled UI construction?
3. What must placeholders never claim or simulate?
4. When must a surface remain explicitly non-complete until backend confirmation exists?

> Placeholder discipline exists to enable controlled UI construction without allowing frontend assumptions to become fake product truth.

---

## 2. Core Dependency Principle

> Backend truth may be temporarily absent from a screen under construction, but it may never be silently replaced by frontend invention.

The Pilot UI may be planned and later constructed before every backend contract is live in Base44.

However:

- any backend-dependent surface must remain explicitly classified as provisional, shell-only, or pending backend binding where applicable;
- no placeholder may be treated as the authoritative business state;
- no UI-only behavior may be presented as equivalent to backend-confirmed workflow progression;
- no screen may be declared product-complete merely because its layout exists.

---

## 3. Backend Dependency Categories

Pilot UI construction must recognize the following backend dependency categories.

### 3.1 Identity and Scope Dependencies

These dependencies govern who is acting and within what operational boundary.

Examples:

- tenant identity;
- user/operator identity;
- tenant-scoped visibility;
- permission-aware display;
- access restrictions or blocked states.

Frontend rule:

> The UI may display tenant/user context, but it may not enforce or invent tenant security semantics.

### 3.2 Operational Summary Dependencies

These dependencies feed overview-level Pilot UI surfaces.

Examples:

- dashboard counts;
- queue totals;
- review workload summaries;
- pending or blocked item totals;
- operational state cards.

Frontend rule:

> Dashboard and summary surfaces may be structurally prepared, but displayed operational truth must remain backend-fed or explicitly marked as provisional.

### 3.3 Review Queue Dependencies

These dependencies govern the review queue and work-item state.

Examples:

- reconciliation item status;
- review reason;
- action availability;
- queue grouping;
- item selection identity;
- backend-determined review urgency or state.

Frontend rule:

> The UI may organize queue presentation, but it may not derive review state.

### 3.4 Evidence and Explanation Dependencies

These dependencies govern item-level review detail.

Examples:

- invoice evidence fields;
- payment evidence fields;
- mismatch explanations;
- reason-code descriptions;
- audit-relevant context;
- backend-provided comparatives or explanation payloads.

Frontend rule:

> The UI may arrange evidence, but it may not create the explanation logic or truth verdict.

### 3.5 Human Correction Dependencies

These dependencies govern operator action semantics.

Examples:

- correction submission request shape;
- correction validation responses;
- correction acceptance result;
- rejected correction result;
- correction persistence confirmation;
- backend-owned post-correction workflow state.

Frontend rule:

> A correction form may be constructed before live binding, but correction outcome truth may not be simulated as authoritative.

### 3.6 Finalized Truth Dependencies

These dependencies govern the Financial Truth Layer record outcome.

Examples:

- finalized truth status;
- immutable record presentation;
- audit-safe truth metadata;
- finalization origin/context;
- finalized record identifiers or timestamps;
- backend-owned truth-state explanations.

Frontend rule:

> Finalized truth may be displayed only as backend-owned state or as an explicitly labeled future display surface.

### 3.7 Export Readiness Dependencies

These dependencies govern downstream readiness visibility.

Examples:

- export-ready state;
- blocked export state;
- pending readiness state;
- readiness blockers;
- downstream eligibility explanation;
- backend-owned export interpretation.

Frontend rule:

> Export readiness must never be calculated in Base44 from visible form or screen conditions.

### 3.8 Intake Dependencies

These dependencies govern ingestion-related UI work planned for later phases.

Examples:

- upload request behavior;
- validation response;
- ingestion status;
- source-file acceptance or rejection;
- item creation results;
- intake error semantics.

Frontend rule:

> Intake may be planned later, but it is not part of the first Pilot slice and must not pull dependency design away from the review-to-truth narrative.

---

## 4. Placeholder Usage Categories

Controlled placeholders may be used only in the categories below.

### 4.1 Structural Placeholder

Purpose:

- reserves page regions;
- shapes information hierarchy;
- shows where backend-fed content will appear.

Allowed examples:

- empty card area labeled for future dashboard counts;
- detail panel section reserved for backend-provided evidence;
- readiness summary block clearly marked as pending backend binding.

Not allowed:

- a visually complete block that silently implies live backend truth.

### 4.2 Contract-Shaped Mock Data

Purpose:

- helps define table layout;
- helps test information density;
- helps construct meaningful screen hierarchy around expected backend fields.

Allowed examples:

- review queue rows using clearly provisional data structures;
- evidence fields shaped after known or expected backend payload families;
- placeholder blocker labels used only to structure the Export Readiness Surface.

Not allowed:

- mock records presented as real operational outcomes;
- invented domain semantics that have not been approved or backend-aligned.

### 4.3 Action Placeholder

Purpose:

- shows where future backend-bound user actions will occur;
- supports layout for buttons, forms, and action feedback regions.

Allowed examples:

- correction submit button marked as backend-bound;
- disabled export action area where only readiness display is currently planned;
- modal or confirmation shell that does not pretend a backend update occurred.

Not allowed:

- local action flow that visually claims real acceptance, finalization, or readiness transition.

### 4.4 Response-State Placeholder

Purpose:

- reserves space for future success, error, blocked, or pending response states;
- helps ensure later API binding has a clear presentation destination.

Allowed examples:

- pending correction submission state area;
- future blocked-readiness message region;
- future permission-denied presentation card.

Not allowed:

- placeholder success messaging that states a real backend action has completed when no backend confirmation exists.

---

## 5. Placeholder Labeling Discipline

Every placeholder introduced during later Pilot UI construction must satisfy the following labeling discipline in implementation planning and related documentation.

1. It must be explicitly identifiable as provisional, backend-bound, shell-only, or pending contract confirmation.
2. It must not use wording that implies backend-confirmed completion unless such confirmation exists.
3. It must be tied to a named screen or UI surface.
4. It must identify the dependency category it stands in for where relevant.
5. It must be removable or replaceable without changing the product architecture.
6. It must never silently become a permanent substitute for backend integration.

> A placeholder is acceptable only when its temporary nature and dependency relationship are visible.

---

## 6. Placeholder Claims That Are Strictly Forbidden

The following claims are forbidden unless they are truly supported by backend-owned truth.

- "Finalized" as a result of UI-only interaction;
- "Export Ready" based on frontend-visible completeness;
- "Approved" following a mock correction action;
- "Tenant access denied" as if enforced by frontend logic rather than backend permission;
- "Correction accepted" without backend result semantics;
- "Review complete" when only the page transition occurred;
- "Evidence sufficient" when that assessment is not backend-owned;
- "Ready for accounting export" without backend-owned readiness state.

> Base44 may present screens that discuss these outcomes, but it may not fabricate them.

---

## 7. Screen-Specific Dependency and Placeholder Rules

### 7.1 Tenant / User Context Surface

Backend dependencies:

- tenant identity;
- operator identity;
- true scope semantics.

Allowed placeholders:

- clearly provisional tenant label;
- clearly provisional user context display.

Forbidden:

- frontend-enforced tenant isolation;
- invented permission decisions.

### 7.2 Pilot Dashboard

Backend dependencies:

- real review counts;
- real operational totals;
- real blocked/pending/ready summaries.

Allowed placeholders:

- structured stat-card layouts;
- provisional sample values when explicitly marked.

Forbidden:

- presenting sample counts as live product metrics.

### 7.3 Reconciliation Review Queue

Backend dependencies:

- queue contents;
- statuses;
- reason codes;
- action availability;
- item identity.

Allowed placeholders:

- structured sample rows;
- future status pill positions;
- placeholder reason labels strictly for layout testing.

Forbidden:

- deriving queue statuses in Base44;
- implying row truth from mock interactions.

### 7.4 Match Detail / Evidence View

Backend dependencies:

- detail payload;
- evidence fields;
- explanation semantics;
- review basis.

Allowed placeholders:

- evidence card structure;
- provisional field groups;
- labeled comparison layout.

Forbidden:

- fake explanation logic;
- UI-generated review verdict.

### 7.5 Human Correction Screen

Backend dependencies:

- correction request contract;
- validation behavior;
- accepted/rejected correction semantics;
- persisted workflow result.

Allowed placeholders:

- form layout;
- disabled submit area;
- provisional post-submit response region.

Forbidden:

- fake acceptance;
- fake finalization;
- fake state transition after frontend-only submit.

### 7.6 Finalized Truth Record

Backend dependencies:

- finalized status;
- immutable truth record semantics;
- finalization metadata.

Allowed placeholders:

- structured truth-record shell;
- section headings for future backend-fed state;
- empty or clearly pending data blocks.

Forbidden:

- representing mock truth as finalized financial truth.

### 7.7 Export Readiness Surface

Backend dependencies:

- readiness status;
- blocker semantics;
- downstream availability explanation.

Allowed placeholders:

- readiness card shell;
- blocker-section layout;
- future action display region.

Forbidden:

- calculating readiness from UI completion;
- showing real readiness claims from invented data.

### 7.8 Intake Workspace

Backend dependencies:

- upload behavior;
- ingestion validation;
- item creation lifecycle;
- intake failure semantics.

Allowed placeholders during first slice:

- none, because Intake Workspace is deferred beyond the first implementation slice.

Later posture:

- may be reopened under a later controlled phase.

Forbidden:

- pulling Intake into first-slice scope merely for UI breadth.

---

## 8. Product-Completion Discipline

The following rules govern what may and may not be described as complete.

1. A screen shell is not a completed Pilot capability.
2. A placeholder-filled screen is not backend-integrated.
3. A contract-shaped mock is not a verified backend contract.
4. A disabled or provisional action area is not implemented workflow execution.
5. A finalized-truth display shell is not finalized truth implementation.
6. An export-readiness panel is not export readiness logic.
7. A visually coherent first Pilot slice is not a feature-complete Pilot UI.

> Completion language must reflect backend-semantic reality, not visual progress.

---

## 9. Dependency Escalation Triggers

Later EPIC 33 work must explicitly reopen backend dependency review when any of the following becomes necessary:

- a placeholder must be replaced with live response semantics;
- a UI state is about to be described as operationally real;
- Human Correction moves from shell to action implementation;
- Finalized Truth Record moves from display shell to backend-bound truth surface;
- Export Readiness moves from display shell to backend-fed readiness surface;
- tenant or permission presentation moves from placeholder to enforced context;
- Intake Workspace moves into active construction planning.

These triggers prevent hidden architecture drift.

---

## 10. Dependency and Placeholder Matrix

| Surface | Key Backend Dependency | Placeholder Allowed | Completion Claim Allowed Before Backend Confirmation |
|---|---|---|---|
| Tenant / User Context | Tenant and user semantics | Yes, explicitly provisional | No |
| Pilot Dashboard | Operational summary values | Yes, clearly marked | No |
| Review Queue | Queue rows, statuses, reasons | Yes, contract-shaped only | No |
| Match Detail / Evidence | Evidence payload and explanation semantics | Yes, structural only | No |
| Human Correction | Action request and result semantics | Yes, shell only | No |
| Finalized Truth Record | Finalized state semantics | Yes, display shell only | No |
| Export Readiness | Readiness and blocker semantics | Yes, display shell only | No |
| Intake Workspace | Ingestion lifecycle | No in first slice | No |

---

## 11. Acceptance Criteria

This dependency and placeholder discipline is considered complete only if:

- the backend dependency categories are explicitly defined;
- allowed placeholder types are explicitly bounded;
- placeholder labeling rules are documented;
- forbidden placeholder claims are identified;
- screen-specific placeholder rules are defined;
- screen completion claims are separated from visual construction progress;
- dependency escalation triggers are documented;
- deferred intake behavior remains outside first-slice construction scope;
- Human Correction, Finalized Truth Record, and Export Readiness cannot be falsely presented as backend-complete from UI shells alone.

---

## 12. Out of Scope

This document does not:

- define final backend contracts;
- implement backend endpoints;
- generate Base44 prompts;
- construct Base44 pages;
- bind live APIs;
- approve mock content as product truth;
- implement matching logic;
- implement correction execution;
- implement finalization execution;
- implement export readiness logic;
- execute Scenario 15;
- rerun regression suites;
- authorize deployment or release behavior.

---

## 13. Closing Discipline Statement

> The Pilot UI may use placeholders to move construction forward, but it may not use placeholders to move truth forward.

This document governs the line between:

- valid visual preparation;
- valid contract-shaped scaffolding;
- backend-dependent meaning;
- prohibited frontend invention.

It protects EPIC 33 from confusing demo construction with product truth implementation.