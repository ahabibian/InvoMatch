
PILOT SCREEN INVENTORY AND RESPONSIBILITY MAP
Mini-EPIC 33.1 — Pilot Screen Inventory and Responsibility Map
1. Purpose

This document defines the primary screen inventory for the InvoMatch Pilot UI and assigns an explicit product responsibility to each screen.

The purpose is to prevent EPIC 33 from turning into a visually attractive but structurally weak set of disconnected pages.

Each screen must exist for a clear reason, consume backend-owned truth, expose a specific part of the Financial Truth Layer, and support only the operator actions that belong to that product moment.

This document defines:

the required Pilot UI screens
the primary responsibility of each screen
the intended user/operator role
the backend-derived data each screen consumes
the operator actions each screen may trigger
the backend dependency of each screen
the Financial Truth Layer value exposed by each screen
explicit responsibility boundaries that must not be crossed

This document does not design final layouts or visual components.
It defines the functional screen architecture that later Base44 implementation must follow.

2. Screen Inventory Overview

The Pilot UI for EPIC 33 is organized around the end-to-end InvoMatch product story:

Operational overview
        ↓
Financial intake context
        ↓
Review queue
        ↓
Detailed evidence inspection
        ↓
Human correction / decision
        ↓
Finalized truth record
        ↓
Export readiness and trust confirmation

The required screen set is:

Pilot Dashboard
Intake Workspace
Reconciliation Review Queue
Match Detail / Evidence View
Human Correction Screen
Finalized Truth Record / Export Readiness
Tenant / User Context Surface
Error & Trust State Presentation Surface

Some of these are full pages.
Some may be persistent shell elements or shared presentation patterns.
All are part of the Pilot UI architecture.

3. Screen Responsibility Matrix
ScreenPrimary RoleMain FTL SurfaceMain Operator Value
Pilot DashboardProduct/system overviewworkflow state, operational readinessunderstand what needs attention
Intake WorkspaceShow raw intake and processing contextraw input → normalized processingunderstand what entered the system
Reconciliation Review QueuePrioritize items requiring human attentionproposed system decision + review statusdecide what to inspect next
Match Detail / Evidence ViewExplain one reconciliation caseevidence, reasoning, candidate comparisonunderstand why the system proposed an outcome
Human Correction ScreenSubmit governed human intenthuman decision / correction intentapprove, reject, correct, or reassign
Finalized Truth Record / Export ReadinessShow authoritative resolved outcomefinalized truth + lineage + export readinessverify operational trustworthiness
Tenant / User Context SurfaceReinforce scoped product operationtenant and user contextconfirm who is acting in which workspace
Error & Trust State Presentation SurfaceShow blockers, degraded states, restrictionsuncertainty, readiness failure, permissionspreserve trust during non-happy paths
4. Screen 1 — Pilot Dashboard
4.1 Purpose

The Pilot Dashboard provides the operator with a concise overview of the current financial workflow state.

It is the entry point into the demo and the product.
It must immediately communicate that InvoMatch is not merely storing files; it is managing a governed reconciliation pipeline that produces reviewable and export-relevant truth.

4.2 Primary Audience
pilot operator
internal product reviewer
demo viewer
early stakeholder evaluating the value of InvoMatch
4.3 Core Responsibilities

The Pilot Dashboard should surface:

current intake/process status
count of items requiring review
count of finalized truth records
count or presence of export-ready records
blockers or trust warnings
recent workflow activity where backend data supports it
navigation entry into the key operator paths
4.4 Backend-Derived Data Required

The dashboard may consume backend-provided summaries such as:

total open review items
total finalized truth records
export-ready count
unresolved blockers
latest processing run state
degraded or failed system state
tenant-scoped workload summary

The UI must not calculate these totals from raw records unless the backend explicitly provides the computation-ready aggregate in a safe response shape.

4.5 Permitted Operator Actions

The dashboard may allow:

navigate to Intake Workspace
navigate to Review Queue
navigate to Finalized Truth / Export Readiness
inspect current blocker states
open the latest relevant workflow area

It should not perform core workflow mutation directly.

4.6 Forbidden Responsibilities

The Pilot Dashboard must not:

calculate reconciliation outcomes
create review status
infer export readiness
simulate queue prioritization locally
alter financial truth state
duplicate backend operational aggregation logic
4.7 FTL Value Exposed

The dashboard exposes the Financial Truth Layer at the product level by showing:

raw intake is being transformed into workflow state
some records require human adjudication
some records become finalized truth
only validated finalized truth may become export-ready

It is the overview layer of FTL visibility.

5. Screen 2 — Intake Workspace
5.1 Purpose

