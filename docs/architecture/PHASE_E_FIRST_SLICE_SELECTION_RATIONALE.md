
Phase E First Slice Selection Rationale
Purpose

This document explains why the first Phase E backend-binding slice is limited to:

Review Queue
Match Detail / Evidence
Selection Logic

The selected slice is:

Narrow in execution scope
Read-oriented rather than write-oriented
Directly aligned with the Financial Truth Layer demonstration narrative
Capable of exposing backend-governed review truth
Lower risk than action-heavy or operation-heavy surfaces
Resistant to Phase E integration sprawl
Why Review Queue

Review Queue is the natural entry point into the operator review workflow.

Binding this surface in a future execution step allows the Pilot UI to show:

Real review items returned by the backend
Real queue state derived from backend truth
Empty, loading, and unavailable conditions without frontend invention
Navigation into a detail surface grounded in backend facts

It does not require:

Correction submission
Finalization behavior
Export readiness decisions
Frontend-side reconstruction of review truth
Why Match Detail / Evidence

Match Detail / Evidence is the first surface that makes the InvoMatch product story visible.

It allows the operator to understand:

What backend match detail exists
Which evidence supports the reviewed item
Why the product is traceable rather than opaque
How review truth becomes inspectable without frontend recomputation

It is the highest narrative-value read surface in the initial Phase E step.

Why Pilot Dashboard Is Not the First Slice

Pilot Dashboard is not rejected permanently, but it is not selected for the first controlled slice.

Reasons:

It is more aggregation-heavy
It carries a higher risk of pseudo-summary or frontend-inferred truth
It is less directly connected to the core operator review narrative
Queue plus Detail / Evidence better expose the Financial Truth Layer story

Pilot Dashboard may be revisited later as a secondary binding candidate.

Why Human Correction Is Excluded

Human Correction is write-oriented and semantics-sensitive.

It requires prior clarity on:

Submission contract
Backend confirmation semantics
Rejection and error posture
Idempotency or retry behavior
Product state mutation rules

Entering Human Correction in the first slice would prematurely convert Phase E from controlled read binding into operational workflow execution.

Why Finalized Truth and Export Readiness Are Excluded

These surfaces depend on mature backend semantics around:

Finalized state retrieval
Readiness state interpretation
Traceability of finalization and export eligibility

They must not be live-bound before the UI can render them without inference or semantic invention.

Why Intake Workspace Is Excluded

Intake Workspace is explicitly outside the first controlled backend-binding slice.

It introduces ingestion-oriented operational behavior and should not become live merely to make a demo look richer.

Mini-EPIC 33.9 preserves the prior Phase E boundary:

Intake Workspace is not automatically eligible for live binding.
