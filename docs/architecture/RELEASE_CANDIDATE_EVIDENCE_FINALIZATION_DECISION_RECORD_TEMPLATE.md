
Release Candidate Evidence Finalization Decision Record Template
Purpose

This document defines the reusable decision record template used when a future reviewer evaluates whether a release candidate evidence record may proceed to evidence finalization.

This template is documentation-only.

It does not finalize release candidate evidence, approve a release candidate, approve deployment, create packages, publish artifacts, authorize CI release execution, or promote any environment.

Decision Record Identity
Decision record id: <to-be-assigned>
Decision record title: <release-candidate-evidence-finalization-decision>
Decision record version: <template-version-or-record-version>
Created at UTC: <timestamp>
Created by: <reviewer-or-author>
Review type: release-candidate-evidence-finalization-decision
Related readiness gate: Release Candidate Evidence Finalization Readiness Gate
Related Mini-EPIC: Mini-EPIC 32.43
Template source: RELEASE_CANDIDATE_EVIDENCE_FINALIZATION_DECISION_RECORD_TEMPLATE.md
Reviewed Source Identity

The reviewer must identify the exact source state being reviewed.

Repository: <repository-name-or-url>
Reviewed branch: <branch-name>
Reviewed commit SHA: <full-commit-sha>
Commit short SHA: <short-sha>
Working tree state at review time: <clean|dirty|unknown>
Review timestamp UTC: <timestamp>
Reviewer: <name-or-role>

The reviewed branch and commit must be explicit. A decision record must not rely on an implied, floating, or unstated source state.

Evidence Record Candidate Reference

The reviewer must identify the candidate evidence record being evaluated.

Candidate evidence record id: <candidate-id>
Candidate evidence record path or reference: <path-or-reference>
Candidate evidence record schema/version: <schema-or-version>
Candidate lifecycle state before review: <draft|created|reviewed|ready-for-finalization|other>
Candidate owner: <owner-or-role>
Candidate creation timestamp UTC: <timestamp-or-not-applicable>
Candidate review timestamp UTC: <timestamp-or-not-applicable>

This section references a future candidate record only. This template does not create that candidate record.

Readiness Gate Result

The reviewer must record the result of the finalization readiness gate before making a go/no-go decision.

Readiness gate name: Release Candidate Evidence Finalization Readiness Gate
Gate source: Mini-EPIC 32.43
Gate result: <pass|fail|deferred>
Gate evaluated at UTC: <timestamp>
Gate evaluator: <name-or-role>
Gate evidence reference: <path-or-reference>
Gate unresolved items: <none-or-list>
Gate blocking items: <none-or-list>

A failed or deferred readiness gate must not be recorded as approval to finalize evidence.

Required Evidence References

The reviewer must confirm that required evidence references are explicit and concrete.

Release candidate evidence candidate: <path-or-reference>
Release validation evidence: <path-or-reference>
CI validation reference: <path-or-reference>
Scenario regression evidence: <path-or-reference>
Operational validation evidence: <path-or-reference>
Contract validation evidence: <path-or-reference>
Full backend validation evidence: <path-or-reference>
Frontend lint evidence: <path-or-reference>
Frontend build evidence: <path-or-reference>
Prior lifecycle state evidence: <path-or-reference>
Review responsibility evidence: <path-or-reference>
Blocking finding evidence: <path-or-reference-or-none>

Evidence references must identify the evidence. They must not rely on vague statements such as "CI passed" without a concrete run, commit, branch, or evidence location.

CI Validation Reference Fields

The reviewer must record CI validation references without overstating their meaning.

CI provider: <GitHub Actions|other>
Workflow name: <workflow-name>
CI run id: <run-id>
CI run number: <run-number>
CI run URL: <url-or-reference>
CI branch: <branch-name>
CI commit SHA: <full-commit-sha>
CI trigger: <push|pull_request|manual|other>
CI status: <success|failure|cancelled|skipped|unknown>
Failed job or step, if any: <none-or-description>
Repair commit, if applicable: <full-commit-sha-or-none>
Re-run reference, if applicable: <run-id-or-none>

CI validation may support evidence finalization readiness only when it matches the reviewed source identity. CI validation alone does not approve deployment, publishing, release authorization, or environment promotion.

Lifecycle State Before Finalization

The reviewer must explicitly record the lifecycle state before any future finalization action.