The Intake Workspace shows what entered the system and how it is positioned within the processing flow.

This screen is important because users must understand the difference between:

raw financial input
backend-processed interpretation
unresolved items that later flow into review

Without this screen, the UI jumps too quickly into reconciliation conclusions and weakens the FTL narrative.

5.2 Primary Audience
operator reviewing incoming financial data
pilot viewer who needs to understand the start of the FTL lifecycle
5.3 Core Responsibilities

The Intake Workspace should surface:

uploaded/imported source batches or financial intake sets
intake status
processing status
normalized record availability where backend exposes it
basic source metadata
whether the intake produced reviewable reconciliation items
navigation from intake context into downstream review
5.4 Backend-Derived Data Required

Possible backend-provided data:

intake batch ID
intake timestamp
tenant scope
source type
processing run state
counts of parsed or normalized items
unresolved or failed processing markers
linkage to related review items

The backend determines what is complete, partial, failed, or pending.

5.5 Permitted Operator Actions

Depending on backend support and EPIC 33 scope, the screen may allow:

view intake batch detail
inspect processing status
navigate to related review queue items
retry or acknowledge a processing state only if later explicitly authorized by backend contract

For the initial Pilot UI, the safest minimum is:

inspect
navigate
do not mutate
5.6 Forbidden Responsibilities

The Intake Workspace must not:

parse raw source records
normalize input client-side
classify processing success itself
decide whether an intake is financially valid
invent derived review item counts
duplicate backend intake pipeline status logic
5.7 FTL Value Exposed

The Intake Workspace exposes:

raw input
processing stage
transition from financial source material into backend-governed product state

It is the UI layer where the Financial Truth Layer begins to become visible.

6. Screen 3 — Reconciliation Review Queue
6.1 Purpose

The Reconciliation Review Queue is the operator’s workbench for unresolved or review-required financial cases.

It must make the pilot feel like a real operational product, not just a static showcase.

This screen is where backend-identified uncertainty becomes a managed human workflow.

6.2 Primary Audience
operational reviewer
finance back-office user
internal pilot tester
6.3 Core Responsibilities

The Review Queue should surface:

items requiring review
review status
short reason for review
proposed system decision summary
evidence availability indicator
urgency or blocking marker where backend provides it
current permitted operator actions at summary level
queue filtering/sorting over backend-safe fields
6.4 Backend-Derived Data Required

Potential backend-provided fields:

review item ID
associated intake or transaction reference
current review state
proposed match summary
confidence/explanation category if backend exposes it
reason review is required
evidence summary
age or timestamp
action availability
export impact or finalization dependency where relevant
6.5 Permitted Operator Actions

The Review Queue may allow:

open match detail
filter by review state
filter by reason category
filter by export blocker state
navigate into correction or decision handling

The queue itself should not silently apply financial decisions.

6.6 Forbidden Responsibilities

The Review Queue must not:

infer which items require review
compute review priorities from raw facts unless explicitly backend-provided
approve or reject via fragile direct inline logic unless routed through deliberate action flows
finalize records
modify candidate matching locally
derive operational truth from visual filter state
6.7 FTL Value Exposed

The Review Queue exposes:

system-proposed financial interpretation
items not yet trustworthy enough to finalize
where human review enters the Financial Truth Layer

This is the first UI point where the user sees that InvoMatch distinguishes between machine proposal and governed truth.

7. Screen 4 — Match Detail / Evidence View
7.1 Purpose

The Match Detail / Evidence View explains a single reconciliation case in enough detail for a human to make a responsible decision.

This screen is central.
If it is weak, InvoMatch looks like a black-box matcher.
If it is strong, the product demonstrates financial explainability.

7.2 Primary Audience
operator making a review decision
stakeholder evaluating product trustworthiness
internal auditor of pilot UX
7.3 Core Responsibilities

The Match Detail / Evidence View should display:

source-side record summary
counterpart candidate or candidate set summary
normalized values as returned by backend
proposed system decision
comparison evidence
mismatch or ambiguity markers
relevant reasoning/explanation blocks
lineage references where appropriate
current review state
permitted next actions
7.4 Backend-Derived Data Required

Possible backend fields:

review item ID
invoice/payment/reference record IDs
normalized amount/date/counterparty/invoice number fields
proposed match result
candidate comparison structure
evidence list
reason codes
unresolved ambiguity markers
existing human correction history if any
action availability
audit references where applicable
7.5 Permitted Operator Actions

The screen may allow:

proceed to approve
proceed to reject
proceed to correct
proceed to manual reassignment
return to queue
inspect linked lineage/evidence references

