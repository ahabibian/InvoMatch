# Release Candidate Evidence Lifecycle Transition Decision Record Template

## Purpose

This document defines the required template for recording the outcome of any future release-candidate evidence record lifecycle transition review.

The template builds on:

- Mini-EPIC 32.35 - Release Candidate Evidence Record Creation Gate Definition
- Mini-EPIC 32.36 - Release Candidate Evidence Record Lifecycle State Transition
- Mini-EPIC 32.37 - Release Candidate Evidence Lifecycle Transition Review Checklist

A lifecycle transition decision record is a governance artifact only. It records the review decision for a requested lifecycle transition. It does not execute the transition by itself.

## Non-Release Boundary

A lifecycle transition decision record does not:

- create a release candidate
- create a release-candidate evidence record instance
- execute a lifecycle transition
- mutate lifecycle state
- create validation evidence
- run CI
- run validation packs
- generate packages
- publish artifacts
- deploy anything
- promote staging or production
- change runtime behavior
- change CLI behavior
- change manifest schema behavior
- change release identity behavior
- claim release-candidate readiness
- claim production readiness

## Required Decision Record Identity Fields

Every lifecycle transition decision record must include:

| Field | Requirement |
|---|---|
| decision_record_id | Stable identifier for the transition decision record. |
| decision_record_schema_version | Template/schema version used for the decision record. |
| created_at_utc | UTC timestamp when the decision record was created. |
| created_by | Human or system actor creating the decision record. |
| reviewer | Reviewer responsible for the lifecycle transition decision. |
| review_date_utc | UTC date or timestamp of the review decision. |
| related_evidence_record_id | Identifier of the evidence record under review. |
| related_evidence_record_path | Path or durable reference to the evidence record under review. |
| related_transition_review_checklist_reference | Reference to the completed transition review checklist from Mini-EPIC 32.37 or its future successor. |
| source_governance_references | References to Mini-EPIC 32.35, 32.36, 32.37, and any later applicable governance documents. |

## Required Source and Target Lifecycle State Fields

Every decision record must identify the requested lifecycle transition:

| Field | Requirement |
|---|---|
| current_lifecycle_state | Current lifecycle state before the requested transition. |
| requested_target_lifecycle_state | Requested target lifecycle state. |
| requested_transition_type | Transition category such as creation, finalization, repair, supersession, voiding, or rejection handling. |
| transition_requested_by | Actor requesting the transition. |
| transition_requested_at_utc | UTC timestamp of the request. |
| transition_request_reference | Link, issue, document, or operational reference explaining where the transition was requested. |
| transition_allowed_by_rules | Explicit yes/no/blocked result based on Mini-EPIC 32.36 lifecycle transition rules. |
| transition_rule_reference | Specific rule or section supporting the allowed, rejected, or blocked result. |

## Required Transition Reason Fields

Every decision record must explain why the transition was requested:

| Field | Requirement |
|---|---|
| transition_reason_summary | Concise summary of why the transition is requested. |
| transition_reason_detail | Detailed explanation of the transition request. |
| operational_context | Operational or release-process context, without claiming release readiness. |
| evidence_context | Evidence-related reason for the transition. |
| risk_context | Known risk, uncertainty, gap, or audit concern relevant to the transition. |
| dependency_context | Related records, repairs, supersessions, voiding actions, validation evidence, or review dependencies. |

## Reviewer Decision Outcomes

The reviewer decision must be one of the following explicit outcomes:

| Decision outcome | Meaning |
|---|---|
| accepted | Requested transition is accepted as governance-complete, subject to any separate execution mechanism. |
| rejected | Requested transition is rejected and must not proceed. |
| blocked | Requested transition cannot proceed because mandatory evidence, rules, or prerequisites are missing or failed. |
| requires_evidence | Requested transition cannot be accepted until additional real evidence is supplied. |
| requires_repair | Requested transition cannot be accepted until the evidence record or supporting material is repaired. |
| requires_supersession | Existing record must be superseded by another record before the requested transition can be accepted. |
| requires_voiding | Existing record must be voided because it is invalid, unsafe, misleading, or unusable. |
| finalized | Finalization transition is accepted only when required real validation evidence is present and referenced. |

## Required Reviewer Decision Fields

