
OPERATOR WORKFLOW DEFINITION
Mini-EPIC 33.1 — Operator Workflow Definition
1. Purpose

This document defines the end-to-end operator workflow for the InvoMatch Pilot UI within EPIC 33.

The purpose is to ensure that the Pilot UI is not designed merely as a set of isolated screens, but as a coherent product flow that demonstrates how an operator moves through the Financial Truth Layer lifecycle:

Operational status
        ↓
Intake context
        ↓
Review-required reconciliation case
        ↓
Evidence inspection
        ↓
Governed human decision or correction
        ↓
Finalized truth record
        ↓
Export readiness and traceability visibility

This document establishes:

the primary operator journey that the Pilot UI must support
the role of each screen in the flow
the entry, transition, decision, refresh, and stop conditions
where backend truth must be re-read after operator action
how blockers, permission restrictions, missing evidence, and unresolved states interrupt the flow
how the workflow makes the Financial Truth Layer visible as a product experience

This document does not implement UI screens, define exact API routes, or authorize new backend behavior.
It defines the workflow model that later Base44 implementation and pilot demo construction must follow.

2. Core Workflow Principle

The governing principle is:

The operator workflow must show how backend-governed financial uncertainty becomes reviewed, traceable, finalized truth without allowing the UI to manufacture that truth.

The workflow must therefore preserve the following distinctions:

system status is backend-owned
review queue membership is backend-owned
evidence is backend-owned
operator action is submitted as intent
action validity is backend-owned
finalized truth is backend-owned
export readiness is backend-owned

The UI guides the operator through the journey.
It does not replace the backend decision system.

3. Primary Operator Workflow Overview

The core operator flow for EPIC 33 is:

1. Open Pilot Dashboard
2. Inspect system and workload state
3. Enter Intake Workspace if source/process context is needed
4. Open Reconciliation Review Queue
5. Select a review-required case
6. Inspect Match Detail / Evidence View
7. Move into Human Correction Screen if decision is required
8. Submit approve / reject / correct / reassign intent
9. Wait for backend acceptance or rejection
10. Refresh from authoritative backend state
11. Inspect resulting Finalized Truth Record where available
12. Inspect Export Readiness, lineage, and trust status

This is the foundational Pilot UI product journey.

4. Workflow Stage 1 — Enter Pilot Dashboard
4.1 Operator Objective

The operator begins by understanding:

what is happening in the financial workflow
whether review work is pending
whether finalized truth records exist
whether export-ready records exist
whether any trust or operational blockers are active
4.2 Primary Screen
Pilot Dashboard
4.3 Required Backend Truth

The Dashboard must display backend-provided summaries such as:

open review item count
finalized truth count
export-ready count
unresolved blocker count
latest intake or processing status
degraded or failed health indicators where relevant
4.4 Main Operator Decisions

From the Dashboard, the operator may decide to:

inspect intake and processing context
go directly to the Review Queue
inspect finalized truth/export readiness context
inspect trust or blocker indicators
4.5 Transition Options

Recommended transitions:

Dashboard → Intake Workspace
Dashboard → Review Queue
Dashboard → Finalized Truth / Export Readiness
Dashboard → Relevant trust/blocker context
4.6 Workflow Discipline

The Dashboard is an orientation screen.
It must not become a direct financial decision screen.

It may direct attention.
It must not mutate reconciliation state.

5. Workflow Stage 2 — Inspect Intake Workspace
5.1 Operator Objective

The operator enters intake context when they need to understand:

what financial source material entered the system
whether processing completed, failed, or remains pending
whether intake gave rise to review-required items
whether the downstream reconciliation workflow is grounded in visible source context
5.2 Primary Screen
Intake Workspace
5.3 Required Backend Truth

The screen must use backend-provided state such as:

intake batch identifier
intake timestamp
source type
processing status
normalization availability
partial or failed processing markers
downstream review linkage where available
5.4 Main Operator Decisions

The operator may:

inspect a specific intake batch
understand whether processing is complete
move into related Review Queue context
return to Dashboard
5.5 Transition Options

Recommended transitions:

Dashboard → Intake Workspace
Intake Workspace → Review Queue
Intake Workspace → Dashboard
5.6 Stop Conditions

The flow should visibly stop or redirect if:

processing has failed
intake remains incomplete
required source state is unavailable
permission prevents intake visibility

In those conditions, the UI must not pretend the downstream review flow is healthy.

