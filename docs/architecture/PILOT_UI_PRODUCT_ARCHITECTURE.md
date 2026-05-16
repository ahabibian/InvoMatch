
PILOT UI PRODUCT ARCHITECTURE
Mini-EPIC 33.1 — Pilot UI Product Architecture
1. Purpose

This document defines the product and operational architecture of the InvoMatch Pilot UI for EPIC 33.

The purpose of this architecture is to ensure that the Pilot UI is built as a controlled product demonstration layer over the existing backend and Financial Truth Layer, rather than as an ad hoc collection of screens.

This document establishes:

the exact role of Base44 in EPIC 33
the fixed boundary between UI and backend
the read and write interaction model
how tenant, user, trust, and error states are surfaced
the principle that the UI consumes backend truth and never creates product truth
the architectural foundation for all downstream screen, API, workflow, and demo definitions in Mini-EPIC 33.1

Mini-EPIC 33.1 does not implement UI pages.
It defines the architecture that makes later UI implementation safe, consistent, and product-valid.

2. Architectural Position of the Pilot UI
2.1 System Role

The Pilot UI is a presentation and operator interaction layer placed above the backend product system.

Its role is to:

present backend-derived financial workflow state
expose Financial Truth Layer value in a human-understandable way
support operator review and action submission
make the InvoMatch product story demonstrable in a controlled pilot environment
provide the UI surface required for usability observation and product validation

The Pilot UI is not:

a decision engine
a reconciliation engine
a persistence authority
an audit subsystem
an export subsystem
a replacement for backend product logic
2.2 High-Level Architecture
┌──────────────────────────────────────────────┐
│              Pilot UI Layer                  │
│                  Base44                      │
│                                              │
│  - Screens                                   │
│  - Layout                                    │
│  - Tables / Filters / Modals                 │
│  - Lightweight view state                    │
│  - API requests                              │
│  - Operator action triggers                  │
│  - Trust / error state presentation          │
└──────────────────────┬───────────────────────┘
                       │
                       │ API Contracts
                       ▼
┌──────────────────────────────────────────────┐
│             Backend Application Layer        │
│                                              │
│  - Authenticated tenant/user context         │
│  - Reconciliation workflow state             │
│  - Matching and correction processing        │
│  - Finalization logic                        │
│  - FTL projection and record generation      │
│  - Export readiness calculation              │
│  - Audit linkage and evidence references     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│            Product Truth / Persistence       │
│                                              │
│  - Source records                            │
│  - Normalized entities                       │
│  - Match candidates                          │
│  - Review decisions                          │
│  - Finalized truth records                   │
│  - Audit-safe lineage                        │
│  - Export-ready projections                  │
└──────────────────────────────────────────────┘
3. Base44 Architectural Boundary
3.1 Base44 Is a Pilot UI Layer Only

Within EPIC 33, Base44 is adopted as the Pilot UI implementation surface.

Its usage is justified because EPIC 33 is not trying to optimize frontend engineering depth.
Its immediate purpose is to:

make the Financial Truth Layer visible
demonstrate the operator workflow
validate which screens and interactions matter
build a coherent pilot experience for review, partner discussion, and future product direction

However, this speed advantage is acceptable only if the architectural boundary is kept strict.

3.2 Base44 Allowed Responsibilities

Base44 may own:

screen composition
route/page organization
visual layout
cards, tables, panels, filters, and modals
local form state before submission
temporary selection state
API call orchestration
loading, empty, success, degraded, and blocked state presentation
display of backend-provided evidence and explanations
trigger of operator actions through backend endpoints

Examples:

showing a review queue
opening a match detail view
rendering backend-generated evidence blocks
letting the user submit an approve/reject/correct intent
showing export readiness as returned by backend
displaying tenant and user context as returned by backend
3.3 Base44 Forbidden Responsibilities

Base44 must not own, derive, recreate, or persist any of the following:

matching logic
confidence scoring logic
financial reconciliation decision logic
finalization logic
tenant access rules
user permission rules
source-of-truth financial state
audit trail generation
export readiness calculation
export package logic
FTL record generation
canonical persistence
correction learning logic
backend-equivalent business rules

Examples of forbidden behavior:

calculating whether a match is valid inside Base44
deciding whether a record is finalized based on UI-side assumptions
deriving export readiness from several frontend fields
hiding or revealing financial records based on frontend-only tenant filtering
generating “audit history” in the UI from local action memory
storing final review decisions in Base44-owned state as authoritative truth
4. Core Architectural Principle
4.1 UI Consumes Backend Truth, Not Creates Truth

The foundational principle of Pilot UI architecture is:

