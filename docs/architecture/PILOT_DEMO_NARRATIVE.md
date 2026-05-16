
PILOT DEMO NARRATIVE
Mini-EPIC 33.1 — Pilot Demo Narrative
1. Purpose

This document defines the official Pilot Demo Narrative for EPIC 33.

The purpose is to establish the product story that the future InvoMatch Pilot UI must be able to demonstrate clearly, consistently, and without improvisation.

EPIC 33 is not only building screens.
It is building the first product-visible demonstration of the Financial Truth Layer.

Therefore, the demo narrative must make it unmistakable that InvoMatch is not simply:

uploading financial files
showing matched rows
presenting a static dashboard
letting a user click approve

Instead, the Pilot UI must demonstrate a governed product lifecycle:

Financial input enters the system
        ↓
The backend processes and structures it
        ↓
A reconciliation case requiring review becomes visible
        ↓
The system exposes its proposed interpretation and evidence
        ↓
A human operator submits a governed decision or correction
        ↓
The backend confirms the resulting financial truth state
        ↓
A finalized truth record becomes visible
        ↓
Export readiness, lineage, and trust status are shown

This document defines:

the core demo story
the exact narrative sequence
what the audience should understand at each stage
what each screen must contribute to the story
how trust, blockers, and uncertainty fit the demonstration
what the demo must not imply or exaggerate

This document does not build the UI, define exact Base44 layouts, authorize export implementation, or invent backend capabilities that do not exist.

2. Core Demo Principle

The governing principle is:

The Pilot Demo must show how InvoMatch turns financial ambiguity into backend-governed, human-reviewable, traceable financial truth.

The demo is successful only if the audience understands three things:

InvoMatch does not blindly automate decisions.
InvoMatch exposes evidence and human accountability.
InvoMatch produces a more trustworthy downstream financial state than the raw input alone.
3. Demo Narrative in One Paragraph

The canonical EPIC 33 Pilot Demo narrative is:

A financial input enters InvoMatch and is processed into structured backend state. The system identifies a reconciliation case that requires human review instead of silently forcing a conclusion. The operator opens that case, inspects the system’s proposed interpretation, sees the supporting evidence and any uncertainty, and submits a governed decision or correction. The backend evaluates that intent, updates the authoritative state, and exposes the resulting finalized truth record when the case satisfies the required conditions. The UI then shows whether that truth record is export-ready and how it remains traceable through evidence, lineage, and audit linkage.

This paragraph is the reference narrative for later UI implementation, demo scripts, and pilot-facing presentation.

4. Demonstration Goals

The Pilot Demo must communicate the following product claims through actual screen flow.

4.1 Product Claim 1 — Financial Input Is Not Yet Financial Truth

The audience must see that raw intake is the starting point, not the conclusion.

The demo should show:

a financial source or intake context
processing state
the idea that backend-governed interpretation occurs after intake
4.2 Product Claim 2 — The System Creates a Proposed Interpretation, Not an Unchallengeable Verdict

The audience must see:

a review-required case
a proposed system interpretation
a visible distinction between proposal and finalized truth
4.3 Product Claim 3 — Evidence Makes the System Explainable

The audience must see:

evidence supporting the system proposal
reasons for review
ambiguity or incomplete support where relevant
4.4 Product Claim 4 — Human Review Is Governed, Not Cosmetic

The audience must see:

a deliberate operator decision or correction step
that action is submitted to backend governance
the UI does not directly manufacture truth
4.5 Product Claim 5 — Finalized Truth Is a Distinct Backend State

The audience must see:

a finalized truth record as a separate state
its relation to earlier review and evidence
that backend state, not UI optimism, defines completion
4.6 Product Claim 6 — Export Readiness Is Explicit, Not Assumed

The audience must see:

whether the truth record is export-ready
if blocked, why
that readiness is backend-owned and not a visual badge invented by the UI
4.7 Product Claim 7 — Trust Is Preserved by Showing Blockers Honestly

