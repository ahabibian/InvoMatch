
FTL SURFACE DEFINITION
Mini-EPIC 33.1 — Financial Truth Layer Surface Definition
1. Purpose

This document defines how the Financial Truth Layer (FTL) must become visible through the InvoMatch Pilot UI.

The purpose is to prevent the FTL from remaining only an internal architecture term or backend abstraction.
EPIC 33 must make the FTL understandable, inspectable, and demonstrable through product surfaces that reveal how raw financial input becomes governed financial truth.

This document defines:

which stages of the FTL lifecycle must appear in the Pilot UI
where each stage is surfaced
what product meaning each surface communicates
what backend-derived information is needed
how the FTL must be represented without leaking business logic into the UI
which frontend shortcuts are forbidden because they would weaken or falsify the FTL story

This document does not implement UI pages, define exact API endpoints, or redesign FTL backend architecture.
It defines the visible product expression of the FTL for EPIC 33.

2. Core FTL Surface Principle

The central principle for EPIC 33 is:

The Financial Truth Layer must be visible as a lifecycle, not as a label.

The Pilot UI must allow a user, reviewer, or demo audience to understand the progression:

Raw Financial Input
        ↓
Backend Processing / Normalization
        ↓
Proposed System Interpretation
        ↓
Evidence and Reasoning
        ↓
Human Review or Correction
        ↓
Finalized Truth Record
        ↓
Lineage, Audit Linkage, and Export Readiness

The FTL is only successfully surfaced if the UI makes these stages clearly distinguishable.

3. FTL Lifecycle Surface Map
FTL StageProduct MeaningPrimary UI Surface
Raw financial inputWhat entered the system before truth formationIntake Workspace
Processing / normalizationHow input became structured backend stateIntake Workspace, Match Detail
Proposed system interpretationWhat the system currently believesReview Queue, Match Detail
Evidence and reasoningWhy that interpretation existsMatch Detail / Evidence View
Human review / correctionHow accountable human judgment enters the flowHuman Correction Screen
Finalized truth recordThe resolved backend-governed financial outcomeFinalized Truth Record
Lineage and audit linkageWhy the truth is traceable and reviewableMatch Detail, Finalized Truth Record
Export readinessWhether resolved truth is downstream-readyFinalized Truth Record / Export Readiness
Trust blockersWhy truth is not yet complete or usableError & Trust State Surface
4. Surface 1 — Raw Financial Input
4.1 Product Meaning

Raw financial input represents the pre-truth state of the workflow.

It is the financial material that entered InvoMatch before normalization, matching, review, or finalization.

This may include:

imported invoice records
imported payment records
source batches
financial source files or input sessions
source metadata relevant to processing context

The Pilot UI must make it clear that raw input is not yet financial truth.

4.2 Primary UI Surface

Raw financial input is primarily surfaced in:

Intake Workspace

It may also be referenced downstream in:

Match Detail / Evidence View
Finalized Truth Record, through source lineage references
4.3 Required Backend-Derived Information

The UI may need backend-provided information such as:

source batch identifier
intake timestamp
source type
number of source records
processing state
tenant context
linkage to downstream processed entities
source validation or processing warnings where available
4.4 Required UI Communication

The UI should communicate:

this is what entered the system
this input may or may not already be processed
this input is not itself the finalized truth state
downstream FTL stages are derived through backend-governed processing
4.5 Forbidden Frontend Behavior

The UI must not:

parse raw input itself
infer normalization status from visual assumptions
declare input valid beyond backend-confirmed state
treat an uploaded or imported source as a finalized financial record
invent downstream matching context before backend provides it
5. Surface 2 — Processing and Normalization
5.1 Product Meaning

Processing and normalization represent the point at which raw financial input becomes structured backend-operational state.

This includes backend handling such as:

intake acceptance or rejection
structured record extraction where already part of the system
normalized financial fields
processing completeness or failure state
readiness for reconciliation workflows

This is the beginning of truth formation, but it is still not final truth.

5.2 Primary UI Surfaces

Processing and normalization may be surfaced in:

Intake Workspace
Match Detail / Evidence View

The Intake Workspace shows processing at the intake or batch level.
The Match Detail view shows normalized values in the context of a specific review case.

5.3 Required Backend-Derived Information

Backend responses may provide:

processing status
normalized amount
normalized date
normalized supplier/counterparty data
normalized invoice number or reference fields
incomplete/missing normalization markers
processing failure reasons in user-safe form
downstream review linkage
5.4 Required UI Communication

The UI should communicate:

the system has transformed raw material into structured interpretation
normalized data is backend-generated
normalization may still contain uncertainty or incompleteness
downstream reconciliation and review operate on this structured representation
5.5 Forbidden Frontend Behavior

The UI must not:

normalize financial fields locally
fix dates, amounts, or references on its own
fill missing data through frontend guessing
imply normalization certainty where backend indicates ambiguity
use frontend formatting as a substitute for backend normalization
6. Surface 3 — Proposed System Interpretation
6.1 Product Meaning

The proposed system interpretation is the point where InvoMatch presents its current machine-generated understanding of a financial relationship.

Examples may include:

a proposed invoice-to-payment match
a recommended reconciliation outcome
an unresolved candidate set requiring review
a status indicating insufficient confidence for automatic finalization

This surface is critical because it separates:

system proposal
from
final truth

That distinction must never be blurred.

6.2 Primary UI Surfaces

The proposed system interpretation is surfaced in:

Reconciliation Review Queue
Match Detail / Evidence View

The Review Queue summarizes cases requiring attention.
The Match Detail view presents the proposal in context.

6.3 Required Backend-Derived Information

The UI may require:

proposed status
proposed match candidate
review-required flag
proposal reason category
unresolved ambiguity marker
high-level confidence/explanation category if backend exposes it
permitted next actions
whether finalization is currently blocked
6.4 Required UI Communication

The UI must communicate:

this is the system's current interpretation
this interpretation is not equivalent to finalized truth
some proposals require human confirmation or correction
the system is explicit about uncertainty where present
6.5 Forbidden Frontend Behavior

The UI must not:

transform a proposal into final truth through labeling
display an unreviewed proposal as if it were approved
locally determine whether a proposal is “good enough”
use color or copy to exaggerate confidence beyond backend truth
hide review-required states to simplify demo flow
7. Surface 4 — Evidence and Reasoning
7.1 Product Meaning

Evidence and reasoning are what make the FTL credible.

This surface explains why the system produced a proposed interpretation or why a case remains unresolved.

Evidence may include backend-provided signals such as:

amount alignment
date proximity
reference matches
counterparty similarity
missing required evidence
conflicting candidate signals
reasons for blocked finalization

The UI does not generate this evidence.
It reveals it.

7.2 Primary UI Surface

Evidence and reasoning are primarily surfaced in:

Match Detail / Evidence View

They may also be summarized in:

Reconciliation Review Queue
Finalized Truth Record, where lineage references are needed
7.3 Required Backend-Derived Information

The UI may need:

evidence items
reason codes translated or accompanied by user-safe descriptions
candidate comparison blocks
matched field indicators
mismatch indicators
ambiguity indicators
evidence completeness state
lineage reference identifiers
action availability based on current evidence state
7.4 Required UI Communication

The UI should communicate:

why the system proposed the current interpretation
which facts support it
which facts weaken or block it
whether evidence is complete, partial, or missing
whether the case is ready for human decision or still structurally blocked
7.5 Forbidden Frontend Behavior

The UI must not:

fabricate evidence from visual comparison
invent explanation text not grounded in backend output
reinterpret backend reason codes without an explicit product mapping
collapse weak evidence and strong evidence into the same visual meaning
replace evidence with superficial “AI says this is right” messaging
8. Surface 5 — Human Review and Correction
8.1 Product Meaning

Human review and correction represent the governed point where an operator contributes accountable judgment to the FTL lifecycle.

This is not merely “editing a row.”
It is a backend-governed decision point that may influence:

reconciliation status
truth formation
finalization eligibility
export readiness
audit linkage
8.2 Primary UI Surface

Human decision is surfaced in:

Human Correction Screen

It may also be reflected after submission in:

Match Detail / Evidence View
Finalized Truth Record
8.3 Required Backend-Derived Information

Before decision submission:

current review state
permitted action types
current proposal
required fields for the selected action
candidate options where reassignment is allowed
explanation of any blocked action state

After backend response:

accepted or rejected action result
updated review status
whether truth formation progressed
whether finalization or export readiness changed
next available navigation path
8.4 Required UI Communication

The UI should communicate:

what decision the operator is about to submit
that the UI is submitting intent, not directly mutating truth
whether backend accepted or rejected the action
what state now applies after backend confirmation
whether the record has moved closer to finalized truth
8.5 Forbidden Frontend Behavior

The UI must not:

claim a decision succeeded before backend confirmation
locally finalize truth after operator input
store correction outcome as authoritative frontend state
hide backend rejection or conflict response
present correction as casual editing detached from workflow governance
9. Surface 6 — Finalized Truth Record
9.1 Product Meaning

The finalized truth record is the core FTL outcome.

It represents a backend-governed, resolved financial state that has passed through the required processing, review, and finalization conditions defined by the system.

This is where InvoMatch becomes more than a matcher.
It becomes a system that produces authoritative operational truth.

9.2 Primary UI Surface

The finalized truth record is surfaced in:

Finalized Truth Record / Export Readiness

It may be linked from:

Dashboard
Review Queue
Match Detail / Evidence View
9.3 Required Backend-Derived Information

The UI may need:

truth record identifier
finalized status
resolved financial interpretation
source references
linked review decision where applicable
lineage references
audit references
finalization timestamp
tenant context
export readiness state
9.4 Required UI Communication

The UI must communicate:

this is no longer merely a proposal
this record has reached backend-governed resolved state
the truth record is traceable to earlier intake, evidence, and review stages
downstream readiness is a separate explicit status, not assumed
9.5 Forbidden Frontend Behavior

The UI must not:

invent finalization status
merge “approved by human” and “finalized by backend” into the same uncontrolled concept
imply that any review action automatically equals finalized truth unless backend states so
reconstruct truth from earlier screen data
use final UI appearance to compensate for missing backend finalization
10. Surface 7 — Lineage and Audit Linkage
10.1 Product Meaning

Lineage and audit linkage show that the truth record is not isolated or arbitrary.

They allow the product to demonstrate:

what the truth record came from
what system interpretation preceded it
whether human review contributed
what evidence and workflow path support it
how it remains traceable for future operational or audit needs

This is essential for moving InvoMatch toward a credible Financial Truth Layer product.

10.2 Primary UI Surfaces

Lineage and audit linkage should be visible in:

Match Detail / Evidence View
Finalized Truth Record / Export Readiness

The level of detail may differ, but the connection must be explicit.

10.3 Required Backend-Derived Information

Possible backend fields:

source record references
review item references
decision references
finalized truth record references
evidence linkage
audit event identifiers or user-safe references
timestamps tied to relevant state transitions
10.4 Required UI Communication

The UI should communicate:

the truth record has an explainable path
the operator can trace the record backward to intake and review context
decisions are not detached from evidence
audit linkage is backend-governed and not UI-simulated
10.5 Forbidden Frontend Behavior

The UI must not:

construct lineage from locally cached screen history
create fake “timeline” events unsupported by backend references
represent frontend navigation history as audit history
generate audit trail statements independently
obscure broken or missing lineage where backend says linkage is incomplete
11. Surface 8 — Export Readiness
11.1 Product Meaning

Export readiness tells the operator whether a finalized truth record is sufficiently governed and complete for downstream use.

It is not synonymous with:

file generation
public release
external delivery
irreversible operational transfer

Within Mini-EPIC 33.1, export readiness is a displayed backend truth state, not an export implementation effort.

11.2 Primary UI Surface

Export readiness is primarily surfaced in:

Finalized Truth Record / Export Readiness

It may also be summarized in:

Pilot Dashboard
11.3 Required Backend-Derived Information

Possible backend fields:

export readiness status
readiness category
blocking reason if not ready
evidence completeness state
unresolved review dependency if present
finalized truth dependency status
user-safe operational explanation
11.4 Required UI Communication

The UI must communicate:

whether the record is export-ready
why it is ready or blocked
what unresolved condition prevents readiness where applicable
that export readiness is backend-calculated and not UI-inferred
11.5 Forbidden Frontend Behavior

The UI must not:

calculate export readiness locally
convert finalized status into export-ready status by assumption
suggest actual export has occurred
implement export logic under the guise of readiness display
hide blocked readiness because it weakens the demo
12. Surface 9 — Trust Blockers and Non-Happy-Path Truth
12.1 Product Meaning

A trustworthy Financial Truth Layer must make incompleteness and uncertainty visible.

This includes cases where:

evidence is missing
review is unresolved
processing failed
export is blocked
permission prevents an action
backend health is degraded
recovery is in progress

These are not UI embarrassments.
They are part of product credibility.

12.2 Primary UI Surface

Trust blockers are surfaced across:

Error & Trust State Presentation Surface
Dashboard
Review Queue
Match Detail
Finalized Truth Record / Export Readiness
12.3 Required Backend-Derived Information

The UI may need:

trust state category
affected workflow area
whether progress is blocked
whether retry is available
whether operator review is needed
user-safe blocker explanation
recovery state if known
12.4 Required UI Communication

The UI should communicate:

what is not yet trustworthy
what remains unresolved
whether the operator can act
whether the flow is merely incomplete or actively blocked
whether downstream truth or export readiness is affected
12.5 Forbidden Frontend Behavior

The UI must not:

replace blocker specificity with generic “error” copy
smooth over uncertainty for visual simplicity
show green/ready states against backend blockers
continue the story as if finalization is complete when backend truth is unresolved
turn trust warnings into optional decorative UI
13. FTL Surface-to-Screen Responsibility Matrix
FTL SurfacePrimary ScreenSecondary Screen(s)Backend Truth Required
Raw financial inputIntake WorkspaceFinalized Truth Record via lineagesource batches, source metadata
Processing / normalizationIntake WorkspaceMatch Detailnormalized backend state
Proposed system interpretationReview QueueMatch Detailproposal state, review-required status
Evidence and reasoningMatch DetailReview Queue summaryevidence blocks, reason categories
Human decisionHuman Correction ScreenMatch Detail, Finalized Truth Recordpermitted actions, backend decision result
Finalized truthFinalized Truth RecordDashboard summaryfinalized record state
Lineage / audit linkageFinalized Truth RecordMatch Detailreferences, traceability data
Export readinessFinalized Truth RecordDashboard summaryreadiness state, blocker reason
Trust blockersError & Trust SurfaceAll relevant screensbackend-derived trust/error state
14. FTL Narrative Sequence for the Pilot UI

The Pilot UI should make the following product narrative possible without explanation outside the interface:

1. A financial intake exists.
2. The system processes and normalizes that input.
3. A reconciliation interpretation is formed.
4. The system exposes evidence and uncertainty.
5. A human operator reviews or corrects the case.
6. The backend produces a finalized truth record.
7. The truth record carries lineage and audit linkage.
8. Export readiness becomes visible as a governed downstream state.

If a user cannot understand this flow through the Pilot UI, then EPIC 33 has not adequately demonstrated the FTL.

15. FTL Surface Discipline for Base44 Implementation

When building later Base44 pages, every visual block should be classified as belonging to one of the FTL surfaces defined here.

Examples:

source batch card → Raw Financial Input
normalized field panel → Processing / Normalization
proposed match panel → Proposed System Interpretation
evidence comparison table → Evidence and Reasoning
correction form → Human Review and Correction
final truth summary → Finalized Truth Record
audit/lineage panel → Lineage and Audit Linkage
readiness badge + blocker explanation → Export Readiness
warning banner → Trust Blocker Surface

A visual element that cannot be tied to one of these surfaces should be treated skeptically before implementation.

16. Out of Scope

This document does not:

implement UI screens
design Base44 layouts
define exact API endpoint names
define final payload schemas
redesign backend FTL logic
create export functionality
authorize actual export implementation
authorize Scenario 15 execution
authorize regression scenario re-runs
authorize deployment, release, or public artifact publication
17. Closure Standard

This FTL surface definition is complete when:

the visible FTL lifecycle is explicitly defined
raw input, normalized processing, proposed system interpretation, evidence, human review, finalized truth, lineage, audit linkage, export readiness, and trust blockers are all mapped to UI surfaces
each FTL surface has a clear product meaning
each FTL surface identifies the required backend-derived truth
each FTL surface identifies forbidden frontend shortcuts
the Pilot UI can be evaluated against a concrete FTL visibility standard
later Base44 implementation can reveal the FTL without making it a vague marketing phrase
18. Key FTL Surface Statement

The Financial Truth Layer becomes real in the Pilot UI only when users can see the controlled transition from raw financial input to traceable, finalized, export-aware truth.

Any UI that skips that transition and jumps directly from intake to polished output fails the FTL demonstration standard of EPIC 33.1.
