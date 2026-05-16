
TRUST ERROR AND PERMISSION PRESENTATION RULES
Mini-EPIC 33.1 — Trust, Error, and Permission Presentation Rules
1. Purpose

This document defines the presentation rules for trust states, operational errors, workflow blockers, degraded conditions, and permission restrictions in the InvoMatch Pilot UI.

The purpose is to ensure that EPIC 33 does not present a misleading “happy-path only” interface that hides uncertainty, suppresses blockers, or weakens the credibility of the Financial Truth Layer.

A financial workflow product must be able to show:

what is ready
what is incomplete
what is blocked
what is restricted
what failed
what can be retried
what remains unresolved
what cannot safely continue

This document establishes:

trust-preserving UI principles
error presentation requirements
permission presentation requirements
blocker-state handling expectations
screen-level and global trust state categories
guidance for operator-safe messaging
explicit frontend prohibitions against hiding, softening, or fabricating backend truth

This document does not implement UI components, define final visual styling, or redesign backend error contracts.
It defines the presentation discipline that later EPIC 33 implementation must follow.

2. Core Trust Presentation Principle

The governing principle is:

The Pilot UI must preserve operator trust by making backend-defined uncertainty, restriction, and failure visible in a controlled, useful, and non-deceptive way.

This means:

do not expose raw backend internals
do not hide meaningful operational truth
do not replace specific blockers with vague generic errors
do not imply readiness where backend state is blocked
do not imply success where backend state is unresolved
do not make missing permission appear like a technical malfunction
do not make backend degradation disappear behind cosmetic UI polish

The UI exists to communicate governed state honestly.

3. Trust-State Categories

The Pilot UI must be able to present the following trust-state categories.

Trust StateProduct MeaningUI Responsibility
ReadyThe current state is valid and operationally usableshow clear positive state without exaggeration
In ProgressBackend processing or transition is underwayshow active progress without claiming completion
Review RequiredHuman judgment is needed before trust can advanceshow review obligation clearly
Evidence IncompleteThe system lacks required support for a stronger stateshow missing support and impact
BlockedWorkflow cannot safely continueshow blocker and affected action
Export Not ReadyFinalized or near-final state is not downstream-readyshow readiness failure and reason
Permission RestrictedUser is not allowed to view or actshow restriction as authorization state
DegradedSystem is partially available but reliability is reducedshow caution and affected areas
FailedAn operation or read path could not completeshow failure safely and provide valid next step where available
Recovery in ProgressBackend recovery or repair state is activeshow recovery state without promising completion
Stale / ConflictUI action was based on outdated stateshow refresh requirement and reject false continuation
Not Found / GoneRequested resource is unavailable or no longer existsshow absence honestly and redirect appropriately
4. Message Construction Standard

Every trust, error, or permission message should answer as many of these five questions as are relevant:

What happened?
What is affected?
Can the operator continue?
What backend-owned condition caused this state?
What valid next step exists, if any?

A message that says only:

Something went wrong.

is inadequate for a financial operational product.

5. User-Safe Error Messaging Rule

The UI must not expose:

stack traces
raw exception payloads
database errors
framework-level error text
internal service naming where inappropriate
raw validation objects unless explicitly shaped for user display
unreviewed backend debug messages

The UI should instead display backend-provided or frontend-mapped user-safe operational messages.

Example:

Weak
500 Internal Server Error
Stronger
The review queue could not be loaded.
No review decisions were changed.
Refresh the queue or return to the dashboard.

The stronger message preserves trust because it explains:

what failed
what remained safe
what can be done next
6. State Severity Discipline

The UI must distinguish between:

6.1 Informational State

Used when:

there is no blocker
the user only needs context
state is passive

Example:

This record is currently under review.
6.2 Warning State

Used when:

workflow may continue
trust is reduced
an important condition requires attention

Example:

Evidence is partial. Human review remains required before finalization can proceed.
6.3 Blocking State

Used when:

the workflow cannot safely continue
a requested action is unavailable
a required backend condition is not satisfied

Example:

Finalization cannot proceed because required evidence is missing.
6.4 Failure State

Used when:

an operation could not complete
a data read failed
a submission failed due to system or validation outcome

Example:

The correction could not be submitted because the review item changed before your action was processed.
Refresh the record and review the latest state.