The audience must understand that InvoMatch is trustworthy because it can show:

review required
missing evidence
unresolved state
export not ready
permission or blocker states where relevant
5. Canonical Demo Sequence

The canonical Pilot Demo should follow this sequence unless a later explicitly documented variation is justified.

Stage 1 — Open the Pilot Dashboard
Narrative Purpose

Set the product context.

The audience should immediately understand that InvoMatch is managing a financial workflow with:

intake activity
review work
finalized truth records
export readiness state
blockers where relevant
Primary Screen
Pilot Dashboard
What to Show

The demo should display some combination of:

current review workload
finalized truth record count
export-ready or export-blocked summary
latest intake/processing context
trust or blocker indicator where relevant
What the Audience Should Understand

InvoMatch is an operational product layer, not a single-screen file viewer.

What Must Not Be Implied

The demo must not imply:

the dashboard itself makes financial decisions
all records are automatically trustworthy
counts or readiness are frontend-derived
Stage 2 — Enter Intake Workspace
Narrative Purpose

Show where the financial workflow begins.

The audience should see that records entered the system before being reviewed or reconciled.

Primary Screen
Intake Workspace
What to Show

The demo should show:

a source intake batch or equivalent backend-defined intake context
intake status
processing or normalization status
connection to downstream review work where available
What the Audience Should Understand

The Financial Truth Layer starts from raw or imported financial material, but raw input alone is not the truth state.

What Must Not Be Implied

The demo must not imply:

uploading a record automatically finalizes it
frontend parsing defines financial reality
processing completeness is assumed rather than backend-owned
Stage 3 — Open the Reconciliation Review Queue
Narrative Purpose

Introduce the core problem InvoMatch solves: not every financial case should be silently finalized.

Primary Screen
Reconciliation Review Queue
What to Show

The demo should show:

one or more review-required cases
review status
a reason for review
a summary of the system proposal
evidence state indicator
any export/finalization blocker where useful
What the Audience Should Understand

InvoMatch surfaces uncertainty as governed work rather than hiding it.

What Must Not Be Implied

The demo must not imply:

queue membership is frontend-calculated
review is cosmetic
every system proposal is automatically accepted
Stage 4 — Open Match Detail / Evidence View
Narrative Purpose

Reveal the product’s explainability.

The audience should see not just what the system proposes, but why.

Primary Screen
Match Detail / Evidence View
What to Show

The demo should show:

relevant source and candidate records
normalized values where relevant
proposed system interpretation
supporting evidence
mismatches or uncertainty if present
reason review is required
permitted next actions
What the Audience Should Understand

InvoMatch supports operator judgment through evidence, not through opaque automation.

What Must Not Be Implied

The demo must not imply:

evidence is invented by the frontend
visual similarity equals financial truth
uncertainty disappears merely because the screen looks polished
Stage 5 — Enter Human Correction Screen
Narrative Purpose

Show governed human intervention.

The operator now responds to the backend-provided case through an explicit, accountable decision flow.

Primary Screen
Human Correction Screen
What to Show

The demo may show one of the supported action paths:

approve proposed match
reject proposal
correct the outcome
manually reassign where backend permits it

The preferred default demo path is:

Operator inspects evidence
        ↓
Operator submits a governed approve or correction intent
What the Audience Should Understand

Human review is not a decorative step. It is a structured contribution to backend-governed financial truth.

What Must Not Be Implied

The demo must not imply:

clicking a button itself changes truth
the frontend decides whether a correction is valid
operator action automatically creates final truth before backend confirmation
Stage 6 — Show Backend Acceptance or Rejection Outcome
Narrative Purpose

Make backend authority visible.

After the operator submits intent, the UI must display the backend-confirmed outcome.

Primary Surface
Human Correction Screen, followed by
refreshed authoritative state
What to Show

Depending on backend result, the UI should show:

action accepted
action rejected
validation issue
stale/conflict state
permission denial
or progression into updated review/finalization state