Lifecycle object: <release-candidate-evidence-record>
State before decision: <draft|created|reviewed|ready-for-finalization|other>
State source reference: <path-or-reference>
State owner: <owner-or-role>
State timestamp UTC: <timestamp>
State mutation requested by this decision: none

This decision record must not silently mutate lifecycle state. Any future lifecycle transition must be explicit, auditable, and separately recorded.

Reviewer Responsibilities

The reviewer must confirm that they have completed the required responsibilities.

Confirmed reviewed commit and branch are explicit: <yes|no>
Confirmed evidence candidate reference exists: <yes|no>
Confirmed readiness gate result is recorded: <yes|no>
Confirmed required evidence references are concrete: <yes|no>
Confirmed CI validation reference is concrete: <yes|no>
Confirmed lifecycle state before finalization is explicit: <yes|no>
Confirmed blocking findings are recorded: <yes|no>
Confirmed decision does not claim release-candidate readiness: <yes|no>
Confirmed decision does not approve deployment: <yes|no>
Confirmed decision does not create or publish artifacts: <yes|no>
Confirmed decision does not authorize CI release execution: <yes|no>
Confirmed decision does not promote any environment: <yes|no>

A reviewer must not approve evidence finalization when required responsibilities are incomplete.

Blocking Findings

The reviewer must record any blocking findings.

Finding idSeverityDescriptionEvidence referenceRequired correctionBlocks finalization
<id>`<blockingmajorminor>`<description><reference>

If no blocking findings exist, the reviewer must state:

Blocking findings: none identified

The absence of blocking findings must be explicit. It must not be implied.

Go / No-Go Decision

The reviewer must record one decision.

Allowed decision values:

go-for-evidence-finalization
no-go-for-evidence-finalization
deferred

Decision:

Decision value: <go-for-evidence-finalization|no-go-for-evidence-finalization|deferred>
Decision rationale: <summary>
Decision timestamp UTC: <timestamp>
Decision reviewer: <name-or-role>
Required follow-up: <none-or-list>
Supersedes prior decision record: <none-or-reference>
Superseded by later decision record: <none-or-reference>

A go-for-evidence-finalization decision means only that the future evidence finalization action may proceed, subject to the post-decision constraints below.

It does not mean the evidence has already been finalized.

Post-Decision Constraints

After this decision is recorded, the following constraints apply:

The decision record must not overwrite source evidence.
The decision record must not silently mutate earlier lifecycle states.
A correction after finalization must create a new correction or supersession record.
A failed gate must not be recorded as a successful finalization decision.
A deferred decision must clearly state what remains unresolved.
Documentation-only decisions must not be treated as release execution.
The decision must remain traceable to the reviewed commit, branch, candidate evidence record, and CI validation reference.
Any later finalization action must be separately recorded.
Any later release-candidate readiness decision must be separately recorded.
Any later deployment approval must be separately recorded.
Non-Authorization Boundaries

This decision record template does not authorize any of the following:

Actual evidence finalization
Release-candidate readiness
Deployment approval
Package creation
Artifact publishing
CI release authorization
Environment promotion
Production rollout
Version tagging
Public release publication

The decision may only express whether a future reviewer permits the evidence finalization workflow to proceed.

Distinction Matrix
ConceptCovered by this decision record?Meaning
Readiness to proceed with evidence finalizationYesThe reviewer may decide whether finalization may proceed.
Actual evidence finalizationNoMust be performed and recorded separately.
Release-candidate readinessNoRequires a separate release-candidate readiness decision.
Deployment approvalNoRequires a separate deployment approval process.
Package creationNoRequires a separate packaging process.
Artifact publishingNoRequires a separate publishing process.
CI release authorizationNoRequires a separate CI release authorization process.
Environment promotionNoRequires a separate promotion process.
Template Usage Rules

When this template is used to create a real decision record:

Replace all placeholders with concrete values.
Preserve the non-authorization boundaries.
Preserve the distinction between readiness, finalization, release readiness, deployment, packaging, publishing, CI release authorization, and promotion.
Do not remove required identity, evidence, CI, lifecycle, reviewer, finding, and decision fields.
Store the completed decision record as a separate immutable or supersedable record.
Do not edit this template to represent a real decision.
Do not treat the completed record as evidence finalization unless a separate finalization action explicitly records that transition.
Template Status
Template status: defined
Execution status: not executed
Evidence finalization status: not finalized
Release-candidate readiness status: not claimed
Deployment status: not approved
Packaging status: not created
Publishing status: not published
CI release authorization status: not authorized
Environment promotion status: not promoted
