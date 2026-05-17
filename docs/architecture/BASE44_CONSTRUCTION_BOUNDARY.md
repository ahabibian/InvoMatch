# Base44 Construction Boundary

## Mini-EPIC 33.2 — Pilot UI Implementation Planning & Base44 Construction Boundary

## 1. Purpose

This document defines the explicit implementation boundary for using Base44 during EPIC 33 Pilot UI construction.

Mini-EPIC 33.1 established that Base44 is not the product truth layer, not the backend, and not the place where financial decision logic lives.

Mini-EPIC 33.2 now converts that architectural position into a direct construction rule set:

> Base44 may construct and present the Pilot UI, but it may not reinterpret, fabricate, or own product truth.

This document exists to prevent Base44 implementation from becoming an uncontrolled frontend logic layer during Pilot UI construction.

---

## 2. Boundary Principle

> Base44 is a Pilot UI construction layer. It is not a financial truth engine.

Base44 may be used to build:

- product-facing UI structure;
- navigation and screen routing;
- workflow presentation surfaces;
- operator interaction shells;
- display states shaped around backend-owned truth;
- explicitly documented placeholder surfaces where live backend binding is not yet present.

Base44 may not be used to create:

- financial business logic;
- backend substitute behavior;
- tenant enforcement rules;
- finalized-truth decisions;
- export-readiness decisions;
- reconciliation or matching decisions;
- invented acceptance outcomes.

---

## 3. What Base44 Is Allowed to Do

The following implementation actions are permitted inside Base44 during EPIC 33 Pilot UI construction.

### 3.1 Page and Layout Construction

Base44 may define:

- application shell;
- screen layouts;
- page hierarchy;
- reusable visual sections;
- responsive page arrangements where needed for demo usability;
- shared page headers and section structures.

### 3.2 Navigation Structure

Base44 may define:

- left navigation or top navigation patterns;
- screen-to-screen movement;
- demo-flow navigation routes;
- page access pathways for approved Pilot UI screens;
- breadcrumbs or return paths where useful for operator orientation.

Navigation may express workflow structure.

Navigation may not imply business authorization or state truth that the backend has not provided.

### 3.3 Screen Shells and Display Regions

Base44 may construct screen shells for:

- Pilot Dashboard;
- Reconciliation Review Queue;
- Match Detail / Evidence View;
- Human Correction Screen;
- Finalized Truth Record;
- Export Readiness Surface;
- Intake Workspace;
- shared trust / error / permission presentation areas.

These shells may exist before full backend connection only when they are clearly treated as UI construction surfaces, not functioning product proof.

### 3.4 Tables, Detail Panels, Cards, Filters, and Modals

Base44 may provide standard Pilot UI presentation components such as:

- tables;
- detail panels;
- evidence cards;
- status display sections;
- non-truth-defining filter controls;
- drawers;
- modal confirmation surfaces;
- empty-state regions;
- loading-state regions.

These components may improve usability and demo clarity.

They may not create new product semantics.

### 3.5 Lightweight UI State

Base44 may manage lightweight, local UI state that is strictly presentational, such as:

- selected row display;
- open / closed panel state;
- active tab state;
- modal visibility;
- temporary field editing before submission;
- UI-only filters where they do not reinterpret backend truth;
- demo navigation state.

Lightweight UI state must never become a source of business status or financial truth.

### 3.6 Controlled Display States

Base44 may show controlled display states such as:

- loading;
- empty;
- disabled;
- awaiting backend confirmation;
- data unavailable;
- permission display state when backend-bound or explicitly marked as placeholder;
- blocked state when based on documented backend-shaped assumptions.

Display states are permitted as presentation mechanics.

They may not claim that a backend process has completed when no such truth exists.

### 3.7 API Call Placeholders and Backend-Bound Request Points

Base44 may include:

- clearly named backend integration points;
- placeholder request handlers;
- visible action buttons intended for future API binding;
- non-final mock action flows that are explicitly labeled as provisional.

These are allowed only when they document where backend truth will later enter the UI.

They must not be represented as complete functional integration.

### 3.8 Explicitly Documented Mock or Provisional Data Surfaces

Base44 may use structured mock data only when:

- the mock is explicitly documented;
- the mock shape is intended to mirror an expected backend contract;
- the mock is visibly understood as construction-stage support;
- the mock does not claim live product state;
- the mock does not create false acceptance, finalization, or readiness signals.

---

## 4. What Base44 Is Not Allowed to Do

The following actions are forbidden in Base44 during EPIC 33 Pilot UI construction.

### 4.1 Derive Review State

Base44 must not decide:

- whether a reconciliation item is correct;
- whether a review item should be accepted;
- whether a record is approved;
- whether evidence is sufficient;
- whether an operator action changes the product truth state.

Review state must come from backend-owned semantics or remain visibly non-final.

### 4.2 Derive Export Readiness

Base44 must not determine:

- whether a record is export-ready;
- whether export prerequisites are satisfied;
- whether unresolved issues block export;
- whether financial truth is ready for downstream consumption.

Export readiness is a backend-owned product status.

### 4.3 Create Fake Finalized Truth

Base44 must never create or imply:

- finalized transaction truth;
- accepted reconciliation truth;
- immutable record truth;
- audit-safe finalized truth;
- export-authorized truth.

