# Screen Construction Acceptance Criteria

## Mini-EPIC 33.2 — Pilot UI Implementation Planning & Base44 Construction Boundary

## 1. Purpose

This document defines the minimum acceptance criteria that must govern later Base44 construction of approved EPIC 33 Pilot UI screen surfaces.

Mini-EPIC 33.1 established:

- the Pilot UI architecture;
- the approved screen inventory;
- operator workflow;
- Financial Truth Layer presentation surfaces;
- the official Pilot Demo Narrative.

Mini-EPIC 33.2 has now defined:

- the Pilot UI implementation strategy;
- the Base44 construction boundary;
- the screen construction sequence;
- the First Pilot Slice;
- screen readiness classification;
- backend dependency and placeholder discipline.

This document converts that planning into reviewable, screen-level construction expectations.

> A screen should not be considered acceptably constructed merely because a page exists. It must satisfy the minimum criteria required for its role in the Pilot UI architecture.

---

## 2. Acceptance Criteria Principle

The acceptance criteria in this document are designed to answer:

1. What must exist on a screen for its initial construction to be considered structurally valid?
2. What truth-boundary rules must remain intact?
3. What placeholder or backend-bound markings must be visible where needed?
4. What must not be falsely implied by a newly constructed screen?

The criteria are not a release checklist.

They are a controlled construction-quality gate for future EPIC 33 Pilot UI implementation work.

> Construction acceptance proves that a screen has been built according to plan. It does not prove backend integration, product completion, or release readiness.

---

## 3. Universal Acceptance Criteria for All Pilot UI Screens

Every Pilot UI screen constructed later in EPIC 33 must satisfy the following universal acceptance criteria.

1. The screen must align with the approved screen role defined in Mini-EPIC 33.1 and Mini-EPIC 33.2.
2. The screen must fit the approved Pilot Screen Construction Sequence unless an explicit architecture-level deviation has been documented.
3. The screen must not introduce frontend-owned matching, finalization, export-readiness, or tenant-rule logic.
4. The screen must distinguish backend-owned truth from shell-only or placeholder content where applicable.
5. The screen must preserve the Pilot Demo Narrative rather than expanding into unrelated visual or functional scope.
6. The screen must contain only construction elements appropriate to its readiness classification.
7. The screen must not be described as product-complete if backend-dependent semantics remain unbound.
8. The screen must not turn provisional content into silent business truth.

---

## 4. Acceptance Criteria by Screen

### 4.1 Pilot Shell / Navigation Frame

Construction is acceptable only if:

1. A shared application frame exists for the Pilot UI.
2. The frame provides clear navigation access to the first-slice screen path.
3. Screen routing or route destinations are organized according to the approved Pilot construction sequence.
4. Page title or location context is visible enough to orient the operator.
5. The frame does not imply that backend workflows are completed simply because navigation is available.
6. Placeholder routes, if present, are clearly treated as not-yet-complete construction surfaces.

Not acceptable:

- isolated pages with no coherent product shell;
- navigation entries that create the appearance of complete backend workflow execution;
- route sprawl beyond the approved Pilot scope without documented reason.

### 4.2 Tenant / User Context Surface

Construction is acceptable only if:

1. A visible tenant/user context region exists in the Pilot UI.
2. The surface is clearly presentation-level unless backend-bound semantics are later confirmed.
3. Any provisional tenant or user labels are obviously placeholders or explicitly documented construction assumptions.
4. The surface does not implement frontend-owned tenant authorization or security logic.
5. The context placement supports Pilot Demo clarity across relevant screens.

Not acceptable:

- tenant labels presented as backend-verified when they are not;
- UI logic that pretends to enforce tenant isolation;
- omission of tenant/user context from the first-slice Pilot environment.

### 4.3 Pilot Dashboard

Construction is acceptable only if:

1. The dashboard acts as a clear operator entry point.
2. It visibly connects the operator to the Reconciliation Review Queue.
3. It contains only review-relevant summary areas appropriate to the Pilot narrative.
4. Any counts, metrics, or summaries that are not backend-bound are explicitly provisional or shell-only.
5. It does not become a generic analytics page disconnected from the review-to-truth path.
6. It supports progression into the first coherent Pilot slice.

Not acceptable:

- dashboards dominated by cosmetic metrics with no workflow value;
- fake live operational totals presented as authoritative;
- dashboards that distract from or replace the review path.

### 4.4 Reconciliation Review Queue

Construction is acceptable only if:

1. A queue/table structure exists for displaying review work.
2. The layout includes clear regions for status, reason/context, and action availability.
3. The queue supports a clear conceptual transition into Match Detail / Evidence View.
4. Any queue rows, reason labels, or status values that are provisional are explicitly marked or governed as contract-shaped placeholder content.
5. No review state is derived in frontend logic.
6. No queue interaction implies backend acceptance, correction persistence, or finalization without actual backend semantics.
7. The screen remains central to the first Pilot slice rather than becoming a secondary appendix.

