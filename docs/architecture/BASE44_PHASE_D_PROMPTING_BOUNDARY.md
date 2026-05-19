
Base44 Phase D Prompting Boundary
Purpose

This document defines the mandatory prompting discipline for actual Base44 construction during:

Phase D — Intake & Shared Trust-State Completion

within Mini-EPIC 33.6.

Phase D is especially sensitive because an uncontrolled Base44 prompt can easily fabricate operational behavior that is not authorized, including:

Fake upload outcomes
Fake ingestion state
Fake parsing / OCR state
Fake trust verdicts
Fake permission enforcement
Fake backend-confirmed behavior

The purpose of this prompting boundary is to ensure that Base44 constructs only the authorized Phase D presentation surfaces and does not reinterpret the pilot UI as an operational intake or authorization system.

Governing Prompting Rule

Every Phase D Base44 prompt must construct presentation surfaces, not operational outcomes.

A Phase D prompt may ask Base44 to create:

Intake framing
Source-material workspace layout
Reserved non-operational intake regions
Honest backend-dependency copy
Shared trust-state presentation components
Shared error-state presentation components
Shared permission-state presentation components

A Phase D prompt may not ask Base44 to create:

A working upload flow
A fake successful upload state
A fake file queue
Fake parsed documents
Fake OCR results
Fake ingestion progress
Fake run creation
Fake permission denial or approval
Fake trust confirmation
Any Phase E backend binding or simulation
Prompting Boundary for Intake Workspace
Base44 May Be Asked To

Base44 may be prompted to create an Intake Workspace that:

Appears as the upstream pilot entry surface
Explains that raw financial source material will later enter the product pipeline here
Contains reserved visual regions for future intake interaction
Uses placeholder cards or panels only when clearly marked as future backend-dependent
States that current Phase D intake is non-operational
Connects narratively to downstream review surfaces
Reinforces that review queue records are not being created from this surface in the current pilot
Base44 Must Not Be Asked To

Base44 must not be prompted to create:

Upload invoice button with implied current success
Upload bank statement button with implied current success
Drag-and-drop uploader that looks operational
“File uploaded successfully”
“3 files queued”
“OCR completed”
“Records parsed”
“Matching started”
“Run created”
“Continue to review generated records”
Any fake operational transition from intake to review
Required Intake Prompt Language

Any Base44 prompt for Intake Workspace construction must explicitly include language equivalent to:

This surface is a non-operational Phase D pilot intake framing screen.
Do not create a real or simulated upload workflow.
Do not show uploaded files, file queues, ingestion results, OCR output, parsing output, or processing progress.
Do not imply that review records originate from this screen in the current pilot.
Use honest copy that explains future backend intake dependency.
Prompting Boundary for Shared Trust-State Presentation
Base44 May Be Asked To

Base44 may be prompted to create reusable presentation patterns for states such as:

Not yet backend-confirmed
Future backend-dependent
Unavailable in current pilot
Non-operational in current pilot
Restricted or permission-dependent in future product state

These patterns may appear as:

Information banners
Explanatory cards
Consistent microcopy blocks
Shared status-language components
Cross-surface note structures
Base44 Must Not Be Asked To

Base44 must not be prompted to create:

“Verified”
“Trusted”
“Confirmed”
“Audit-safe”
“Permission granted”
“Permission denied”
“Access blocked”
“Backend failure detected”
“Trust validated”
“Securely approved”

unless those terms are clearly presented as future backend-dependent explanatory language and not as live product outcomes.

Required Trust-State Prompt Language

Any Phase D trust-state prompt must explicitly include language equivalent to:

Do not create a trust verdict.
Do not create operational verification badges.
Do not imply backend confirmation where backend binding does not yet exist.
Use honest presentation language to distinguish structural UI from backend-confirmed truth.
Prompting Boundary for Shared Error-State Presentation
Base44 May Be Asked To

Base44 may be prompted to create shared error-state presentation components that:

Explain unavailable or non-operational pilot states
Show how future backend-connected failures may later be communicated
Establish a consistent visual grammar for error posture
Remain explicitly presentational and non-simulated
Base44 Must Not Be Asked To

Base44 must not be prompted to create:

Fake API error responses
Fake failed uploads
Fake ingestion failures
Fake OCR/parser failures
Fake permission errors
Fake empty-state messages that imply a real backend lookup failed
Fake red alert banners tied to nonexistent runtime failures
Required Error-State Prompt Language

Any Phase D error-state prompt must explicitly include language equivalent to:

This is a presentational error/unavailable-state pattern, not a live backend failure.
Do not simulate failed operations.
Do not imply that an API request, upload, parsing, or ingestion operation has actually failed.
Use bounded copy that preserves the distinction between current pilot limitation and real product runtime error.
Prompting Boundary for Shared Permission-State Presentation
Base44 May Be Asked To

Base44 may be prompted to create permission-state presentation components that:

Explain that future product actions may depend on role or permission context
Use future-oriented explanatory copy
Show a consistent place for permission-related language in the product UI
Remain clearly non-enforcing in the current pilot
Base44 Must Not Be Asked To

Base44 must not be prompted to create:

Real or simulated role checks
Fake “authorized” state
Fake “unauthorized” state
Fake “access denied” product outcome
Fake locked actions based on nonexistent user roles
Fake permission gate interactions
Any front-end claim that Base44 is enforcing backend product permissions
Required Permission-State Prompt Language

Any Phase D permission-state prompt must explicitly include language equivalent to:

This is future permission-dependent explanatory language only.
Do not simulate authorization logic.
Do not create fake permission approval or denial outcomes.
Do not present Base44 as the owner of product access-control truth.
Cross-Surface Prompting Discipline

Phase D prompts must preserve semantic continuity across:

Intake Workspace
Pilot Dashboard
Review Queue
Match Detail / Evidence View
Human Correction
Finalized Truth
Export Readiness

Any trust/error/permission presentation added during Phase D must:

Use consistent terminology
Avoid contradicting earlier Phase B or Phase C wording
Avoid changing established screen responsibility boundaries
Avoid redefining backend-dependent states as frontend-owned states
Prohibited Prompt Outcomes

A Base44 Phase D prompt is invalid if its output produces or implies any of the following:

Successful file upload
File-processing progress
OCR/parser completion
Ingestion complete
Run generated
Live review records created from Intake Workspace
Trust verification complete
Permission decision enforced
Backend error actually occurred
Frontend-owned operational product truth
Phase E backend binding begun
Required Review After Each Sensitive Prompt

Any Base44 output related to the following areas must be reviewed immediately before proceeding:

Intake Workspace output
Trust-state presentation output
Error-state presentation output
Permission-state presentation output

The review must check for:

Fake operational claims
Semantic leakage into Phase E
Fake backend state
Fake truth or permission outcome
Contradiction with Phase D execution boundary
Damage to previously constructed Phase A–C Pilot UI narrative

If semantic leakage occurs, a correction prompt must be issued before continuing.

Execution Outcome

Phase D Base44 construction may proceed only through prompts that preserve this prompting boundary.

The next required Mini-EPIC 33.6 governance artifact is:

PHASE_D_TARGET_INTAKE_TO_TRUST_ARTIFACT_DEFINITION.md
