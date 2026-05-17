# Pilot Screen Construction Sequence

## Mini-EPIC 33.2 — Pilot UI Implementation Planning & Base44 Construction Boundary

## 1. Purpose

This document defines the official controlled construction sequence for Pilot UI screens during EPIC 33.

Mini-EPIC 33.1 established the Pilot UI architecture, approved screen inventory, operator workflow, Financial Truth Layer presentation surfaces, and Pilot Demo Narrative.

Mini-EPIC 33.2 now determines the order in which those approved screens should be constructed in Base44.

This sequence exists to prevent implementation from becoming:

- visually convenient but product-weak;
- screen-by-screen without workflow coherence;
- over-scoped before the first coherent Pilot UI slice exists;
- disconnected from the Financial Truth Layer demonstration narrative.

> Pilot UI screen construction must follow workflow logic, dependency order, and demo narrative priority.

---

## 2. Construction Sequence Principle

The Pilot UI must be built in a sequence that answers three questions in the correct order:

1. What structural frame must exist before any screen is meaningful?
2. What minimum workflow path makes the product narrative visible?
3. What supporting or backend-dependent surfaces should wait until the core Pilot story is structurally coherent?

The approved screen sequence is therefore based on:

- application structure first;
- operator context second;
- core review flow third;
- human intervention fourth;
- backend-owned financial truth presentation fifth;
- supporting intake and cross-screen trust states sixth.

---

## 3. Official Pilot Screen Construction Sequence

The official construction sequence for EPIC 33 Pilot UI work is:

1. Pilot Shell / Navigation Frame
2. Tenant / User Context Surface
3. Pilot Dashboard
4. Reconciliation Review Queue
5. Match Detail / Evidence View
6. Human Correction Screen
7. Finalized Truth Record
8. Export Readiness Surface
9. Intake Workspace
10. Shared Trust / Error / Permission Presentation Layer

This sequence is controlled.

Later implementation work may refine details inside a screen, but it should not reorder the core screen construction path without an explicit architecture-level reason.

---

## 4. Sequence Rationale by Screen

### 4.1 Pilot Shell / Navigation Frame

> Build first because every later Pilot UI screen requires a stable product frame.

The Pilot Shell / Navigation Frame establishes:

- application structure;
- screen routing;
- visual hierarchy;
- the operator's sense of product location;
- a stable frame into which later screens are added.

Without this first, every later screen risks becoming a disconnected standalone mockup rather than part of an actual Pilot UI.

### 4.2 Tenant / User Context Surface

> Build second because the Pilot UI must demonstrate that operator activity exists within a defined tenant/user context.

This surface provides the visible location for:

- tenant identity presentation;
- user/operator context presentation;
- future backend-fed scoping signals;
- architecture-consistent demonstration of tenant-awareness.

This screen surface is built early because tenant-aware presentation is a core credibility requirement for InvoMatch and should be visible from the start of the Pilot UI narrative.

### 4.3 Pilot Dashboard

> Build third because it is the first operational entry surface in the Pilot Demo Narrative.

The Pilot Dashboard should visually establish:

- the operator's current operational starting point;
- summary visibility into review-relevant work;
- the path into the Reconciliation Review Queue;
- the role of the Pilot UI as a controlled operational cockpit rather than a collection of isolated screens.

The Dashboard should not be overbuilt into analytics or reporting.

Its purpose in this construction sequence is to orient and transition the operator into the core review workflow.

### 4.4 Reconciliation Review Queue

> Build fourth because it is the first core workflow screen and the operational heart of the Pilot demonstration.

The Review Queue should surface:

- items requiring operator review;
- backend-shaped review indicators or explicitly documented placeholders;
- structured columns for evidence-aware navigation;
- the controlled transition into individual record inspection.

This screen must be available before detailed record inspection can have product meaning.

### 4.5 Match Detail / Evidence View

> Build fifth because individual review only becomes meaningful after the Review Queue exists.

The Match Detail / Evidence View should provide:

- selected item inspection;
- evidence presentation;
- reason/context display;
- operator orientation before any correction action;
- a controlled surface for Financial Truth Layer explanation.

This screen is critical.

It must communicate why an item is under review and what evidence is visible, without allowing the frontend to determine the truth of the item.

### 4.6 Human Correction Screen

> Build sixth because human action should follow evidence inspection, not precede it.

The Human Correction Screen should support:

- a correction-entry surface;
- explicit backend-bound action points;
- correction context grounded in the selected item;
- placeholder response-state handling only where documented.

This screen is sequenced after detail inspection to preserve a disciplined operator narrative:

Review item
> inspect evidence
> take bounded human action

It must not be positioned as a standalone arbitrary editing tool.

### 4.7 Finalized Truth Record

> Build seventh because finalized truth is a downstream outcome surface, not an initial interaction surface.

The Finalized Truth Record should display:

- backend-owned finalized state when available;
- record-level truth surfaces;
- immutable/audit-oriented presentation semantics where applicable;
- the visible transition from review intervention toward governed truth.

This screen is deliberately sequenced after correction because it must not imply that truth exists before the review/action path is understood.

### 4.8 Export Readiness Surface

> Build eighth because export readiness is a downstream interpretation of backend-owned finalized truth.

The Export Readiness Surface should display:

- whether downstream export is blocked, pending, or ready when backend semantics support it;
- readiness explanations or blockers;
- the distinction between finalized truth and export readiness;
- a UI surface that remains presentational, never truth-generating.