5.7 Workflow Discipline

The Intake Workspace clarifies financial origin and process state.
It does not perform reconciliation decisions and does not infer readiness.

6. Workflow Stage 3 — Enter Reconciliation Review Queue
6.1 Operator Objective

The operator enters the Review Queue to identify cases that require human attention.

This is the operational heart of the pilot because it shows that:

the system does not blindly finalize uncertain financial interpretations
unresolved cases are explicitly surfaced
operator work is prioritized around backend-defined review states
6.2 Primary Screen
Reconciliation Review Queue
6.3 Required Backend Truth

The queue must display backend-shaped review item summaries including:

review item ID
review status
reason review is required
proposed system interpretation summary
evidence state summary
export/finalization blocker markers where available
permitted next actions
timestamps or age indicators where useful
6.4 Main Operator Decisions

The operator may:

filter queue items
locate a relevant or urgent item
open a selected review case
return to Dashboard
6.5 Transition Options

Recommended transitions:

Dashboard → Review Queue
Intake Workspace → Review Queue
Review Queue → Match Detail / Evidence View
Review Queue → Dashboard
6.6 Stop Conditions

The queue must handle:

empty queue
permission denial
queue load failure
filtered no-result state
stale or unavailable queue state

An empty queue is not an error.
A failed or inaccessible queue is an operational state that must be clearly shown.

6.7 Workflow Discipline

The queue is for selecting work, not quietly performing final decisions.
It may direct the operator toward action, but it must not shortcut governed review.

7. Workflow Stage 4 — Inspect Match Detail and Evidence
7.1 Operator Objective

The operator opens a specific reconciliation case to understand:

what raw or normalized records are involved
what the system currently proposes
why the system proposes it
what evidence supports or weakens it
whether a human decision is required
what actions are currently permitted
7.2 Primary Screen
Match Detail / Evidence View
7.3 Required Backend Truth

This screen must display backend-provided detail such as:

source record summary
candidate or counterpart summary
normalized financial values
proposed system decision
evidence blocks
reasoning categories or user-safe explanations
mismatch markers
ambiguity markers
evidence completeness state
permitted actions
current review state
lineage/audit references where relevant
7.4 Main Operator Decisions

The operator may decide to:

approve the current proposal
reject the proposal
correct or manually reassign
defer decision by returning to the queue
inspect linked lineage or intake context where supported
7.5 Transition Options

Recommended transitions:

Review Queue → Match Detail / Evidence View
Match Detail / Evidence View → Human Correction Screen
Match Detail / Evidence View → Review Queue
Match Detail / Evidence View → Intake Workspace where source context is linked
7.6 Stop Conditions

The flow must visibly stop or restrict action if:

evidence is missing
the item is stale
the review item no longer exists
the operator lacks permission
the case is structurally blocked
the backend marks action as unavailable

The UI must not let the operator proceed visually where backend truth prevents a valid workflow transition.

7.7 Workflow Discipline

The Match Detail view is a decision-support surface.
It is not a decision-authority surface.

The operator sees and interprets backend-provided truth.
The backend remains responsible for action validity.

8. Workflow Stage 5 — Enter Human Correction Screen
8.1 Operator Objective

The operator moves into a governed decision context to submit one of the supported intent types:

approve proposed match
reject proposed match
correct the case
manually reassign where permitted

This is the formal human-in-the-loop contribution to the Financial Truth Layer.

8.2 Primary Screen
Human Correction Screen
8.3 Required Backend Truth Before Action

Before submission, the screen must show backend-owned constraints such as:

current review item state
currently permitted actions
current proposal summary
required fields for the selected action
valid candidate options where reassignment is allowed
blocked reason if an action path is unavailable
8.4 Main Operator Decisions

The operator chooses:

action type
correction or reassignment target where relevant
structured reason/comment where required by backend contract
whether to submit or cancel
8.5 Write Flow Requirement

The UI submits:

operator intent

The backend decides:

whether the intent is accepted, rejected, conflicted, blocked, or invalid

The UI must not treat the operator’s click as equivalent to truth mutation.

8.6 Transition Options

Recommended transitions:

Match Detail / Evidence View → Human Correction Screen
Human Correction Screen → Match Detail / Evidence View after rejected/blocked action
Human Correction Screen → Finalized Truth Record where backend truth becomes available
Human Correction Screen → Review Queue where the item remains unresolved
8.7 Backend Response Handling