The UI must not collapse warning, blocker, and failure into one generic visual treatment.

7. Validation Error Presentation
7.1 Product Meaning

Validation errors occur when operator-provided input does not satisfy backend requirements for a requested action.

Examples:

required reason missing
invalid correction input
unsupported reassignment choice
missing required form field
malformed action payload
7.2 Required UI Behavior

The UI should:

identify the invalid field or action context where safe
explain what is required
preserve the user’s local form state where appropriate
avoid implying that backend state changed
allow correction and resubmission when valid
7.3 Required Message Shape

A good validation message should communicate:

The correction was not submitted.
A review reason is required for this action.
Add the required reason and submit again.
7.4 Forbidden UI Behavior

The UI must not:

silently discard backend validation errors
claim the action was applied
replace a validation failure with a generic system error
fix or alter backend-required data silently
reinterpret backend validation semantics on its own
8. Permission Denied Presentation
8.1 Product Meaning

Permission denied indicates that the current user does not have the backend-authorized right to:

view a record
access a queue
perform a review action
inspect a truth record
access tenant-scoped data outside their permission boundary
8.2 Required UI Behavior

The UI should:

present the condition as an authorization restriction, not a system crash
avoid exposing sensitive data
explain that the requested view or action is not available in the current permission context
avoid presenting hidden functionality as if it simply “did not exist” when explanatory context is useful
preserve route or workflow safety
8.3 Required Message Shape

Examples:

You do not have permission to view this finalized truth record in the current workspace.
This review action is not available for your current role.
No financial state was changed.
8.4 Forbidden UI Behavior

The UI must not:

attempt to reproduce permission logic locally
hide backend permission denial behind generic missing-data language
leak the existence of restricted data where that would be unsafe
show disabled controls without explanation where the restriction matters to workflow understanding
allow visual continuation after backend rejection
9. Export Not Ready Presentation
9.1 Product Meaning

Export not ready means that a record does not satisfy backend-defined downstream readiness conditions.

This may occur because:

truth is not finalized
evidence is incomplete
review remains unresolved
required lineage is unavailable
some other readiness dependency remains blocked
9.2 Required UI Behavior

The UI should:

make the readiness failure explicit
display backend-provided blocker reason
distinguish “not export-ready” from “export failed”
avoid suggesting that export took place
show the link back to the unresolved source of the blocker where appropriate
9.3 Required Message Shape

Example:

Export readiness is blocked.
This truth record cannot be treated as downstream-ready because the review dependency remains unresolved.
Return to the linked review case to inspect the blocker.
9.4 Forbidden UI Behavior

The UI must not:

calculate readiness locally
mark a record ready because it looks complete visually
conflate finalized state with readiness state
hide readiness blockers to keep the demo smooth
authorize or simulate export execution
10. Failed Run Presentation
10.1 Product Meaning

A failed run occurs when a backend processing step, intake operation, or governed workflow operation does not complete successfully.

Examples:

intake processing failed
normalization failed
backend read failed
action submission could not complete
truth projection cannot be loaded
10.2 Required UI Behavior

The UI should identify:

what operation failed
what was not changed
whether the operator can retry
whether downstream workflow is affected
whether the system is partially usable
10.3 Required Message Shape

Example:

Processing failed for this intake batch.
No finalized truth record was produced from this run.
Review the processing status or return to the dashboard.
10.4 Forbidden UI Behavior

The UI must not:

imply partial success without backend confirmation
continue downstream flow as if failed processing completed
display raw backend exception output
suppress failure in favor of a neutral loading state
treat failed run and in-progress state as interchangeable
11. Degraded System Health Presentation
11.1 Product Meaning

Degraded health means the backend is still partially available, but trust or completeness of one or more UI surfaces is reduced.

Examples:

dashboard summary partially unavailable
health/trust monitor unavailable
delayed data refresh
non-critical read projection missing
secondary context unavailable while core workflow remains accessible
11.2 Required UI Behavior

The UI should:

state that the system is degraded
identify affected areas if backend provides that information
explain whether the operator may safely continue
avoid overstating precision when summary state is incomplete
preserve trust by refusing to fake completeness
11.3 Required Message Shape

Example:

System status is partially degraded.
Review actions remain available, but dashboard summary counts may be incomplete.
Use the review queue for the current authoritative workload view.
11.4 Forbidden UI Behavior