The UI consumes backend truth, displays backend truth, and submits operator intent. It does not create product truth.

This principle governs every EPIC 33 screen and every API contract.

The UI may:

ask for state
render state
collect human input
submit a request to change state

The backend must:

validate the request
check authorization
apply business rules
mutate product truth where allowed
return the updated authoritative state
4.2 Required Interaction Pattern

Every meaningful operator action must follow this pattern:

1. UI displays backend-provided state
2. Operator selects an action
3. UI collects minimal intent payload
4. UI submits payload to backend
5. Backend validates permission, state, and rules
6. Backend accepts or rejects the action
7. UI refreshes from backend truth
8. UI displays resulting authoritative state

The UI must never assume success prior to backend confirmation.

5. Read Flow Architecture
5.1 Definition

A read flow is any frontend interaction where the Pilot UI requests authoritative product state from backend APIs and renders it without altering it.

Read flows include:

dashboard summaries
intake status
processing run status
review queue items
match detail records
evidence blocks
human correction history
finalized truth record state
export readiness state
tenant/user context
permission-aware availability of actions
system trust/degraded states
5.2 Read Flow Principle

The UI must receive a backend response that is already shaped enough to be safely displayed.

Base44 should not be forced to reconstruct product meaning from raw low-level records.

For example:

Bad:

UI receives raw invoices, raw payments, raw match candidates,
then calculates “review required” locally.

Good:

Backend returns a review queue item with:
- review_status
- reason_for_review
- candidate_summary
- evidence_summary
- permitted_actions

This reduces frontend logic leakage and preserves backend authority.

5.3 Read Flow Expectations

Backend read responses should support the following UI needs:

clear status labels
human-readable explanation fields where useful
stable entity identifiers
tenant/user-scoped data only
explicit readiness/blocking states
explicit empty states where applicable
timestamps and lineage references where relevant
links or IDs for drill-down navigation
permission-conditioned action availability
6. Write Flow Architecture
6.1 Definition

A write flow is any frontend interaction where the operator expresses an intent that may modify system state through a backend API.

Write flows may include:

approve proposed match
reject proposed match
correct a wrong match
manually reassign a target
confirm a human review decision
request finalization of a reviewed record where the backend allows it
acknowledge or trigger controlled workflow transitions where later EPIC 33 screens require it
6.2 Write Flow Principle

The UI submits intent, not truth.

Examples:

Correct:

{
  "action": "approve_match",
  "review_item_id": "..."
}

Incorrect:

{
  "final_match_status": "approved",
  "export_ready": true,
  "truth_record_state": "finalized"
}

The first payload asks the backend to perform a governed operation.
The second payload illegally attempts to dictate product truth from the UI.

6.3 Write Flow Validation Ownership

For every write flow, the backend exclusively owns:

authorization
tenant isolation
entity existence checks
state transition validation
conflict handling
duplicate action prevention
audit generation
persistence
response truth

The UI only:

prevents obviously incomplete submissions
communicates in-progress status
displays backend acceptance or rejection
refreshes authoritative state
7. Tenant and User Context Architecture
7.1 Purpose

The Pilot UI must visibly reinforce that InvoMatch is not a single-user toy dashboard.
It is a tenant-aware product layer operating over governed financial records.

Therefore, tenant and user context should be surfaced where it adds clarity and trust.

7.2 Context Display Principles

The UI may display backend-provided context such as:

current tenant name or identifier
current operational workspace
authenticated user identity or role label
current permission scope where useful
environment or pilot mode label, if available

This context should be:

visible enough to reinforce product maturity
not intrusive
never generated or inferred by frontend logic
7.3 Context Ownership

The backend owns:

who the current user is
which tenant context is active
which actions are permitted
which records are visible

The UI displays this information, but does not determine it.

8. Trust-State Architecture
8.1 Why Trust States Matter

InvoMatch is dealing with financial reconciliation and truth formation.
A product UI that only shows “happy path” green panels is weak and unconvincing.

The Pilot UI must demonstrate that it can communicate uncertainty, incompleteness, and operational blockers without breaking product trust.

Trust states are therefore a first-class UI concern.

8.2 Trust State Categories

At minimum, the Pilot UI architecture must be able to present:

complete / ready
review required
evidence incomplete
export not ready
permission restricted
processing in progress
degraded backend health
failed operation
recovery in progress
unresolved review dependency
8.3 Trust State Rule

The UI should never cosmetically smooth over uncertainty.

If the backend indicates:

missing evidence
unresolved review
failed processing
not-export-ready status

the UI must preserve that meaning clearly.

