# Screen Readiness Classification

## Mini-EPIC 33.2 — Pilot UI Implementation Planning & Base44 Construction Boundary

## 1. Purpose

This document defines the formal readiness classification for all approved Pilot UI screen surfaces in EPIC 33.

Mini-EPIC 33.1 established the Pilot UI architecture, screen inventory, operator workflow, Financial Truth Layer presentation surfaces, and Pilot Demo Narrative.

Mini-EPIC 33.2 now determines which screens may enter Base44 construction immediately, which may exist only as controlled shells, which require backend contract confirmation before they can be treated as functionally valid, and which should remain deferred beyond the first Pilot slice.

This classification exists to prevent:

- premature screen construction;
- false claims of implementation completeness;
- uncontrolled placeholder expansion;
- backend-dependent surfaces being presented as finished UI capabilities;
- deviation from the First Pilot Slice Definition.

> A screen may be visible in the Pilot UI plan without being functionally ready for full implementation.

---

## 2. Classification Model

Each approved Pilot UI screen is assigned one or more readiness classifications from the following controlled model.

### 2.1 Ready for Immediate Base44 Construction

A screen is classified as Ready for Immediate Base44 Construction when:

- its role is already architecturally clear;
- its core layout can be constructed without inventing product truth;
- it supports the approved Pilot screen sequence;
- it does not require unresolved backend semantics in order to begin structural construction.

This classification authorizes controlled UI construction planning later in EPIC 33.

It does not authorize business logic implementation.

### 2.2 Ready Only as Shell / Placeholder Surface

A screen is classified as Ready Only as Shell / Placeholder Surface when:

- its place in the Pilot narrative is approved;
- its layout or presentation area can be constructed;
- its real product meaning depends on backend-owned semantics not yet bound;
- it must not be described as functionally complete.

This classification is especially important for downstream truth and readiness surfaces.

### 2.3 Requires Backend Contract Confirmation

A screen or screen segment is classified as Requires Backend Contract Confirmation when:

- specific state meanings are backend-owned;
- action result semantics are not yet safe to represent as final;
- exact response shapes or status vocabulary require confirmation;
- tenant, permission, finalized truth, export readiness, or correction result semantics cannot be safely invented in UI planning.

This classification does not prohibit future construction work.

It prohibits false completion claims and truth-generating frontend assumptions.

### 2.4 Deferred Beyond First Implementation Slice

A screen or capability is classified as Deferred Beyond First Implementation Slice when:

- it is relevant to the broader Pilot UI;
- it is not necessary to demonstrate the first coherent review-to-truth narrative;
- implementing it now would weaken focus or expand scope prematurely.

Deferral is a planning decision, not a rejection of the screen.

---

## 3. Classification Summary Table

| Screen or Surface | Immediate Base44 Construction | Shell / Placeholder Only | Requires Backend Contract Confirmation | Deferred Beyond First Slice |
|---|---|---|---|
| Pilot Shell / Navigation Frame | Yes | No | No | No |
| Tenant / User Context Surface | Yes | Partially, where tenant data is not yet bound | Yes, for true tenant/user semantics | No |
| Pilot Dashboard | Yes | Partially, where metrics or counts are provisional | Yes, for backend-fed operational summaries | No |
| Reconciliation Review Queue | Yes | Partially, where queue rows or reasons are provisional | Yes, for status/reason/action semantics | No |
| Match Detail / Evidence View | Yes | Partially, where evidence payloads are provisional | Yes, for evidence and explanation semantics | No |
| Human Correction Screen | Limited structural construction | Yes | Yes, for action request/result semantics | No |
| Finalized Truth Record | Limited structural construction | Yes | Yes, for finalized truth semantics | No |
| Export Readiness Surface | Limited structural construction | Yes | Yes, for readiness semantics and blockers | No |
| Intake Workspace | Not in first slice | Possible only after later phase authorization | Yes, for intake behavior semantics | Yes |
| Shared Trust / Error / Permission Presentation Layer | Not as full layer in first slice | Partial only when necessary for included screens | Yes, for permission and trust-state semantics | Yes |

---

## 4. Screen-by-Screen Readiness Decision

### 4.1 Pilot Shell / Navigation Frame

Classification:

- Ready for Immediate Base44 Construction.

Rationale:

- the product frame is structurally required before screen workflows can be coherent;
- shell/navigation does not require backend truth to begin;
- this surface anchors the controlled Pilot environment.

Permitted construction posture:

- full structural shell planning;
- approved route structure;
- placement for later tenant/user context;
- navigation entries for Pilot slice screens.

Explicit constraint:

- navigation may not imply that backend state transitions are already real.