The UI must not:

silently suppress degraded state
show derived summary precision that backend did not provide
imply everything is healthy when backend says otherwise
block unrelated workflow areas unless backend state requires it
12. Recovery in Progress Presentation
12.1 Product Meaning

Recovery in progress means the backend is actively restoring or re-evaluating a previously failed or incomplete state.

This may apply to:

reprocessing a failed item
rehydrating a view projection
restoring trust/health status
other future backend-managed recovery paths
12.2 Required UI Behavior

The UI should:

show recovery as active but not yet complete
avoid promising a completion time
explain affected workflow where appropriate
prevent premature downstream truth claims
12.3 Required Message Shape

Example:

Recovery is in progress for this processing context.
Final truth and export readiness may remain unavailable until recovery completes.
12.4 Forbidden UI Behavior

The UI must not:

claim recovery completed early
hide lingering blockers
turn recovery status into a silent spinner with no explanation
present downstream records as final while recovery is unresolved
13. Missing Evidence Presentation
13.1 Product Meaning

Missing evidence means the backend lacks the necessary support to justify a stronger state, action, or readiness claim.

This may affect:

review decision confidence
finalization eligibility
export readiness
audit traceability
13.2 Required UI Behavior

The UI should:

clearly state that evidence is missing or incomplete
identify whether review, finalization, or export is affected
avoid implying that absence of evidence is harmless
route the user back to relevant evidence context where appropriate
13.3 Required Message Shape

Example:

Evidence is incomplete for this reconciliation case.
The record cannot be shown as finalized export-ready truth until the missing support is resolved.
13.4 Forbidden UI Behavior

The UI must not:

hide evidence absence
replace evidence with generic AI confidence language
permit unsupported finalization flow visually
imply that a human click alone resolves evidentiary gaps unless backend confirms it
14. Unresolved Review State Presentation
14.1 Product Meaning

Unresolved review state means a financial case has not yet reached a governed outcome accepted by the backend.

This may include:

waiting for operator decision
rejected proposal awaiting further handling
correction flow not yet accepted
review case returned to queue after conflict
14.2 Required UI Behavior

The UI should:

clearly show unresolved status
avoid presenting finalized truth
make valid next review action visible where backend permits it
distinguish unresolved state from failure state
14.3 Required Message Shape

Example:

This case remains unresolved.
A human review decision is still required before final truth can be produced.
14.4 Forbidden UI Behavior

The UI must not:

treat unresolved state as success
remove unresolved case from view without backend instruction
collapse review-required and blocked states into the same vague label
imply downstream readiness where none exists
15. Stale or Conflict State Presentation
15.1 Product Meaning

A stale/conflict condition occurs when the user attempts to act on state that has changed since the screen was loaded.

Examples:

another operator or process changed the review item
permitted actions changed
underlying evidence changed
review item moved to a new backend-owned state
15.2 Required UI Behavior

The UI should:

reject optimistic continuation
explain that state changed
instruct the operator to refresh or reload the current record
avoid claiming the attempted action succeeded
15.3 Required Message Shape

Example:

This review item changed before your decision was applied.
No action was completed.
Refresh the record and review the latest backend state.
15.4 Forbidden UI Behavior

The UI must not:

auto-merge conflicting operator action semantics
silently overwrite newer backend state
keep showing old action controls as if still valid
hide conflict behind generic submission failure
16. Not Found or No Longer Available Presentation
16.1 Product Meaning

A not found / gone state means the requested record or context is not available under the current backend state.

This may occur because:

the item no longer exists
the item moved out of a queue
the current user no longer has access
a route references stale or invalid data
16.2 Required UI Behavior

The UI should:

avoid pretending the record exists
avoid exposing unauthorized existence where unsafe
direct the operator back to a valid parent context where appropriate
distinguish absence from generic failure where backend contract allows it
16.3 Required Message Shape

Example:

This review item is no longer available in its previous state.
Return to the review queue to load the current authoritative workload.
17. Global vs. Local Trust Presentation
17.1 Global Trust Surfaces

Global trust surfaces may include:

dashboard-level health banner
top-level degraded system notice
tenant/workspace context restrictions
application-wide permission/authentication notice

These describe broader platform or session context.

17.2 Local Trust Surfaces

Local trust surfaces may include:

item-level evidence gap
record-level export blocker
action-level permission denial
field-level validation message
queue item unresolved state

These describe a specific workflow or record.

17.3 Required Distinction

The UI must not display local item problems as if the whole system is degraded.
The UI must not hide system-wide degradation inside a single local component.

Trust scope must match the actual backend-defined scope.

18. Screen-Level Presentation Requirements
18.1 Pilot Dashboard

Must be able to show:

degraded health
summary unavailable
export-not-ready count where backend provides it
blocker summaries
empty but valid tenant state
18.2 Intake Workspace

Must be able to show:

processing pending
processing failed
partial normalization
intake unavailable
permission restriction
18.3 Review Queue

Must be able to show:

queue empty
queue load failure
permission denied
review-required states
export-impact blockers where backend provides them
18.4 Match Detail / Evidence View

Must be able to show:

missing evidence
stale item
ambiguous proposal
blocked action state
permission restriction
incomplete lineage where relevant
18.5 Human Correction Screen

Must be able to show:

validation error
action unavailable
permission denied
stale/conflict state
accepted action
rejected action
accepted action with no finalized truth yet
18.6 Finalized Truth Record / Export Readiness

Must be able to show:

no finalized truth available
finalized but not export-ready
export blocker reason
lineage incomplete
permission denied
failed readiness read
18.7 Tenant / User Context Surface

Must be able to show:

current tenant/user context
unavailable context safely
permission or authentication problem where relevant
19. Trust-Preserving Copy Rules

The following copy principles should guide later UI implementation:

19.1 State Before Emotion

Describe the operational state first.
Do not write emotional or marketing-heavy copy around blockers.

19.2 Avoid False Reassurance

Do not say:

Everything looks good.

when backend state is partial, unresolved, or degraded.

19.3 Avoid Empty Alarm

Do not exaggerate technical severity where the state is a valid business workflow condition.

For example:

Review required is not necessarily an “error.”
Export not ready may be a governed normal condition.
Permission restricted is not a system failure.
19.4 Preserve Non-Action

Where no financial state changed, say so if it helps operator trust.

Example:

No financial state was changed.
19.5 Prefer Operational Clarity

Good copy says:

what state applies
what remains unresolved
what next step exists

Not:

abstract optimism
technical noise
empty apology
20. Forbidden Trust Presentation Patterns

The following are prohibited in EPIC 33 Pilot UI implementation:

Showing raw backend error payloads to users
Replacing specific backend blockers with “Something went wrong”
Presenting green/ready states against blocked backend truth
Hiding permission restrictions by silently removing meaningful actions
Treating unresolved review as completed work
Displaying export-ready when backend export readiness is false or absent
Displaying final truth where backend finalization is absent
Using frontend navigation history as audit or lineage truth
Optimistically claiming action success before backend confirmation
Treating evidence absence as visually minor when it blocks truth formation
21. Relationship to FTL Demonstration

Trust, error, and permission presentation are not secondary polish.
They are part of the Financial Truth Layer demonstration itself.

A product that claims to build financial truth but cannot show:

why truth is blocked
why evidence is insufficient
why an action is restricted
why export readiness is unavailable

has not actually demonstrated a governable truth system.

It has only demonstrated a polished interface.

22. Out of Scope

This document does not:

define final UI components or styling
choose icons, color palettes, or animation patterns
finalize backend error object schemas
implement trust state APIs
implement retry or recovery APIs
authorize export implementation
authorize export execution
authorize Scenario 15 execution
authorize regression reruns
authorize deployment, release, or public artifact publication
23. Closure Standard

This trust, error, and permission presentation rules document is complete when:

the Pilot UI trust-state categories are explicitly defined
validation, permission, export readiness, failed run, degraded health, recovery, missing evidence, unresolved review, stale/conflict, and missing-resource states are each defined
required user-safe presentation behavior is documented for each state
forbidden frontend behavior is explicit
global and local trust presentation are separated
screen-level trust/error expectations are mapped
copy rules preserve operational clarity without exposing raw backend internals
the Pilot UI can later represent non-happy-path financial truth honestly and consistently
24. Key Trust Presentation Statement

A Pilot UI that hides backend-defined uncertainty is not trustworthy; it is merely polished.

EPIC 33 must prefer operational honesty over demo smoothness wherever the two come into tension.