After action submission, the UI must handle backend outcomes such as:

action accepted
action rejected
validation failed
permission denied
stale/conflicting review state
action accepted but truth not yet finalized
action accepted and final truth now available
8.8 Mandatory Refresh Rule

After every operator action:

The UI must refresh from backend-authoritative state before presenting the resulting workflow outcome.

No optimistic truth mutation is permitted.

8.9 Workflow Discipline

This screen is where human accountability enters the flow.
It must feel deliberate, not casual.

A correction is not “editing a row.”
It is a governed product decision event.

9. Workflow Stage 6 — Inspect Finalized Truth Record
9.1 Operator Objective

After a valid review/correction flow, the operator inspects whether the backend has produced a finalized truth record.

The operator should be able to understand:

what the final resolved financial truth is
how it relates to prior source, evidence, and review activity
whether finalization occurred
whether the record is still blocked or unresolved
9.2 Primary Screen
Finalized Truth Record / Export Readiness
9.3 Required Backend Truth

The screen must display backend-provided information such as:

finalized truth record ID
finalization status
resolved financial interpretation
linked review decision
lineage references
evidence traceability
audit references where available
timestamp of finalization
tenant context
9.4 Main Operator Decisions

At this stage, the operator primarily:

verifies final truth state
inspects traceability
understands whether downstream readiness exists
navigates back to linked evidence/review if needed
9.5 Transition Options

Recommended transitions:

Human Correction Screen → Finalized Truth Record
Finalized Truth Record → Match Detail / Evidence View
Finalized Truth Record → Review Queue where unresolved dependencies remain
Finalized Truth Record → Dashboard
9.6 Stop Conditions

The finalized truth stage must show a clear stop condition if:

truth has not been finalized
finalization remains blocked
lineage is incomplete
linked evidence is insufficient
the operator lacks access
truth state cannot be loaded

The UI must not force a “successful ending” if backend truth has not reached one.

9.7 Workflow Discipline

Finalized truth is a backend-owned product state.
It is not simply the visual consequence of a button click.

10. Workflow Stage 7 — Inspect Export Readiness
10.1 Operator Objective

The operator inspects whether the finalized truth record is export-ready or still blocked.

This provides the final operational reassurance in the Pilot UI story:

reconciliation has moved beyond proposal
human review has been accounted for
a truth artifact exists
downstream readiness is explicitly visible
10.2 Primary Screen
Finalized Truth Record / Export Readiness
10.3 Required Backend Truth

The screen must display:

export readiness status
blocker reason if not ready
evidence completeness dependency where relevant
finalization dependency status
unresolved review dependency where relevant
user-safe operational explanation
10.4 Main Operator Decisions

Within Mini-EPIC 33.1, the operator may:

inspect readiness
understand blockers
navigate to linked evidence or review context

The operator does not perform export execution in this workflow definition.

10.5 Transition Options

Recommended transitions:

Finalized Truth Record → Export Readiness section
Export Readiness blocked → Linked Match Detail / Review Context
Export Readiness ready → Dashboard or narrative completion
10.6 Stop Conditions

The workflow stops in a blocked state if:

export readiness is false
evidence remains incomplete
truth record is not finalized
review dependency is unresolved
backend readiness data is unavailable

This is acceptable.
A credible pilot must show governed blockers, not just ideal outcomes.

10.7 Workflow Discipline

Export readiness is a backend truth state, not an export operation.
This document does not authorize export implementation or export execution.

11. End-to-End Core Operator Flow

The canonical Pilot UI workflow should be represented as:

Dashboard
  ↓
Review workload or intake context identified
  ↓
Intake Workspace, when source/process context is needed
  ↓
Reconciliation Review Queue
  ↓
Match Detail / Evidence View
  ↓
Human Correction Screen
  ↓
Backend action acceptance/rejection
  ↓
Authoritative state refresh
  ↓
Finalized Truth Record / Export Readiness

A minimal successful truth-formation path is:

Dashboard
  → Review Queue
  → Match Detail
  → Human Correction
  → Backend accepts decision
  → Finalized Truth Record
  → Export Readiness visible

A valid blocked path is:

Dashboard
  → Review Queue
  → Match Detail
  → Missing evidence or unavailable action
  → Trust/blocker state shown
  → No false finalization shown

Both are legitimate product demonstrations.