Not acceptable:

- list views with no visible evidence of review-specific structure;
- frontend-generated “approved,” “rejected,” or “ready” outcomes;
- placeholder queue content presented as real operational truth.

### 4.5 Match Detail / Evidence View

Construction is acceptable only if:

1. The screen clearly represents inspection of one selected review item.
2. Evidence presentation regions exist for showing relevant item context.
3. A reason, explanation, or review-context region is reserved where required by the Pilot narrative.
4. The screen supports a clear next-step transition toward Human Correction where that path is appropriate.
5. Provisional evidence blocks are explicitly placeholder-governed if backend payloads are not yet connected.
6. The screen does not generate or claim a truth verdict.
7. The presentation makes evidence legible without implying that evidence interpretation has been finalized in the frontend.

Not acceptable:

- detail screens that are visually dense but do not expose review rationale;
- UI-computed confidence or match verdict presented as product truth;
- detail pages detached from the Reconciliation Review Queue context.

### 4.6 Human Correction Screen

Construction is acceptable only if:

1. A bounded correction-entry surface exists.
2. The correction surface is clearly connected to the prior review/evidence context.
3. Any submission control is presented as backend-bound, provisional, or explicitly non-final when backend action semantics are not yet active.
4. The screen includes space for later result-state presentation without claiming that a result has already occurred.
5. No local UI action is represented as authoritative acceptance, rejection, finalization, or export-readiness change.
6. The screen respects the distinction between operator input and backend-confirmed product outcome.
7. The screen remains inside the approved first Pilot slice posture rather than expanding into a full workflow engine.

Not acceptable:

- mock submit flows that end in false “accepted” or “finalized” results;
- correction forms detached from the review item that caused them;
- frontend-only correction behavior represented as persisted system truth.

### 4.7 Finalized Truth Record

Construction is acceptable only if:

1. A structured downstream truth-record display surface exists.
2. The surface is visibly separated from earlier review and correction states.
3. The screen can host backend-owned finalized state, metadata, or record fields later.
4. If backend finalized-state semantics are not yet bound, the surface remains explicitly shell-only or placeholder-governed.
5. The screen does not claim real finalization from frontend state transitions.
6. The surface reinforces the Financial Truth Layer narrative rather than becoming a decorative summary card.
7. It remains clear that finalized truth is a backend-owned condition.

Not acceptable:

- fake finalized records created solely to close the demo visually;
- display content that implies immutable truth where no backend truth exists;
- finalized-state language used without dependency discipline.

### 4.8 Export Readiness Surface

Construction is acceptable only if:

1. A dedicated readiness display surface exists distinct from the Finalized Truth Record.
2. The surface provides space for backend-fed readiness state, blockers, and explanations.
3. Any provisional readiness labels are explicitly governed as placeholders.
4. The screen does not compute readiness from visible UI conditions.
5. The screen does not imply that export behavior exists when only display structure exists.
6. The surface completes the review-to-truth-to-readiness narrative without overstating implementation maturity.

Not acceptable:

- UI-only “ready to export” logic;
- readiness determined from completion of form fields or local interactions;
- presenting export as operational when only a readiness shell exists.

### 4.9 Intake Workspace

Construction is acceptable only after a later controlled phase explicitly reopens it.

For future construction, acceptance will require:

1. a clear intake-entry role within the broader Pilot UI;
2. backend-bound or explicitly provisional upload/ingestion semantics;
3. no distortion of the already-approved first-slice review-to-truth priority;
4. clear distinction between intake presentation and backend processing truth.

Current first-slice position:

> Intake Workspace remains deferred beyond the first implementation slice and should not be constructed as part of the first controlled Pilot build target.

Not acceptable in first-slice construction:

- pulling intake forward for visual completeness;
- treating upload UI breadth as more important than the review-to-truth core narrative.

### 4.10 Shared Trust / Error / Permission Presentation Layer

Full-layer construction is acceptable only in a later controlled phase.

For partial first-slice support, limited screen-local states are acceptable only if:

1. they are necessary to keep an included first-slice screen coherent;
2. they do not pretend to implement backend permission enforcement;
3. they do not overtake the primary review flow;
4. they are kept clearly bounded as supporting presentation patterns.

Full later-phase acceptance will require:

5. consistent trust/error/permission treatment across relevant Pilot screens;
6. clear blocked, unavailable, empty, and permission-oriented display patterns;
7. alignment with backend semantics rather than frontend invention.

Not acceptable:

- broad trust-state work that delays the core first-slice build;
- fake permission enforcement in UI only;
- error states presented as authoritative backend outcomes when they are merely placeholder examples.

---

## 5. Acceptance Matrix by Screen