| Field | Requirement |
|---|---|
| reviewer_decision | One of the defined decision outcomes. |
| reviewer_decision_summary | Concise explanation of the decision. |
| reviewer_decision_detail | Detailed decision rationale. |
| decision_timestamp_utc | UTC timestamp when the decision was made. |
| decision_authority | Governance authority or rule allowing the reviewer to make the decision. |
| decision_confidence | Explicit confidence level or uncertainty note. |
| decision_limitations | Any limits, exclusions, or assumptions attached to the decision. |

## Required Checklist Result Fields

The decision record must capture the transition review checklist result:

| Field | Requirement |
|---|---|
| checklist_completed | Yes/no. Must be yes for accepted or finalized decisions. |
| checklist_reference | Durable reference to the completed checklist. |
| checklist_result | Passed, failed, partial, blocked, or not applicable. |
| checklist_failed_items | Required when checklist_result is failed, partial, or blocked. |
| checklist_missing_items | Required when checklist evidence is incomplete. |
| checklist_reviewer_notes | Reviewer observations from the checklist review. |
| checklist_outcome_supports_decision | Explicit yes/no explaining whether the checklist supports the decision. |

## Required Evidence Reference Fields

Every decision record must list the evidence reviewed:

| Field | Requirement |
|---|---|
| required_evidence_references | Evidence references required for this transition type. |
| supplied_evidence_references | Evidence references actually supplied. |
| validation_evidence_references | Real validation evidence references when required. |
| ci_evidence_references | CI evidence references when required. |
| local_validation_references | Local validation command/result references when relevant. |
| documentation_references | Related documentation references. |
| source_commit_reference | Commit SHA relevant to the evidence under review. |
| branch_reference | Branch relevant to the evidence under review. |
| working_tree_state_reference | Clean/dirty state evidence when relevant. |
| evidence_sufficiency_result | Sufficient, insufficient, failed, missing, stale, or not applicable. |

## Missing, Failed, and Incomplete Evidence Fields

If evidence is missing, failed, stale, or incomplete, the decision record must include:

| Field | Requirement |
|---|---|
| missing_evidence | Required list of missing evidence. |
| failed_evidence | Required list of failed evidence. |
| incomplete_evidence | Required list of incomplete evidence. |
| stale_evidence | Required list of stale or superseded evidence. |
| evidence_gap_impact | Explanation of how the evidence gap affects the transition request. |
| evidence_gap_resolution_required | Required action before the transition can proceed. |
| evidence_gap_owner | Owner responsible for resolving the gap, if known. |

## Repair Handling Fields

If the decision outcome is requires_repair, the decision record must include:

| Field | Requirement |
|---|---|
| repair_required | Must be yes. |
| repair_reason | Explanation of why repair is required. |
| repair_scope | Specific evidence record sections, references, commands, results, or metadata requiring repair. |
| repair_validation_required | Evidence required after repair. |
| repair_completion_reference | Reference to the repair record or future repair evidence, when available. |
| repair_must_precede_transition | Must be yes unless explicitly justified. |

## Supersession Handling Fields

If the decision outcome is requires_supersession, the decision record must include:

| Field | Requirement |
|---|---|
| supersession_required | Must be yes. |
| supersession_reason | Explanation of why the current record cannot remain authoritative. |
| superseded_record_id | Evidence record being superseded. |
| superseding_record_id | Replacement evidence record, if already known. |
| supersession_reference | Link or path to the supersession record or planned supersession action. |
| supersession_effect | Explanation of how audit traceability is preserved. |

## Voiding Handling Fields

If the decision outcome is requires_voiding, the decision record must include:

| Field | Requirement |
|---|---|
| voiding_required | Must be yes. |
| voiding_reason | Explanation of why the record must be voided. |
| voided_record_id | Evidence record proposed for voiding. |
| voiding_risk | Risk caused by keeping the record active. |
| voiding_reference | Link or path to the voiding action or future voiding record. |
| post_voiding_required_action | Required follow-up action after voiding. |

## Finalization-Specific Fields

If the requested transition is finalization, the decision record must require real validation evidence.

| Field | Requirement |
|---|---|
| finalization_requested | Must be yes for finalization transitions. |
| finalization_decision | accepted, rejected, blocked, requires_evidence, or requires_repair. |
| finalization_validation_evidence_required | Must be yes. |
| finalization_validation_evidence_references | Required references to real validation evidence. |
| finalization_ci_evidence_references | Required when CI evidence is part of the finalization gate. |
| finalization_local_evidence_references | Required when local validation is used as supporting evidence. |
| finalization_missing_evidence | Required when any finalization evidence is missing. |
| finalization_failed_evidence | Required when any finalization evidence failed. |
| finalization_readiness_boundary | Must state that finalization evidence does not by itself create deployment or production readiness. |