For the preferred happy-path demo, show:

The backend accepts the operator intent.
The UI refreshes and displays the resulting authoritative state.
What the Audience Should Understand

The UI submits intent. The backend decides and returns truth.

What Must Not Be Implied

The demo must not imply:

optimistic UI success is truth
backend confirmation is optional
state refresh can be skipped
Stage 7 — Open Finalized Truth Record
Narrative Purpose

Show the resolved product outcome.

The audience should see the difference between:

system proposal
human review
finalized backend truth
Primary Screen
Finalized Truth Record / Export Readiness
What to Show

The demo should show:

finalized truth record
resolved financial interpretation
connection to prior review and decision context
lineage or audit references where available
finalization status
What the Audience Should Understand

InvoMatch produces a traceable financial truth artifact, not merely a temporary screen state.

What Must Not Be Implied

The demo must not imply:

finalization is the same as a local UI approval
lineage is optional decoration
finalized truth exists if backend has not actually created it
Stage 8 — Show Export Readiness
Narrative Purpose

Show downstream trust and operational usefulness.

The demo should conclude by showing that the truth record has an explicit readiness state for downstream use.

Primary Screen
Finalized Truth Record / Export Readiness
What to Show

The UI should show either:

export-ready status
or
export-blocked status with clear reason

The preferred main demo path may use a ready state if the backend supports it.
A blocked readiness state is also a valid demo if the purpose is to demonstrate trust-preserving behavior.

What the Audience Should Understand

Export readiness is governed, explicit, and separate from visual completion.

What Must Not Be Implied

The demo must not imply:

export has executed
readiness is guessed by UI
a visually complete record is automatically downstream-safe
6. Preferred Main Demo Path

The recommended default Pilot Demo path is:

1. Dashboard shows pending review work and FTL progress context
2. Intake Workspace shows the financial source and processing context
3. Review Queue shows a review-required reconciliation case
4. Match Detail shows the system proposal and evidence
5. Human Correction Screen submits a governed operator decision
6. Backend confirms the action and the UI refreshes
7. Finalized Truth Record becomes visible
8. Export Readiness is shown with lineage and trust context

This path provides the strongest compact demonstration of the InvoMatch value proposition.

7. Valid Alternative Demo Path — Blocker Demonstration

A second valid demo path should remain available for product honesty:

1. Dashboard shows review work and a trust blocker
2. Review Queue shows a case with missing evidence
3. Match Detail exposes the missing evidence state
4. Human action is unavailable or constrained
5. Finalized truth is not falsely shown
6. Export readiness remains blocked with a clear reason

This path is valuable because it demonstrates:

the product refuses to fabricate certainty
the UI preserves truth under uncertainty
the Financial Truth Layer is governable, not theatrical
8. Demo Screen Contribution Matrix
Demo StagePrimary ScreenProduct Story Contribution
Operational contextDashboardShows workflow state and product seriousness
Financial originIntake WorkspaceShows raw input and processing context
Review obligationReview QueueShows that uncertainty becomes managed work
ExplainabilityMatch Detail / EvidenceShows proposal, evidence, and ambiguity
Human accountabilityHuman CorrectionShows governed operator action
Backend authorityAction response + refreshShows truth mutation is backend-owned
Resolved outcomeFinalized Truth RecordShows authoritative financial truth
Downstream readinessExport ReadinessShows explicit operational trust state
9. Demo Narrative and FTL Surface Alignment

The demo must cover the FTL surfaces already defined in Mini-EPIC 33.1:

FTL SurfaceDemo Stage
Raw Financial InputIntake Workspace
Processing / NormalizationIntake Workspace
Proposed System InterpretationReview Queue, Match Detail
Evidence and ReasoningMatch Detail
Human Review and CorrectionHuman Correction Screen
Finalized Truth RecordFinalized Truth Screen
Lineage and Audit LinkageFinalized Truth Screen, Match Detail
Export ReadinessFinalized Truth / Export Readiness
Trust BlockersAlternate blocker demo path or contextual warnings