The interface should remain professional, but it must not hide operational truth.

9. Error Presentation Architecture
9.1 Error Handling Principle

The Pilot UI must not expose raw backend exceptions or technical stack traces to users.

However, it must also not reduce meaningful operational failures to vague messages like:

“Something went wrong.”

That is not sufficient for a financial workflow product.

9.2 Required Error Presentation Model

UI error messaging should translate backend failures into:

what happened
what is affected
whether the operator can act
whether the system is safe to continue using
what next visible step is available

Example:

Export readiness cannot be confirmed because required evidence is missing for this truth record.
The record has not been finalized for export.
Review the evidence panel or return to the review queue.

This preserves trust without leaking internals.

10. Permission Presentation Architecture
10.1 Permission Must Be Visible, Not Hidden

A professional product does not simply remove functionality without explanation.

When an action is unavailable due to permission or workflow state, the UI should make that clear where appropriate.

Examples:

button disabled with explanation
informative status block
action unavailable message tied to role or state
export readiness section explaining why export cannot proceed
10.2 Backend Ownership

The backend decides:

whether an action is allowed
which action options are available
whether permission denial is role-based or state-based

The UI presents the outcome, never simulates the rule.

11. Product Narrative Architecture
11.1 Pilot UI Must Tell the Product Story

The Pilot UI is not just a control panel.
It is the first visible product surface where the value of Financial Truth Layer becomes understandable.

The architecture must support the following narrative:

Raw financial intake enters the system.
The system processes and reconciles it.
A proposed financial interpretation is formed.
Evidence and reasoning are exposed.
A human operator reviews or corrects the result.
A finalized truth record becomes visible.
Export readiness and audit linkage show that the record is operationally trustworthy.

This narrative must be reflected across screen structure, workflows, and API contracts.

11.2 FTL Visibility Requirement

The Financial Truth Layer must not remain hidden behind internal terminology.

Through the UI, users must be able to see the difference between:

raw input
normalized interpretation
system proposal
human review
finalized truth
export readiness

That is the true product demonstration goal of EPIC 33.

12. Architectural Non-Negotiables

The following principles are mandatory for EPIC 33 implementation:

12.1 Backend Truth Dominance

No Pilot UI screen may become an alternate source of truth.

12.2 Intent-Based Writes

All mutations begin as operator intent and are resolved by backend rules.

12.3 Zero Core Logic in Base44

No financial matching, finalization, export, audit, tenant, or persistence logic may be migrated into the Pilot UI.

12.4 Explicit State Handling

Loading, empty, blocked, degraded, failed, and ready states must be accounted for deliberately.

12.5 FTL Must Be Visibly Demonstrable

The UI must surface the lifecycle from intake to finalized truth, not merely display data tables.

12.6 API Contracts Must Be Screen-Aware

Endpoints and response structures should serve product screens intentionally, rather than pushing UI reconstruction work into Base44.

12.7 Pilot UI Must Remain Migration-Safe

The architecture must allow later migration away from Base44 to a custom frontend without rethinking the product backend model.

13. Architectural Relationship to Later Mini-EPIC 33.1 Deliverables

This document serves as the parent architectural rule set for:

PILOT_SCREEN_INVENTORY_AND_RESPONSIBILITY_MAP.md
FTL_SURFACE_DEFINITION.md
INITIAL_API_TO_SCREEN_MAPPING_FRAMEWORK.md
OPERATOR_WORKFLOW_DEFINITION.md
TRUST_ERROR_AND_PERMISSION_PRESENTATION_RULES.md
PILOT_DEMO_NARRATIVE.md

All those documents must remain consistent with the principles defined here.

14. Out of Scope for This Architecture Document

This document does not:

define final endpoint names
define exact Base44 page layouts
define detailed component hierarchy
define visual design tokens
implement UI
implement backend changes
change existing FTL backend logic
authorize Scenario 15 execution
authorize any regression reruns
authorize any production release behavior
15. Closure Standard for This Architecture Layer

This architecture layer is considered complete when the following are unambiguous:

Base44 is fixed as a Pilot UI Layer only
backend remains the sole source of product truth
UI/backend boundary is defined in allowed and forbidden terms
read and write flow responsibilities are separated
tenant/user context ownership is clear
trust, error, and permission state architecture is established
the Pilot UI is explicitly connected to the FTL product narrative
future EPIC 33 UI implementation can proceed without risking frontend logic contamination
16. Key Architectural Statement

The InvoMatch Pilot UI exists to reveal backend-governed financial truth, not to manufacture it.

That one sentence should remain the standard against which every later EPIC 33 UI decision is judged.
