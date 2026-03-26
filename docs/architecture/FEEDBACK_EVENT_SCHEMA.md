# FEEDBACK EVENT SCHEMA

## Purpose
Define the canonical structure for reviewer correction events.

## Required entities
- review_session
- match_review
- correction_event
- feature_snapshot_reference

## Canonical correction event fields
- correction_id
- tenant_id
- run_id
- match_id
- invoice_id
- previous_payment_id
- corrected_payment_id
- correction_type
- reviewer_action
- reason_code
- reviewer_id
- reviewer_role
- occurred_at_utc
- original_decision
- original_confidence
- corrected_confidence
- feature_snapshot_ref
- rule_version
- engine_version
- ui_version
- notes

## Correction type categories
- accept_match
- reject_match
- replace_match_target
- split_match
- merge_match
- mark_duplicate_invoice
- mark_valid_unmatched
- vendor_normalization_fix
- amount_tolerance_override
- date_tolerance_override
- invoice_number_override

## Schema rules
- correction_id must be immutable
- correction event must be append-only
- original decision context must never be overwritten
- notes must be optional and non-authoritative
- reason_code must be normalized
- correction_type and reviewer_action must be explicit

## Validation expectations
- no correction event without match_id
- no replacement correction without previous and corrected target
- no event without reviewer identity
- no event without timestamp
- no event without original decision reference