### 4.2 Tenant / User Context Surface

Classification:

- Ready for Immediate Base44 Construction;
- Ready Only as Shell / Placeholder Surface where tenant/user data is not yet backend-fed;
- Requires Backend Contract Confirmation for authoritative tenant/user semantics.

Rationale:

- tenant-awareness must be visible early;
- layout and placement can be safely constructed;
- actual context truth remains backend-owned.

Permitted construction posture:

- context banner, header region, or account/tenant surface;
- placeholder labels only when explicitly documented;
- no frontend-owned tenant enforcement.

Explicit constraint:

- presentation of tenant context is allowed; implementation of tenant rules is not.

### 4.3 Pilot Dashboard

Classification:

- Ready for Immediate Base44 Construction;
- Ready Only as Shell / Placeholder Surface for provisional metrics or counts;
- Requires Backend Contract Confirmation for operational summary values.

Rationale:

- dashboard is the first operator entry surface;
- it is needed for the Pilot Demo Narrative;
- true summary data must remain backend-fed.

Permitted construction posture:

- review-oriented dashboard layout;
- workflow entry cards;
- queue navigation path;
- clearly provisional data display where needed.

Explicit constraint:

- dashboard summaries may be shaped for later backend binding, but they may not become invented product truth.

### 4.4 Reconciliation Review Queue

Classification:

- Ready for Immediate Base44 Construction;
- Ready Only as Shell / Placeholder Surface for queue rows, reasons, or statuses that are not yet backend-bound;
- Requires Backend Contract Confirmation for review status, reason codes, and action availability semantics.

Rationale:

- this is the operational heart of the first Pilot slice;
- its structure can be safely constructed now;
- its domain meaning cannot be fabricated in the frontend.

Permitted construction posture:

- queue table layout;
- status/reason/action columns;
- row-selection interaction;
- route into Match Detail / Evidence View.

Explicit constraint:

- the queue may display backend-shaped placeholder states, but it may not derive review truth in UI logic.

### 4.5 Match Detail / Evidence View

Classification:

- Ready for Immediate Base44 Construction;
- Ready Only as Shell / Placeholder Surface for provisional evidence sections;
- Requires Backend Contract Confirmation for evidence payload shape, explanation content, and status semantics.

Rationale:

- evidence inspection is central to the Product Demo Narrative;
- layout can be built without final backend payloads;
- actual meaning of evidence and explanation must remain backend-owned.

Permitted construction posture:

- item detail panels;
- evidence comparison sections;
- reason/explanation areas;
- route into Human Correction Screen.

Explicit constraint:

- the screen may organize evidence, but it may not generate the truth verdict.

### 4.6 Human Correction Screen

Classification:

- Limited structural construction is permitted;
- Ready Only as Shell / Placeholder Surface;
- Requires Backend Contract Confirmation for action request/result semantics.

Rationale:

- this screen is essential to the first Pilot narrative;
- its role is approved;
- however, correction actions are backend-sensitive and must not be falsely simulated as authoritative.

Permitted construction posture:

- correction-entry layout;
- fields shaped around future backend binding;
- clearly labeled backend-bound action area;
- disabled or provisional action states where necessary.

Explicit constraint:

- clicking or submitting within a mock screen must not be represented as creating accepted or finalized backend truth.

### 4.7 Finalized Truth Record

Classification:

- Limited structural construction is permitted;
- Ready Only as Shell / Placeholder Surface;
- Requires Backend Contract Confirmation for finalized truth semantics.

Rationale:

- this screen closes the Financial Truth Layer demonstration arc;
- it must be visible in the First Pilot Slice;
- it cannot imply real finalization without backend semantics.

Permitted construction posture:

- structured truth-record layout;
- display regions for backend-owned finalized state;
- separation from review/correction state.

Explicit constraint:

- Base44 may create the display shell, but it may not create finalized truth.

### 4.8 Export Readiness Surface

Classification:

- Limited structural construction is permitted;
- Ready Only as Shell / Placeholder Surface;
- Requires Backend Contract Confirmation for readiness semantics, blockers, and downstream state meanings.

Rationale:

- this surface is needed to complete the review-to-truth-to-readiness narrative;
- the UI shell can be defined;
- readiness itself is not a frontend calculation.

Permitted construction posture:

- readiness panel;
- blocker/explanation area;
- downstream display region for backend-provided readiness state.

Explicit constraint:

- export readiness may be displayed, but not computed or invented by Base44.

### 4.9 Intake Workspace

Classification:

- Deferred Beyond First Implementation Slice;
- Requires Backend Contract Confirmation for intake behavior semantics;
- not part of the first construction target.

Rationale:

- intake matters to the full Pilot UI;
- it is not necessary for the first review-centered slice;
- prioritizing it too early would shift EPIC 33 away from the core Financial Truth Layer demonstration.

Permitted construction posture:

- none during the first slice unless explicitly reopened in a later controlled phase.

Explicit constraint:

- Intake Workspace must not jump ahead of the approved review-to-truth implementation sequence.

### 4.10 Shared Trust / Error / Permission Presentation Layer

Classification:

- Deferred Beyond First Implementation Slice as a complete shared layer;
- partial shell use is allowed only where necessary for included first-slice screens;
- Requires Backend Contract Confirmation for permission semantics and trusted response-state presentation.

Rationale:

- these states are important for credibility;
- they should be planned carefully;
- they should not delay the first coherent Pilot path.

Permitted construction posture:

- minimal loading/empty/blocked patterns only where a first-slice screen would otherwise be incoherent;
- broader systemization deferred to later phase.

Explicit constraint:

- trust and permission presentation must not be invented as substitute security or backend truth.

---

## 5. Readiness Classification by First Pilot Slice Role

| Surface | First Slice Role | Readiness Interpretation |
|---|---|---|
| Pilot Shell / Navigation Frame | Core foundation | Fully eligible for immediate structural construction |
| Tenant / User Context Surface | Context foundation | Construct now, backend semantics remain pending |
| Pilot Dashboard | Operator entry | Construct now, summary truth remains backend-dependent |
| Reconciliation Review Queue | Core workflow | Construct now, statuses and reasons remain backend-dependent |
| Match Detail / Evidence View | Evidence inspection | Construct now, evidence semantics remain backend-dependent |
| Human Correction Screen | Bounded human action | Shell-level construction only until backend correction semantics are confirmed |
| Finalized Truth Record | Downstream truth visibility | Shell-level construction only until finalization semantics are confirmed |
| Export Readiness Surface | Downstream readiness visibility | Shell-level construction only until readiness semantics are confirmed |
| Intake Workspace | Supporting future entry flow | Deferred beyond first slice |
| Shared Trust / Error / Permission Layer | Cross-screen credibility layer | Deferred as a full layer; minimal screen-local patterns only if required |

---

## 6. Readiness Rules for Later Base44 Construction

Later EPIC 33 implementation must follow these rules:

1. A screen classified as immediate may enter Base44 construction planning without being described as product-complete.
2. A screen classified as shell-only may be laid out, but its backend-dependent truth semantics must remain visibly provisional.
3. A screen classified as requiring backend contract confirmation must not be used as evidence that the underlying product capability is complete.
4. A screen classified as deferred beyond the first slice must not be pulled forward for visual convenience.
5. A single screen may hold multiple classifications at once, and the strictest relevant boundary controls interpretation.
6. Readiness classification governs implementation posture, not only documentation wording.

---

## 7. Required Classification Guardrails

The following guardrails are mandatory:

- immediate construction does not equal product completion;
- shell availability does not equal backend readiness;
- placeholder visibility does not equal trustworthy product truth;
- a downstream outcome surface may be present in the Pilot narrative while still being contract-dependent;
- deferred screens remain valid future Pilot work, but not first-slice work;
- backend-dependent semantics must never be silently replaced by frontend interpretation.

> Readiness classification is designed to prevent UI momentum from outrunning product truth.

---

## 8. Classification Acceptance Criteria

This readiness classification is considered complete only if:

- every approved Pilot UI screen is classified;
- first-slice screens are clearly distinguished from deferred screens;
- immediate construction is separated from backend-semantic readiness;
- shell-only surfaces are explicitly marked;
- backend contract dependencies are named for each relevant surface;
- Intake Workspace is intentionally deferred beyond the first implementation slice;
- Shared Trust / Error / Permission Presentation Layer is not treated as complete first-slice work;
- Human Correction, Finalized Truth Record, and Export Readiness Surface are not misclassified as implementation-ready product capabilities.

---

## 9. Out of Scope

This document does not:

- build actual Base44 screens;
- generate Base44 prompts;
- connect backend APIs;
- settle backend contract design;
- implement matching logic;
- implement correction behavior;
- implement finalization behavior;
- implement export readiness behavior;
- execute Scenario 15;
- run regression reruns;
- authorize deployment or release behavior.

---

## 10. Closing Classification Statement

> The Pilot UI may advance screen-by-screen, but it may not advance truth-by-assumption.

This readiness classification establishes the disciplined boundary between:

- what can be constructed now;
- what can only be shell-visible now;
- what requires backend contract confirmation;
- what must be deferred beyond the first Pilot slice.

It protects EPIC 33 from turning planned screen visibility into false claims of implementation completeness.