The demo must not skip these surfaces unless a later explicitly documented narrower demonstration mode is created.

10. Demo Narrative and Operator Workflow Alignment

The Pilot Demo Narrative must remain consistent with:

OPERATOR_WORKFLOW_DEFINITION.md
PILOT_SCREEN_INVENTORY_AND_RESPONSIBILITY_MAP.md
FTL_SURFACE_DEFINITION.md
INITIAL_API_TO_SCREEN_MAPPING_FRAMEWORK.md
TRUST_ERROR_AND_PERMISSION_PRESENTATION_RULES.md

The narrative is not a separate marketing story.
It is the presentation-facing rendering of the already-defined product workflow architecture.

11. Demo Language Discipline

When presenting the Pilot UI later, messaging should emphasize:

backend-governed truth
evidence-supported interpretation
human accountability
explicit readiness
trust-preserving blockers

Preferred conceptual language:

“proposed interpretation”
“review-required case”
“evidence-backed decision context”
“governed operator action”
“finalized truth record”
“export readiness”
“traceability”
“backend-confirmed state”

Avoid overclaiming language such as:

“AI solved it”
“everything is automated”
“one click and done”
“guaranteed perfect match”
“instant export” unless separately implemented and proven
12. Demo Risk Controls

The following risks must be actively avoided.

12.1 Risk — UI Looks Better Than Product Truth

The demo must not use visual polish to mask unresolved backend capability gaps.

12.2 Risk — FTL Becomes a Buzzword

The demo must visibly show each FTL stage, not merely mention FTL in a headline.

12.3 Risk — Human Review Looks Optional or Fake

The demo must make the human-in-the-loop step structurally meaningful.

12.4 Risk — Finalization and Export Readiness Are Blurred

The demo must preserve the difference between:

reviewed
finalized
export-ready
12.5 Risk — Blockers Are Hidden to Improve Presentation

The demo must prefer operational honesty over theatrical smoothness.

13. What the Pilot Demo Should Leave the Audience Believing

At the end of the demonstration, the audience should reasonably conclude:

InvoMatch can organize financial intake into a governed review workflow.
It exposes system proposals rather than hiding how decisions emerge.
It provides evidence for human review.
It treats human correction as part of a controlled financial truth process.
It produces finalized backend-owned truth records where conditions are satisfied.
It makes export readiness explicit rather than assumed.
It is moving toward a credible B2B Financial Truth Layer product, not just a narrow matching widget.
14. What the Pilot Demo Must Not Claim

The demo must not claim:

all financial decisions are automatically correct
all records become finalized without review
export functionality has been implemented if only readiness is shown
UI approval equals backend finalization without confirmation
evidence is optional to truth formation
Base44 owns product decision state
EPIC 33 already delivers the full commercial product

The Pilot Demo should be strong, but not dishonest.

15. Out of Scope

This document does not:

implement Base44 pages
define screen layout details
define demo choreography timing or spoken presenter script
authorize export implementation
authorize export execution
authorize backend redesign
authorize Scenario 15 execution
authorize regression reruns
authorize deployment, release, or public artifact publication
16. Closure Standard

This Pilot Demo Narrative is complete when:

the full product story from intake to finalized truth and export readiness is explicitly defined
the canonical demo sequence is documented
each stage is tied to a Pilot UI screen
the audience takeaway for each stage is defined
forbidden demo implications are documented
the preferred happy-path demonstration is clear
a valid blocker-focused demonstration path is also defined
the narrative aligns with the operator workflow and FTL surface definitions
future Base44 implementation can be evaluated against this fixed demonstration story
17. Key Demo Narrative Statement

The Pilot Demo is successful only when it proves that InvoMatch can make financial ambiguity visible, governable, reviewable, and progressively convertible into traceable truth.

A demo that merely shows attractive screens, static metrics, or an unexplained “match approved” moment does not meet the EPIC 33 product demonstration standard.
