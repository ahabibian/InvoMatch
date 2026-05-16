
INITIAL API TO SCREEN MAPPING FRAMEWORK
Mini-EPIC 33.1 — Initial API-to-Screen Mapping Framework
1. Purpose

This document defines the initial mapping framework between the InvoMatch Pilot UI screens and the backend API contract categories required to support them.

The purpose is to ensure that EPIC 33 does not drift into either of two weak implementation patterns:

a Pilot UI that reconstructs product meaning from raw backend data through frontend logic
a backend API layer that grows reactively and inconsistently screen-by-screen without a coherent contract structure

This document establishes:

what API capability categories each Pilot UI screen requires
the separation between read endpoints and write/action endpoints
the minimum response-state expectations needed for trust-preserving UI behavior
which data meanings must be backend-owned and returned explicitly
what the UI must never derive, infer, mutate, or fabricate
a contract discipline that supports Base44 now while remaining migration-safe for a later custom frontend

This document does not finalize endpoint URLs, request payload schemas, database structures, or implementation sequence.
It defines the screen-facing API contract framework needed before EPIC 33 moves into implementation.

2. Core Contract Principle

The governing principle is:

Pilot UI screens must be served by backend contracts that expose product truth in display-ready structures without transferring business-rule ownership to the frontend.

This means:

the UI may request screen-relevant state
the backend may shape responses for product clarity
the UI must not reconstruct operational truth from low-level fragments
the backend must not become a thin raw-data dump that forces Base44 to simulate product logic

The APIs should be:

screen-aware
business-rule safe
backend-authoritative
migration-safe
explicit about ready, blocked, degraded, failed, and restricted states
3. API Mapping Scope

This framework covers the Pilot UI surfaces defined in Mini-EPIC 33.1:

Pilot Dashboard
Intake Workspace
Reconciliation Review Queue
Match Detail / Evidence View
Human Correction Screen
Finalized Truth Record / Export Readiness
Tenant / User Context Surface
Error & Trust State Presentation Surface

For each screen, this document identifies:

primary read API categories
optional secondary read API categories
write/action API categories, if any
expected backend-owned semantic fields
UI-forbidden derivations
expected response-state support
4. API Category Taxonomy

To avoid prematurely locking exact routes while still defining architecture, this framework uses API capability categories.

4.1 Read API Categories

Read APIs may include:

dashboard summary read
intake collection read
intake detail read
review queue read
review item detail read
evidence detail read
correction context read
finalized truth record read
export readiness read
tenant/user context read
health/trust state read
permission-aware action availability read
4.2 Write / Action API Categories

Write/action APIs may include:

approve match intent submission
reject match intent submission
correction intent submission
reassignment intent submission
controlled review decision submission
later, only if separately authorized, export-trigger or retry-trigger actions
4.3 Shared Response-State Categories

Every relevant API family should support explicit screen states such as:

success / ready
empty
loading handled by UI while awaiting response
blocked
permission denied
validation rejected
conflict / stale state
not found
degraded but partially usable
failed / retryable
failed / not retryable

The exact transport-level representation can be designed later.
The important requirement here is that the backend communicates operational meaning explicitly enough for the UI to preserve trust.

5. Cross-Cutting API Design Rules
5.1 Backend Must Return Product Meaning, Not Just Raw Fields

Bad contract pattern:

Return raw invoices, raw payments, raw flags,
and make the UI determine:
- which items need review
- which are blocked
- which are export-ready

Required contract pattern:

Return explicit product-state fields such as:
- review_status
- readiness_status
- blocker_reason
- permitted_actions
- trust_state
5.2 UI Must Not Derive Core Workflow Truth

The UI must not derive:

whether a case requires review
whether a proposed match is acceptable
whether a record is finalized
whether export readiness has been achieved
whether evidence is sufficient
whether an action is permitted
whether a tenant has access to a record

These must be backend-owned meanings.

5.3 APIs Should Prefer Stable Semantic Objects Over Screen-Specific Hacks

The backend may return screen-friendly projections, but these projections must remain semantically coherent.

Example:

Good:

review_item_summary
- id
- review_status
- reason_for_review
- proposed_interpretation_summary
- evidence_state
- permitted_actions

Weak:

queue_card_color
button_should_be_red
show_warning_icon

The backend should return meaning, not visual styling instructions.

5.4 Read APIs and Action APIs Must Remain Distinct

Reads answer:

What is the current backend-owned truth?

Actions express:

What operator intent should the backend evaluate?

Do not blend them into opaque “do-and-return-magic” endpoints unless a later implementation design explicitly justifies that pattern.

5.5 Action APIs Must Return Authoritative Result State

After any accepted or rejected operator action, the backend response should make it possible for the UI to refresh and display authoritative outcome.

