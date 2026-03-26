# LEARNING SIGNAL MODEL

## Purpose
Transform raw reviewer corrections into deterministic and explainable learning signals.

## Raw input sources
- correction events
- feature snapshots
- rule hit traces
- reviewer metadata

## Signal design principles
- deterministic
- explainable
- threshold-based
- tenant-aware
- replayable
- promotion-safe

## Example signal types
- vendor_alias_discovered
- invoice_number_ocr_confusion
- amount_tolerance_too_strict
- amount_tolerance_too_wide
- date_window_too_strict
- date_window_too_wide
- payment_reference_more_reliable
- duplicate_detection_false_positive
- duplicate_detection_false_negative
- low_confidence_region_repeatedly_corrected

## Required signal fields
- signal_id
- tenant_id
- signal_type
- source_correction_ids
- source_match_ids
- source_feature_snapshot_refs
- evidence_count
- consistency_score
- reviewer_weight_score
- extracted_at_utc
- extraction_version
- candidate_rule_payload

## Guardrails
- single correction cannot create active production behavior
- low-consistency signals must stay inactive
- cross-tenant promotion is forbidden unless explicitly designed
- every signal must be reproducible from stored inputs