If finalized truth is displayed in a Pilot UI shell before backend binding, it must be explicitly marked as a planned display surface, not as generated truth.

### 4.4 Simulate Backend Acceptance as Product Truth

Base44 must not make a button click, local UI state change, or demo transition appear equivalent to backend-confirmed acceptance.

Prohibited examples include:

- clicking "Approve" and immediately showing "Finalized" as though product truth changed;
- using local state to represent accepted correction results;
- showing export-ready status after purely frontend interaction;
- treating mock action results as authoritative workflow outcomes.

### 4.5 Implement Tenant Rules

Base44 must not implement:

- tenant authorization rules;
- tenant isolation logic;
- user permission enforcement;
- access ownership policy;
- backend security substitutes.

Tenant and permission truth remain backend responsibilities.

The UI may display tenant or permission context only as backend-fed or explicitly documented placeholder presentation.

### 4.6 Implement Matching Logic

Base44 must not:

- compare invoice values;
- compute confidence;
- determine match status;
- infer reconciliation correctness;
- create reason-code logic;
- rank match decisions.

Matching logic remains backend-owned.

### 4.7 Implement Finalization Logic

Base44 must not:

- finalize records;
- freeze truth state;
- decide immutability;
- approve transition into finalized state;
- present local completion as governance-complete finalization.

Finalization logic is explicitly outside Base44.

### 4.8 Turn Placeholder Content into Product Truth

A placeholder may assist UI construction.

A placeholder may not become:

- an accepted domain model;
- an undocumented permanent workaround;
- a substitute for backend contract work;
- a silent source of business meaning;
- a basis for claiming feature completion.

---

## 5. Allowed vs. Forbidden Examples

### 5.1 Allowed Example — Review Queue Shell

Allowed:

- Base44 creates a queue table with columns such as status, reason, amount, supplier, and action availability.
- Sample rows are used for layout work.
- A visible note or documented implementation assumption states that the data surface is mock-shaped pending backend binding.

Not allowed:

- Base44 independently calculates whether a row is accepted, disputed, corrected, or finalized.

### 5.2 Allowed Example — Human Correction Screen

Allowed:

- Base44 creates a correction form layout.
- Form fields reflect a future backend request shape.
- The submit control is defined as a backend-bound action point.

Not allowed:

- Submitting the form locally changes reconciliation truth and marks the transaction finalized.

### 5.3 Allowed Example — Export Readiness Surface

Allowed:

- Base44 creates a panel that will later display backend-provided export readiness status.
- The surface can include labeled sections for blockers, readiness reason, and next-step interpretation.

Not allowed:

- Base44 decides readiness by checking whether visible form fields look complete.

### 5.4 Allowed Example — Permission Presentation

Allowed:

- Base44 displays an empty, blocked, or restricted-state pattern intended for future backend permission binding.
- The document and UI surface clearly indicate that enforcement remains backend-owned.

Not allowed:

- Base44 contains tenant-rule logic and presents that as the authoritative permission model.

---

## 6. Base44 Construction Boundary by UI Concern

| UI Concern | Allowed in Base44 | Forbidden in Base44 |
|---|---|---|
| Layout | Yes | — |
| Navigation | Yes | Navigation implying backend approval |
| Tables / Cards / Panels | Yes | Business decisions embedded in components |
| Local selection state | Yes | Business status mutation |
| Filters | Yes, if presentation-only | Filters that derive truth or acceptance |
| Form entry | Yes | Form submission presented as backend-complete when it is not |
| API placeholders | Yes, explicitly marked | Hidden mock logic treated as real integration |
| Mock data | Yes, documented and provisional | Fake product truth |
| Review status | Display only | Derived in UI |
| Finalized state | Display only | Created in UI |
| Export readiness | Display only | Calculated in UI |
| Tenant access | Display only | Enforced or invented in UI |

---

## 7. Required Implementation Discipline

Every Base44 screen constructed during EPIC 33 must preserve the following discipline:

1. UI structure may advance before live backend binding.
2. Product truth may not advance before backend semantics exist.
3. Placeholder content must be visible in documentation and bounded in purpose.
4. Frontend convenience must never override architecture.
5. Pilot Demo clarity may justify shell construction, but not fake workflow completion.
6. Any apparent product completion must be supported by backend-owned or explicitly governed evidence, not Base44 invention.

---

## 8. Relationship to Later EPIC 33 Work

This boundary document governs later work such as:

- screen construction sequencing;
- Base44 prompt creation;
- screen readiness classification;
- placeholder discipline;
- backend binding preparation;
- future Pilot Demo stabilization.

Later implementation steps may become more detailed, but they may not weaken this boundary.

---

## 9. Out of Scope

This boundary document does not authorize:

- actual Base44 page creation;
- live backend API work;
- backend endpoint redesign;
- matching logic implementation;
- finalization logic implementation;
- export implementation;
- frontend-owned governance decisions;
- Scenario 15 execution;
- regression reruns;
- deployment or release behavior.

---

## 10. Closing Boundary Statement

> Base44 may build the Pilot UI surface. It may not build, replace, or fabricate the product truth layer beneath it.

Mini-EPIC 33.2 uses this construction boundary to ensure that later Pilot UI implementation remains:

- visually productive;
- workflow-oriented;
- backend-contract-aware;
- migration-safe;
- architecturally honest.

This boundary must remain active throughout all subsequent EPIC 33 UI construction work.