| Screen or Surface | Minimum Construction Requirement | Key Prohibition |
|---|---|---|
| Pilot Shell / Navigation Frame | Coherent shared product frame and route structure | No route-based implication of backend completion |
| Tenant / User Context Surface | Visible context presentation region | No frontend tenant enforcement |
| Pilot Dashboard | Review-oriented operator entry with queue transition | No fake live metrics |
| Reconciliation Review Queue | Queue structure with status/reason/action layout | No frontend-derived review truth |
| Match Detail / Evidence View | Selected-item inspection with evidence regions | No UI-generated truth verdict |
| Human Correction Screen | Bounded correction-entry surface | No fake acceptance/finalization outcome |
| Finalized Truth Record | Downstream truth-record display shell | No fabricated finalized truth |
| Export Readiness Surface | Readiness display shell with blocker/explanation space | No frontend-calculated readiness |
| Intake Workspace | Deferred until later phase | No first-slice construction pull-forward |
| Shared Trust / Error / Permission Layer | Later full-layer work; minimal screen-local support only if required | No fake permission/security implementation |

---

## 6. Construction Review Questions

Before a future screen construction step is accepted, reviewers should be able to answer all of the following with confidence:

1. Is this screen part of the approved Pilot screen inventory?
2. Is it being constructed at the appropriate point in the approved sequence?
3. Does it satisfy the minimum criteria for its screen role?
4. Are all placeholder or backend-dependent areas visibly bounded?
5. Does it avoid truth-generation in Base44?
6. Does it support the First Pilot Slice or a later explicitly authorized phase?
7. Would a reviewer understand what is real, what is shell-only, and what is pending backend confirmation?
8. Does acceptance of this screen avoid overstating implementation completeness?

---

## 7. What Screen Acceptance Does Not Mean

Passing these construction acceptance criteria does not mean:

- the screen is production-ready;
- the screen is live-backend-integrated;
- the underlying product capability is complete;
- backend contracts are settled;
- the screen has passed release-readiness review;
- the screen is fully polished visually;
- the Pilot UI is ready for deployment;
- the associated business capability is already implemented.

> Screen acceptance is a controlled UI construction judgment, not a release or backend-completion claim.

---

## 8. Acceptance Failure Conditions

A future screen construction step must be considered unacceptable if any of the following occurs:

1. the screen violates its approved readiness classification;
2. placeholder content is presented as product truth;
3. frontend logic derives review, finalization, readiness, or tenant-security outcomes;
4. the screen jumps ahead of the controlled construction sequence without explicit justification;
5. the screen expands scope beyond its Pilot role without documented reason;
6. downstream truth surfaces are used to falsely close the demo narrative;
7. deferred first-slice exclusions are pulled forward for visual convenience;
8. the construction creates ambiguity about what is backend-owned versus UI-only.

---

## 9. Acceptance Criteria for the First Pilot Slice as a Whole

The first Pilot slice may be considered acceptably constructed later only if:

1. Pilot Shell / Navigation Frame, Tenant / User Context Surface, Pilot Dashboard, Reconciliation Review Queue, and Match Detail / Evidence View are all structurally coherent together.
2. Human Correction Screen exists as a bounded action surface, not as a fake complete correction engine.
3. Finalized Truth Record and Export Readiness Surface exist only in a manner consistent with their shell/dependency status.
4. Intake Workspace remains deferred.
5. Shared Trust / Error / Permission Layer is not over-expanded beyond limited support required for included screens.
6. The Pilot Demo Narrative is visibly understandable from entry through readiness display.
7. No frontend-owned product truth has been introduced.
8. The entire slice remains migration-safe and architecture-aligned.

---

## 10. Acceptance Criteria Completion Standard

This document is complete only if:

- every approved Pilot UI screen or surface has explicit construction acceptance criteria;
- every criterion preserves the Base44 Construction Boundary;
- shell-only and backend-dependent screens are prevented from being misclassified as complete;
- the First Pilot Slice has whole-slice acceptance criteria;
- later reviewers can evaluate construction quality without improvising new standards;
- the document prevents visual completion from being mistaken for product completion.

---

## 11. Out of Scope

This document does not:

- build actual Base44 screens;
- generate Base44 prompts;
- approve live backend integration;
- define final API contracts;
- implement matching logic;
- implement correction execution;
- implement finalization execution;
- implement export readiness behavior;
- execute Scenario 15;
- rerun regression suites;
- authorize deployment or release behavior.

---

## 12. Closing Acceptance Statement

> Pilot UI construction must be reviewable by standard, not defended by visual impression.

These criteria ensure that later EPIC 33 construction is evaluated against:

- approved screen purpose;
- controlled sequence;
- readiness classification;
- backend dependency discipline;
- placeholder honesty;
- First Pilot Slice integrity.

They create a hard line between:

- a screen that merely exists;
- and a screen that is acceptably constructed within the InvoMatch Pilot UI architecture.