At minimum, the result should communicate:

action accepted or rejected
relevant updated status
whether the review item remains open
whether finalized truth is now available
whether export readiness changed
what next navigation target is valid, where appropriate
6. Screen 1 — Pilot Dashboard API Mapping
6.1 Primary Read API Categories

The Pilot Dashboard requires a dashboard summary read capability.

This capability should return a tenant-scoped operational summary, potentially including:

open review item count
finalized truth record count
export-ready truth record count
blocked or unresolved item count
latest relevant intake or processing status
latest known trust/degraded condition where appropriate
summary navigation references where the UI needs to drill down
6.2 Optional Secondary Read API Categories

May include:

health/trust state read
recent activity summary read
tenant/user context read

These may be combined or separate later depending on implementation decisions.

6.3 Write / Action API Categories

The Dashboard should initially require no direct mutation endpoint.

It may navigate to other workflow areas, but it should not be a primary place for financial decision actions.

6.4 Backend-Owned Semantic Fields

Expected semantic outputs may include:

review_queue_status_summary
finalized_truth_summary
export_readiness_summary
processing_health_summary
blocking_conditions_summary
tenant_scope_label

Names are illustrative, not final.

6.5 UI Must Not Derive

The Dashboard UI must not derive:

review counts from raw record pages
export readiness totals from finalized record lists
operational blocker severity from miscellaneous raw flags
system health state from failed individual requests
6.6 Required Response-State Support

The dashboard contract must support display of:

ready summary
empty but valid tenant state
degraded backend summary
partial summary unavailable
permission-restricted visibility where relevant
failed summary load with safe retry path
7. Screen 2 — Intake Workspace API Mapping
7.1 Primary Read API Categories

The Intake Workspace requires:

intake collection read
intake detail read

These support:

intake batch listing
batch-level status
detail inspection for a selected batch or input context
7.2 Optional Secondary Read API Categories

May include:

processing run detail read
normalized record summary read
related review item references read
7.3 Write / Action API Categories

For the architecture defined in Mini-EPIC 33.1, the Intake Workspace does not require direct mutation APIs as a baseline.

A later Mini-EPIC may authorize:

retry processing
resubmit intake
acknowledge failure

Those are not authorized by this mapping framework.

7.4 Backend-Owned Semantic Fields

Expected response meanings may include:

intake batch identifier
intake source type
intake created timestamp
processing state
processing completion state
normalization availability
unresolved parsing/processing marker
downstream review linkage
user-safe processing issue summary
7.5 UI Must Not Derive

The UI must not derive:

processing success
normalization completeness
whether an intake generated review obligations
record validity
whether a source is safe for downstream use
7.6 Required Response-State Support

The intake contracts must support:

intake available
no intake available
processing pending
processing complete
processing failed
processing partially complete
intake detail inaccessible
malformed or blocked read outcome expressed safely
8. Screen 3 — Reconciliation Review Queue API Mapping
8.1 Primary Read API Categories

The Review Queue requires:

review queue read

This API category should return a list of backend-owned review work items already shaped for queue presentation.

8.2 Optional Secondary Read API Categories

May include:

queue filter options read
aggregated queue summary read
export-impact filter availability read
8.3 Write / Action API Categories

The queue itself should generally avoid direct mutation.

It may expose transitions to downstream action screens.
If quick actions are later considered, they must still route through dedicated backend-owned action contracts and be separately justified.

8.4 Backend-Owned Semantic Fields

A review queue item summary may include:

review item identifier
current review status
reason review is required
proposed system interpretation summary
evidence state summary
priority or urgency classification if backend supports it
export impact or finalization blocker marker
permitted next actions
created or last-updated timestamp
8.5 UI Must Not Derive

The queue UI must not derive:

whether an item belongs in the queue
whether an item is urgent
whether evidence is adequate
whether export is blocked
whether approve/reject/correct should be allowed
8.6 Required Response-State Support

The queue contract must support:

populated queue
empty queue
filtered no-result state
queue partially unavailable
queue load failed
permission denied for queue access
stale/refresh-needed state where relevant
9. Screen 4 — Match Detail / Evidence View API Mapping
9.1 Primary Read API Categories

The Match Detail / Evidence View requires:

review item detail read
evidence detail read

These may later be combined into one composite screen-projection contract if that remains semantically clean.

9.2 Optional Secondary Read API Categories

May include:

linked source reference read
linked finalized truth reference read where already available
audit linkage summary read
related candidate set read
9.3 Write / Action API Categories

The screen may provide transition points toward:

approve match action
reject match action
correction action
reassignment action

However, the main detail contract remains read-only.
The actual writes should belong to explicitly governed action APIs.

9.4 Backend-Owned Semantic Fields

Expected meanings include:

review item identity
source record summary
candidate record summary
normalized financial values
proposed interpretation
evidence collection
mismatch/ambiguity markers
reason categories
evidence completeness state
permitted actions
current review workflow state
lineage or audit references where appropriate
9.5 UI Must Not Derive

The UI must not derive:

candidate ranking
strength of evidence
whether the proposal is trustworthy enough
whether review can be skipped
what final state should be reached
reason text unsupported by backend-provided semantics
9.6 Required Response-State Support

The detail/evidence contract must support:

complete detail available
detail available with partial evidence
missing evidence
blocked action state
stale review item
item not found
permission denied
failed data load
recovery/retry guidance where relevant
10. Screen 5 — Human Correction Screen API Mapping
10.1 Primary Read API Categories

The Human Correction Screen requires:

correction context read

This read capability should return the backend-owned state necessary to render a valid decision form, including:

current workflow state
permitted action types
current system proposal
whether manual correction is allowed
required fields per action path
candidate options where reassignment is supported
10.2 Write / Action API Categories

This screen requires explicit backend-owned action contracts for:

approve match intent submission
reject match intent submission
correction intent submission
reassignment intent submission

The UI must submit operator intent, not direct truth-state mutation.

10.3 Backend-Owned Semantic Fields

The correction context and action responses may need:

review item identifier
permitted actions
required form schema or action constraints
current proposal summary
alternate candidate options
action precondition state
user-safe blocked reason if action unavailable
result acceptance/rejection status
updated review status
updated finalized truth availability
updated export readiness where affected
10.4 UI Must Not Derive

The Human Correction Screen must not derive:

whether an action is legally or operationally allowed
whether a correction creates final truth
whether finalization has occurred
whether export readiness changed
whether audit recording succeeded
10.5 Required Response-State Support

Correction read/action contracts must support:

correction context ready
action unavailable
missing prerequisite state
validation rejected
permission denied
state conflict / stale item
action accepted
action rejected
action accepted but downstream truth still not finalized
action accepted and updated backend state available for refresh
11. Screen 6 — Finalized Truth Record / Export Readiness API Mapping
11.1 Primary Read API Categories

This screen requires:

finalized truth record read
export readiness read

These may later be returned through a unified truth-record projection where appropriate, provided the distinction between truth finalization and export readiness remains explicit.

11.2 Optional Secondary Read API Categories

May include:

lineage detail read
linked review decision read
audit reference summary read
linked source intake read
11.3 Write / Action API Categories

Within Mini-EPIC 33.1, this screen requires no export execution endpoint.

It may display readiness.
It must not authorize or trigger export implementation.

A later mini-epic must separately define and authorize any actual export action surface.

11.4 Backend-Owned Semantic Fields

Expected response meanings include:

truth record identifier
finalized state
resolved financial fields
source lineage summary
linked human decision reference
evidence completeness state
audit linkage summary
export readiness status
export blocker reason
downstream-operational note if provided
11.5 UI Must Not Derive

The UI must not derive:

finalized truth from earlier screens
export readiness from finalized status
audit linkage from local timeline
blocker absence from silence
downstream usability from UI presentation
11.6 Required Response-State Support

The truth/readiness contracts must support:

finalized and export-ready
finalized but not export-ready
finalized but lineage incomplete
no finalized truth available
truth record inaccessible
export status unavailable
permission denied
failed truth/readiness load
12. Screen 7 — Tenant / User Context Surface API Mapping
12.1 Primary Read API Categories

This surface requires:

tenant/user context read

This API should return only backend-authoritative context required to anchor the UI experience.

12.2 Optional Secondary Read API Categories

May include:

permission profile summary read
environment/pilot mode context read
12.3 Write / Action API Categories

No write API is required for this surface within Mini-EPIC 33.1.

It is a context display layer, not a tenant management interface.

12.4 Backend-Owned Semantic Fields

Expected response meanings may include:

tenant identifier
tenant display name
current user display name
role label
permission profile summary
environment marker if supported
12.5 UI Must Not Derive

The UI must not derive:

current tenant scope
current role permissions
access boundaries
alternate tenant visibility
security assumptions based on route or page state
12.6 Required Response-State Support

The context contract should support:

context available
context partially unavailable
permission-limited context
not authenticated / not authorized state where relevant
context read failed safely
13. Screen 8 — Error & Trust State Presentation Surface API Mapping
13.1 Primary Read API Categories

This surface is not necessarily powered by a single endpoint.
It may consume structured trust/error states returned by multiple screen APIs.

In addition, a dedicated:

health/trust state read

may be justified for global UI surfaces such as Dashboard or header-level trust banners.

13.2 Write / Action API Categories

This surface should not directly mutate core product truth.

