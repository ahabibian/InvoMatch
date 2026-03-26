# FEEDBACK PERSISTENCE CONTRACT

## Goal
Define the storage contract for feedback intelligence so that correction events, learning signals, candidate rule recommendations, promotions, and rollbacks are persisted in a deterministic, append-only, auditable form.

## Storage principles
- append-only correction history
- immutable event identity
- explicit version linkage
- tenant-safe partitioning
- auditability first
- no hidden mutation of historical context
- replay-safe retrieval

## Primary entities
- correction_event_record
- learning_signal_record
- candidate_rule_recommendation_record
- rule_promotion_record
- rule_rollback_record

## Correction event persistence requirements
- correction_id is immutable and unique
- correction events are append-only
- original decision metadata must never be overwritten
- feature snapshot linkage is mandatory
- reviewer identity is mandatory
- tenant_id must always be present
- engine_version and rule_version must be preserved as historical context

## Learning signal persistence requirements
- signal_id is immutable and unique
- signal extraction version must be stored
- all source ids must remain queryable
- evidence count and consistency values must be preserved
- candidate rule payload must be serializable and reproducible

## Candidate rule persistence requirements
- recommendation_id is immutable and unique
- promotion status must be explicit
- approver identity must be stored for approved/active rules
- replay test state must be queryable
- created and approved timestamps must be preserved
- activation and rollback must create separate audit records

## Promotion / rollback requirements
- rule activation must not overwrite recommendation creation state
- rollback must preserve prior activation history
- active rule lineage must be reconstructable from records alone
- status transitions must be explicit and auditable

## Query requirements
- get correction by id
- list corrections by tenant
- list corrections by run
- list corrections by match
- get signal by id
- list signals by tenant
- get recommendation by id
- list recommendations by status
- list promotions by recommendation
- list rollbacks by recommendation

## Future implementation notes
- sqlite backend should support append-only inserts and deterministic ordering
- postgres migration should preserve the same logical contract
- record serialization should remain backend-agnostic