The actual mutation should occur through dedicated backend-owned action submissions, not through casual client-side status toggles.

7.6 Forbidden Responsibilities

The Match Detail / Evidence View must not:

fabricate reasoning
calculate match scores locally
reorder candidate validity based on frontend logic
generate audit explanation
conclude final state independently
collapse uncertainty just to make the demo look cleaner
7.7 FTL Value Exposed

This screen exposes:

normalized interpretation
proposed system decision
evidence
reasoning
uncertainty

It is the clearest visible proof that InvoMatch is building a Financial Truth Layer, not just a CRUD dashboard.

8. Screen 5 — Human Correction Screen
8.1 Purpose

The Human Correction Screen is where the operator expresses a governed decision or correction intent.

It captures the human-in-the-loop moment and makes clear that the backend remains responsible for evaluating, validating, persisting, and auditing the submitted intent.

8.2 Primary Audience
operational reviewer
user correcting system output
product evaluator assessing real workflow viability
8.3 Core Responsibilities

The Human Correction Screen should support intent submission for actions such as:

approve proposed match
reject proposed match
correct wrong pairing
manually reassign candidate
supply a structured reason where required
confirm decision submission
display backend acceptance/rejection result
8.4 Backend-Derived Data Required

Before submission, the UI needs:

current review item state
permitted actions
required decision fields
candidate options for reassignment if backend provides them
current evidence state
state preconditions
human-readable backend instructions where applicable

After submission, the UI needs:

result state
updated review state
updated truth formation status
next available navigation path
8.5 Permitted Operator Actions

This is the principal write-action screen.

The operator may submit backend-governed intent such as:

approve
reject
correct
reassign
provide review reason/comment where part of contract
8.6 Forbidden Responsibilities

The screen must not:

directly rewrite truth state
create finalized state client-side
decide that a correction is valid before backend confirms
permanently store the decision locally
claim audit trail creation before backend confirms
simulate successful mutation in optimistic UI if backend truth has not returned
8.7 FTL Value Exposed

This screen exposes:

human intervention
human decision as a governed input
the transition from system proposal toward resolved truth

It is the key point where the FTL becomes accountable, not merely automated.

9. Screen 6 — Finalized Truth Record / Export Readiness
9.1 Purpose

The Finalized Truth Record / Export Readiness screen shows the authoritative resolved output of the process.

This screen is where InvoMatch proves that its workflow does not stop at “a user clicked approve.”
It culminates in a backend-owned truth artifact with readiness and audit context.

9.2 Primary Audience
operational reviewer
finance decision-maker
stakeholder evaluating readiness for downstream use
pilot demo audience
9.3 Core Responsibilities

The screen should surface:

finalized truth record summary
original source references
resolved financial interpretation
final status
human review linkage where relevant
evidence/lineage linkage
audit-safe traceability references
export readiness state
blocking reason if not export-ready
downstream-readiness explanation
9.4 Backend-Derived Data Required

Potential backend response fields:

truth record ID
finalization status
finalized financial fields
source lineage
related review item
applied human decision reference
export readiness status
export blocker reason
evidence completeness
timestamps
tenant/user scope
audit reference identifiers
9.5 Permitted Operator Actions

Depending on backend scope, the screen may allow:

inspect final truth
inspect readiness
view blockers
navigate to linked review/evidence context
initiate an export-related path only if a later EPIC 33 contract explicitly authorizes it

For this Pilot UI architecture, the safest intended scope is primarily:

display
verify
navigate
9.6 Forbidden Responsibilities

The screen must not:

determine export readiness from local checks
manufacture finalization status
generate export package logic
alter the truth record
change lineage
act as a persistence layer for exported data
blur the difference between finalized truth and exported artifact
9.7 FTL Value Exposed

This screen exposes:

finalized truth
lineage
audit linkage
export readiness

It is the clearest visible product expression of the Financial Truth Layer as an operational asset.

10. Screen 7 — Tenant / User Context Surface
10.1 Purpose

The Tenant / User Context Surface reinforces that InvoMatch operates within scoped, permission-aware product boundaries.

This may appear as:

persistent header area
compact workspace context panel
screen-level context block

It need not be a standalone navigation destination, but it is a required Pilot UI surface.

10.2 Primary Audience
all authenticated pilot users
product evaluators who need to understand tenant-aware architecture
10.3 Core Responsibilities

The context surface should show backend-provided information such as:

active tenant
active workspace, if modeled
current user label
user role or permission category where useful
pilot/environment indicator if returned by backend
10.4 Backend-Derived Data Required

Potential fields:

tenant ID/display name
user ID/display name
role label
permission profile summary
environment descriptor
10.5 Permitted Operator Actions

