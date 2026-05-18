
Base44 Phase A Prompting Boundary
Mini-EPIC 33.3 — Pilot UI Phase A Construction Authorization & Base44 Shell Execution Boundary
1. Purpose

This document defines the prompting boundary that governs the first real Base44 construction instruction for EPIC 33.

Mini-EPIC 33.3 is the first point at which Base44 may be directly instructed to generate implementation artifacts.

Because generative UI tools can overbuild, reinterpret scope, invent data surfaces, or prematurely simulate workflows, the Phase A prompt must remain unusually constrained.

The prompt is not a creative brief. It is an execution control surface.

2. Prompting Principle

The governing prompt principle is:

Ask Base44 to construct only the Pilot UI shell and navigation frame required by Phase A, and explicitly forbid it from generating later workflow screens, data semantics, fake metrics, or product truth.

This prompting discipline protects the project from:

dashboard invention;
fake product cards;
premature workflow construction;
accidental simulation of review/finalization/export states;
visual breadth that violates phase order.
3. What the Phase A Prompt Must Request

The Phase A prompt must ask Base44 to build:

a professional Pilot UI application shell;
persistent navigation suitable for a B2B operational product;
a main content canvas;
a shared page-header/title pattern;
route or page-entry placeholders for the approved later Pilot screens;
a visible reserved region for tenant/user context;
shell-level visual consistency;
a migration-safe structure that can later host Phase B and later screens without redesigning the overall frame.

The prompt must make clear that:

this is structural work only;
the Pilot workflow itself is not yet being built;
placeholders must remain visibly placeholders;
no operational meaning should be implied by empty shell areas.
4. What the Phase A Prompt Must Explicitly Forbid

The Phase A prompt must explicitly prohibit Base44 from generating:

a real dashboard screen;
review queue tables;
review cards;
evidence cards;
correction forms;
finalized truth records;
export readiness widgets;
intake/upload workspace behavior;
charts, KPIs, reconciliation metrics, or operational counts;
fake backend data;
fake status tags;
fake product readiness indicators;
fake tenant/user values;
access or permission logic;
API integrations;
business workflow interactions.

These prohibitions must be present in the prompt itself, not merely assumed from the surrounding Mini-EPIC documents.

5. Prompt Structure Requirements

The Base44 Phase A prompt should be structured in five parts.

Part 1 — Product Context

Explain briefly:

this is InvoMatch;
the interface is a Pilot UI Layer only;
the backend remains the source of product truth;
this prompt is only for Phase A shell/navigation foundation.
Part 2 — Build Request

Specify exactly what to create:

shell;
navigation;
page frame;
content canvas;
page header pattern;
tenant/user reserved region;
route/page placeholders.
Part 3 — Strict Non-Build Constraints

State what must not be created.

This must be concrete and exhaustive enough that Base44 is not invited to “helpfully” fill gaps.

Part 4 — Structural Quality Expectations

State that the output should be:

coherent;
professional;
B2B operational in posture;
expandable;
future-safe;
not over-designed;
not workflow-complete.
Part 5 — Completion Check

Ask Base44 to return an implementation that:

reads as a product frame;
does not read as a completed product workflow;
is ready to accept later Phase B screens.
6. Route and Navigation Discipline

The prompt may reference later approved Pilot UI surfaces only as:

navigation labels;
disabled or structural entries;
page slots;
shell-aware future placeholders.

It may not ask Base44 to implement the content of those screens.

The difference is critical:

“Create navigation posture for Review Queue” is allowed.
“Build the Review Queue” is not allowed.
“Reserve a page slot for Export Readiness” is allowed.
“Create Export Readiness cards and readiness statuses” is not allowed.
7. Placeholder Discipline in Prompting

Any placeholder requested in the Phase A prompt must be:

explicit;
non-functional;
visibly provisional;
structural rather than semantic.

The prompt must not use vague phrasing such as:

“add useful dashboard content”;
“fill the page meaningfully”;
“show example metrics”;
“make it feel complete.”

Those instructions would invite Base44 to fabricate business meaning.

8. Prompting Failure Modes to Avoid

The following prompt failures are prohibited.

Failure Mode 1 — Over-Broad Product Prompt

Example problem:

Build the InvoMatch Pilot UI.

This is invalid because it authorizes uncontrolled scope.

Failure Mode 2 — Visual Completeness Bias

Example problem:

Make the dashboard look rich and realistic.

This is invalid because it invites fake metrics and workflow content.

Failure Mode 3 — Workflow Leakage

Example problem:

Add review examples so the flow is visible.

This is invalid in Phase A because review flow belongs to later phases.

Failure Mode 4 — Placeholder Ambiguity

Example problem:

Use sample data where needed.

This is invalid because it risks creating fake truth surfaces.

9. Review Requirement After Prompt Execution

The Base44 result produced from the Phase A prompt must be reviewed against:

PHASE_A_EXECUTION_BOUNDARY.md;
PHASE_A_TARGET_SHELL_ARTIFACT_DEFINITION.md;
PHASE_A_CONSTRUCTION_ACCEPTANCE_CRITERIA.md.

The prompt itself is not proof of compliance.

The generated artifact must be inspected for scope leakage.

10. Final Prompting Boundary Statement

Base44 may be instructed to build the Phase A shell. It may not be invited to invent the Phase B workflow, the Phase C truth surfaces, the Phase D operational breadth, or the Phase E backend-connected semantics.