12. Workflow Branches
12.1 Standard Approval Branch
Review Queue
  → Match Detail
  → Operator approves proposed match
  → Backend validates and accepts
  → UI refreshes authoritative state
  → Finalized Truth Record becomes available if backend finalization succeeds
  → Export Readiness shown
12.2 Rejection Branch
Review Queue
  → Match Detail
  → Operator rejects proposed match
  → Backend validates and accepts/rejects
  → UI refreshes
  → Case may remain unresolved or move to alternative backend-defined state

The UI must not fabricate what happens after rejection.

12.3 Correction Branch
Review Queue
  → Match Detail
  → Human Correction Screen
  → Operator submits corrected financial decision
  → Backend validates correction
  → UI refreshes
  → Updated review/finalization truth is shown
12.4 Manual Reassignment Branch
Review Queue
  → Match Detail
  → Human Correction Screen
  → Operator selects backend-permitted alternate candidate
  → Backend validates reassignment
  → UI refreshes
  → New truth/review state is shown
12.5 Blocked Evidence Branch
Review Queue
  → Match Detail
  → Evidence incomplete
  → UI shows blocker
  → Action unavailable where backend says unavailable
  → No finalized truth shown
12.6 Permission Restricted Branch
Any relevant screen
  → Backend denies action or read
  → UI shows permission-aware state
  → UI does not simulate continuation
13. Required Workflow Refresh Points

The Pilot UI must refresh backend state after:

action submission on Human Correction Screen
any backend-reported conflict or stale review item condition
any transition from correction outcome to Finalized Truth Record
any drill-down from Dashboard summary into detailed workflow area where real-time state matters
13.1 Why Refresh Is Mandatory

Without refresh, the UI risks:

displaying stale queue state
implying a correction succeeded when it did not
showing wrong finalization status
displaying incorrect export readiness
desynchronizing screen narrative from backend truth

This would directly violate EPIC 33’s backend-truth boundary.

14. Workflow Stop-State Rules

A workflow should visibly pause or stop when the backend indicates:

unresolved review state
missing evidence
failed processing
permission denied
stale/conflicting decision attempt
export not ready
system degraded in a way that affects trust
required downstream truth not available

In these states, the UI must provide:

clear status
clear affected area
clear next visible path where one exists
no false success messaging
15. Operator Workflow and FTL Demonstration

The workflow is successful when it demonstrates all of the following through actual screen transitions:

FTL ValueWorkflow Evidence
Raw input existsIntake Workspace
Processing occursIntake Workspace
System proposal existsReview Queue, Match Detail
Evidence supports or weakens proposalMatch Detail
Human judgment is governedHuman Correction Screen
Backend truth is refreshedPost-action reload
Finalized truth may emergeFinalized Truth Record
Export readiness is explicitExport Readiness section
Blockers are honestTrust/Error surfaces
16. Pilot Demo Flow Alignment

This workflow definition is the operational basis for the later Pilot Demo Narrative.

The demo should not invent a different story.
It should narrate this workflow:

A financial case enters the system.
The system processes it.
A review-required interpretation appears.
The operator inspects evidence.
The operator submits a governed decision.
The backend confirms the resulting truth state.
A finalized truth record and export readiness status become visible.

If the UI cannot support this flow, the EPIC 33 Pilot UI is not yet product-coherent.

17. Out of Scope

This document does not:

implement Base44 screens
define exact route names
define final API URLs or payload schemas
authorize new backend workflow transitions
authorize export execution
authorize export implementation
authorize Scenario 15 execution
authorize regression reruns
authorize deployment, release, or public artifact publication
18. Closure Standard

This operator workflow definition is complete when:

the end-to-end operator journey is explicitly defined
each major workflow stage is tied to a Pilot UI surface
dashboard, intake, queue, detail, correction, finalized truth, and export readiness roles are clear
backend truth refresh points are explicitly defined
blocked, permission-denied, and unresolved paths are treated as valid workflow states
operator intent and backend truth mutation remain clearly separated
the workflow aligns with the Financial Truth Layer lifecycle
later Pilot UI implementation can follow this flow without inventing product behavior ad hoc
19. Key Operator Workflow Statement

The Pilot UI workflow is correct only when it guides an operator from backend-visible uncertainty to backend-confirmed truth without letting the frontend pretend that truth has already been created.

Any EPIC 33 screen transition or interaction pattern that bypasses that principle weakens the product architecture.