At the pilot stage, this surface may allow:

contextual display only
potentially open account/workspace detail if backed by later scope

It should not become a tenant management console inside EPIC 33.1.

10.6 Forbidden Responsibilities

The context surface must not:

determine permissions
switch tenant through unsafe local UI assumptions
fabricate role state
hide unauthorized data client-side instead of relying on backend isolation
make product appear multi-tenant without actual backend grounding
10.7 FTL Value Exposed

This surface does not expose a stage of FTL directly.
Its value is architectural:

it proves truth is tenant-scoped
it reinforces that financial state is not globally or casually visible
it supports the SaaS credibility of the product
11. Screen 8 — Error & Trust State Presentation Surface
11.1 Purpose

The Error & Trust State Presentation Surface defines how non-happy-path conditions appear across the Pilot UI.

This may exist as:

page-level alerts
inline state blocks
queue status markers
empty states
permission explanations
export blockers
recovery banners

It is a shared cross-screen presentation responsibility, not necessarily a single page.

11.2 Primary Audience
every operator using the product
demo stakeholders evaluating whether the system handles uncertainty responsibly
11.3 Core Responsibilities

This surface must support rendering of states such as:

validation error
permission denied
export not ready
failed run
degraded system health
recovery in progress
missing evidence
unresolved review state
no data available
backend unavailable or limited response state
11.4 Backend-Derived Data Required

Backend responses should provide structured signals such as:

error category
user-safe message
affected entity or area
retry availability
whether further workflow is blocked
recovery or next-step indicator
permission restriction cause where safe to disclose
11.5 Permitted Operator Actions

Depending on context:

retry read action
navigate to affected workflow area
review missing evidence
return to queue
inspect blocker explanation

These actions are navigational or backend-governed retries, not local workarounds.

11.6 Forbidden Responsibilities

The UI must not:

hide meaningful blockers
expose raw stack traces
invent recovery status
falsely claim safety or readiness
continue a workflow visually when backend state says it is blocked
smooth over operational uncertainty for demo convenience
11.7 FTL Value Exposed

This surface exposes a critical FTL principle:

Financial truth is only trustworthy when uncertainty, incompleteness, and permission boundaries are made visible rather than concealed.

12. Screen-to-FTL Lifecycle Mapping
FTL Lifecycle StagePilot UI Surface
Raw financial intakeIntake Workspace
Processing / normalization contextIntake Workspace
Proposed system decisionReview Queue, Match Detail
Evidence and reasoningMatch Detail / Evidence View
Human interventionHuman Correction Screen
Finalized truthFinalized Truth Record
Lineage and audit linkageMatch Detail, Finalized Truth Record
Export readinessFinalized Truth Record / Export Readiness
Trust blockers / uncertaintyError & Trust State Presentation Surface
Tenant-scoped truth contextTenant / User Context Surface
13. Recommended Navigation Logic

The Pilot UI should support a coherent navigation flow:

Dashboard
  → Intake Workspace
  → Review Queue
  → Match Detail / Evidence View
  → Human Correction Screen
  → Finalized Truth Record / Export Readiness

Alternative supporting transitions:

Dashboard
  → Review Queue

Review Queue
  → Match Detail

Finalized Truth Record
  → Linked Review / Evidence Context

Trust or Error State
  → Relevant Recovery or Review Area

Navigation should reflect product causality, not just page availability.

14. Screen Design Discipline

Every screen introduced in EPIC 33 must answer five questions before implementation:

What product moment does this screen represent?
What backend truth does it display?
What FTL layer does it expose?
What operator action, if any, does it safely trigger?
What logic is explicitly forbidden from entering this screen?

A screen that cannot answer these questions should not be added.

15. Out of Scope

This document does not:

define final page layouts
define precise Base44 route names
define visual styling
define component libraries
define exact endpoint URLs
define the final API contract schema
authorize custom frontend development
authorize backend redesign
authorize Scenario 15 execution
authorize regression reruns
authorize export implementation
16. Closure Standard

This screen inventory and responsibility map is complete when:

all core Pilot UI surfaces are explicitly defined
each surface has a clear product responsibility
each surface has a defined backend data dependency
each surface has permitted and forbidden behavior
each surface is mapped to its contribution to the Financial Truth Layer
the primary operator journey is screen-level coherent
later Base44 implementation can proceed without inventing screen purpose ad hoc
17. Key Screen Architecture Statement

Every Pilot UI screen must either reveal backend-governed financial truth, enable a governed human decision, or preserve trust around the state of that truth.

Any screen that does none of those three things is not justified within EPIC 33.1.