It follows the Finalized Truth Record because readiness must not be presented before truth ownership is visibly established.

### 4.9 Intake Workspace

> Build ninth because intake is important, but it is not the shortest route to demonstrating the Financial Truth Layer review narrative.

The Intake Workspace should later represent:

- file/data intake entry;
- upload or ingestion-related framing;
- operational arrival of items into the broader workflow.

However, placing Intake too early creates a risk that EPIC 33 becomes an upload-focused Pilot rather than a Financial Truth Layer demonstration.

For this reason, Intake is intentionally deferred until the review-to-truth path is already structurally visible.

### 4.10 Shared Trust / Error / Permission Presentation Layer

> Build tenth because these shared states must stabilize the Pilot UI after the core sequence exists.

This layer should complete the Pilot UI with:

- loading states;
- empty states;
- unavailable states;
- blocked states;
- permission presentation;
- trust-signaling messages;
- cross-screen consistency in operational clarity.

These states are important for credibility, but they should not delay the construction of the main demonstration path.

---

## 5. Construction Grouping

The official sequence can be grouped into controlled construction bands.

### Group A — Structural Foundation

1. Pilot Shell / Navigation Frame
2. Tenant / User Context Surface

Purpose:

- establish the stable application frame;
- make tenant-aware Pilot presentation visible;
- prepare all later screens for coherent placement.

### Group B — Operator Entry and Review Flow

3. Pilot Dashboard
4. Reconciliation Review Queue
5. Match Detail / Evidence View

Purpose:

- define the core operator journey;
- make review work visible;
- allow the Pilot Demo Narrative to begin functioning as a coherent walkthrough.

### Group C — Human Intervention and Truth Outcome

6. Human Correction Screen
7. Finalized Truth Record
8. Export Readiness Surface

Purpose:

- demonstrate bounded operator intervention;
- expose downstream backend-owned truth outcomes;
- make the Financial Truth Layer story visible.

### Group D — Supporting Operational Completion

9. Intake Workspace
10. Shared Trust / Error / Permission Presentation Layer

Purpose:

- complete the wider Pilot environment;
- reinforce clarity, resilience, and credibility;
- prepare for later backend binding and demo stabilization.

---

## 6. Relationship to the First Pilot Slice

The first coherent Pilot UI slice should draw primarily from:

- Group A;
- Group B;
- controlled portions of Group C.

Specifically, the first slice should include:

1. Pilot Shell / Navigation Frame
2. Tenant / User Context Surface
3. Pilot Dashboard
4. Reconciliation Review Queue
5. Match Detail / Evidence View
6. Human Correction Screen as a bounded action surface
7. Finalized Truth Record / Export Readiness as controlled display shells where needed for narrative closure

The Intake Workspace and full shared trust-state layer should not be required for the first slice to be considered coherent.

---

## 7. Explicit Deferral Rules

The following rules govern deferral.

### 7.1 Screens That Must Not Jump Ahead

The following screens must not be prioritized ahead of the core review narrative:

- Intake Workspace;
- Export Readiness Surface in fully developed form;
- broad trust/error presentation completion;
- visually rich dashboard expansions unrelated to the core review path.

### 7.2 Details That May Be Deferred Within a Screen

A screen may be constructed structurally before all backend bindings are finalized.

Examples:

- Finalized Truth Record may be built as a display shell before final backend response semantics are bound.
- Export Readiness Surface may be built as a presentation layout before readiness semantics are live.
- Human Correction Screen may expose a correction form structure before actual submission integration is implemented.

But these screens must remain clearly classified as construction-stage surfaces where backend truth is not yet active.

### 7.3 Sequence Deviations Require Explicit Justification

If later EPIC 33 work proposes a different construction order, the deviation must explicitly explain:

- why the change is required;
- how it preserves the Pilot Demo Narrative;
- why it does not weaken the architecture defined in Mini-EPIC 33.1;
- why it does not violate the Base44 Construction Boundary.

Convenience alone is not a valid reason to reorder the sequence.

---

## 8. Sequence Acceptance Criteria

This construction sequence is considered formally defined when:

- all approved Pilot UI screen surfaces are placed into a single explicit order;
- the order begins with structural foundation rather than feature randomness;
- the core review path is prioritized before intake completion and decorative expansion;
- Human Correction follows evidence inspection;
- Finalized Truth Record precedes Export Readiness Surface;
- Intake Workspace is intentionally deferred beyond the first review-centered Pilot slice;
- shared trust/error/permission presentation is acknowledged as required but not allowed to interrupt the core Pilot path;
- any later deviation is subject to explicit justification.

---

## 9. Out of Scope

This document does not:

- construct actual Base44 pages;
- generate Base44 prompts;
- connect live backend APIs;
- implement corrections, finalization, or export logic;
- redesign the screen inventory approved in Mini-EPIC 33.1;
- alter backend contracts;
- execute Scenario 15;
- trigger regression reruns;
- authorize deployment or release behavior.

---

## 10. Closing Sequence Statement

> The Pilot UI must be built in the order that makes the product story truthful, coherent, and progressively demonstrable.

The official Pilot Screen Construction Sequence is therefore not a cosmetic preference.

It is a control mechanism that ensures Base44 implementation remains:

- architecture-aligned;
- workflow-centered;
- demo-narrative-aware;
- backend-truth-respecting;
- resistant to ad hoc scope expansion.

This sequence governs all later EPIC 33 Pilot UI construction planning and execution.