Finalization must not be accepted from placeholder evidence, assumed validation, undocumented validation, implied CI status, or stale evidence.

## Rejection and Blocking Fields

If the decision is rejected or blocked, the decision record must include:

| Field | Requirement |
|---|---|
| rejection_or_blocking_reason | Required explanation. |
| rejected_or_blocked_by_rule | Rule, checklist item, evidence requirement, or governance constraint causing the rejection/block. |
| required_before_reconsideration | Required evidence, repair, review, or supersession before reconsideration. |
| reconsideration_allowed | Yes/no. |
| reconsideration_conditions | Conditions under which the transition may be reviewed again. |

## Required Record Skeleton

Future decision records should use this skeleton:

text
# Release Candidate Evidence Lifecycle Transition Decision Record

## Decision Record Identity
- decision_record_id:
- decision_record_schema_version:
- created_at_utc:
- created_by:
- reviewer:
- review_date_utc:
- related_evidence_record_id:
- related_evidence_record_path:
- related_transition_review_checklist_reference:
- source_governance_references:

## Requested Transition
- current_lifecycle_state:
- requested_target_lifecycle_state:
- requested_transition_type:
- transition_requested_by:
- transition_requested_at_utc:
- transition_request_reference:
- transition_allowed_by_rules:
- transition_rule_reference:

## Transition Reason
- transition_reason_summary:
- transition_reason_detail:
- operational_context:
- evidence_context:
- risk_context:
- dependency_context:

## Reviewer Decision
- reviewer_decision:
- reviewer_decision_summary:
- reviewer_decision_detail:
- decision_timestamp_utc:
- decision_authority:
- decision_confidence:
- decision_limitations:

## Checklist Result
- checklist_completed:
- checklist_reference:
- checklist_result:
- checklist_failed_items:
- checklist_missing_items:
- checklist_reviewer_notes:
- checklist_outcome_supports_decision:

## Evidence References
- required_evidence_references:
- supplied_evidence_references:
- validation_evidence_references:
- ci_evidence_references:
- local_validation_references:
- documentation_references:
- source_commit_reference:
- branch_reference:
- working_tree_state_reference:
- evidence_sufficiency_result:

## Missing, Failed, and Incomplete Evidence
- missing_evidence:
- failed_evidence:
- incomplete_evidence:
- stale_evidence:
- evidence_gap_impact:
- evidence_gap_resolution_required:
- evidence_gap_owner:

## Repair Handling
- repair_required:
- repair_reason:
- repair_scope:
- repair_validation_required:
- repair_completion_reference:
- repair_must_precede_transition:

## Supersession Handling
- supersession_required:
- supersession_reason:
- superseded_record_id:
- superseding_record_id:
- supersession_reference:
- supersession_effect:

## Voiding Handling
- voiding_required:
- voiding_reason:
- voided_record_id:
- voiding_risk:
- voiding_reference:
- post_voiding_required_action:

## Finalization Handling
- finalization_requested:
- finalization_decision:
- finalization_validation_evidence_required:
- finalization_validation_evidence_references:
- finalization_ci_evidence_references:
- finalization_local_evidence_references:
- finalization_missing_evidence:
- finalization_failed_evidence:
- finalization_readiness_boundary:

## Rejection or Blocking
- rejection_or_blocking_reason:
- rejected_or_blocked_by_rule:
- required_before_reconsideration:
- reconsideration_allowed:
- reconsideration_conditions:

## Non-Release Boundary Statement
- This decision record is a governance artifact only.
- This decision record does not execute a lifecycle transition.
- This decision record does not create a release candidate.
- This decision record does not create validation evidence.
- This decision record does not run CI.
- This decision record does not generate packages.
- This decision record does not publish artifacts.
- This decision record does not deploy anything.
- This decision record does not claim release-candidate readiness.
- This decision record does not claim production readiness.


## Audit Rule

A lifecycle transition decision record is valid only as a record of review outcome. Any lifecycle state mutation, evidence record creation, release-candidate creation, validation execution, packaging, publishing, deployment, or environment promotion must be performed and evidenced through separate approved mechanisms.