It may later invoke controlled retries or recovery navigation where explicitly authorized, but those are out of scope here.

13.3 Backend-Owned Semantic Fields

Structured trust/error response meaning may include:

trust state category
error category
affected screen/domain
user-safe message
blocker reason
retry availability
permission restriction reason where disclosure is safe
whether the current workflow may continue
whether state is degraded, blocked, or failed
13.4 UI Must Not Derive

The UI must not derive:

true system health from isolated local conditions
whether a blocked record is safe to proceed with
whether a failure is recoverable
whether a permission denial is temporary or permanent
whether evidence absence is operationally acceptable
13.5 Required Response-State Support

Trust/error presentation must support:

informational state
warning state
blocked state
restricted state
failed state
recovery-in-progress state
retryable state
not-retryable state
14. API-to-Screen Mapping Matrix
Pilot UI ScreenPrimary Read API CategoryPrimary Action API CategoryMust Be Backend-Owned
Pilot Dashboarddashboard summary readnone initiallycounts, blockers, readiness summary
Intake Workspaceintake collection/detail readnone initiallyprocessing state, normalization state
Review Queuereview queue readnone initiallyreview membership, reason, action availability
Match Detail / Evidence Viewreview detail + evidence detail readtransition onlyproposal, evidence, ambiguity, permitted actions
Human Correction Screencorrection context readapprove/reject/correct/reassign intent APIsdecision constraints, acceptance, updated state
Finalized Truth / Export Readinessfinalized truth + export readiness readnone in 33.1finalization, readiness, lineage, blocker reason
Tenant / User Contexttenant/user context readnonetenant, user, role, permission context
Error & Trust Surfacestructured screen error states + optional trust readnone initiallytrust category, blocker meaning, retry semantics
15. API Response Meaning Framework

Later endpoint-level implementation should aim to support responses that make UI rendering reliable without pulling business logic into Base44.

Each relevant response projection should strive to communicate:

15.1 Identity
stable entity identifier
related entity references
tenant scope where useful and safe
15.2 Operational State
current state
readiness state
review state
blocked/unblocked state
15.3 Explanation
user-safe summary
reason categories
blocker reasons
evidence state summary
15.4 Actionability
permitted actions
unavailable actions with reason where appropriate
retry availability where relevant
15.5 Traceability
source linkage
review linkage
final truth linkage
audit or lineage references where relevant
16. Frontend Derivation Prohibition Map

The Pilot UI must never derive or fabricate the following:

Forbidden Frontend DerivationBackend Must Provide
Review-required statusexplicit review state
Export readinessexplicit readiness state
Finalized truth availabilityexplicit finalized truth state
Evidence sufficiencyexplicit evidence/trust state
Permitted actionsexplicit permitted_actions
Tenant visibilitybackend-scoped returned dataset
Blocker severityexplicit blocker/trust category
Audit linkageexplicit audit/lineage references
Correction result truthbackend action response + refreshed state

This prohibition map should be treated as a hard guardrail during Base44 implementation.

17. Design Tension: Screen-Aware vs. UI-Coupled APIs

A weak API design can fail in two opposite ways:

17.1 Too Raw

If APIs return only primitive records and force Base44 to assemble product meaning, frontend logic contamination occurs.

17.2 Too Visual

If APIs dictate UI layout, colors, icon choices, or component placement, backend contracts become presentation-coupled and fragile.

17.3 Required Balance

The correct balance is:

The backend returns product semantics; the UI determines presentation.

Examples:

Backend may return:

review_status = "requires_human_decision"
export_readiness = "blocked"
blocker_reason = "missing_required_evidence"

The UI may decide:

where to display it
which layout block contains it
how to visually emphasize it

But the UI may not redefine the meaning.

18. Out of Scope

This document does not:

define exact REST route names
define GraphQL, REST, RPC, or transport decisions
finalize JSON payload schemas
implement endpoints
refactor backend repositories or services
authorize new export behavior
authorize Base44 direct API wiring
authorize Scenario 15 execution
authorize regression reruns
authorize deployment, release, or public artifact publication
19. Closure Standard

This initial API-to-screen mapping framework is complete when:

each Pilot UI surface has been mapped to required API capability categories
read and action contracts are clearly separated
backend-owned semantic outputs are identified
frontend derivation prohibitions are explicit
shared response-state needs are documented
correction and decision flows are tied to intent-based action APIs
finalized truth and export readiness remain explicitly backend-owned states
later EPIC 33 implementation can define precise endpoints without rethinking the contract architecture
20. Key API Mapping Statement

The Pilot UI may be screen-aware, but backend contracts must remain truth-authoritative rather than presentation-driven.

Any EPIC 33 API decision that forces Base44 to reconstruct financial truth, infer readiness, or simulate permissions violates this framework.
