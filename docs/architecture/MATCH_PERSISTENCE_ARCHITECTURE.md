# MATCH PERSISTENCE ARCHITECTURE

## Goal
Persist match-level reconciliation decisions before report aggregation so review, correction, feedback learning, and auditability can be built on durable records instead of ephemeral in-memory results.

## Why this exists
ReconciliationReport is an output summary, not a durable review substrate. Feedback and correction workflows require persisted match-level records linked to a reconciliation run.

## Core design
- reconciliation run produces match records
- match records are stored before final report completion
- report remains an aggregated projection of match records
- feedback will attach to match records, not to report summary rows

## Required properties
- one match record per invoice decision
- explicit run_id linkage
- deterministic selected payment linkage
- candidate payment ids preserved
- confidence and explanation preserved
- created_at timestamp preserved
- query by run_id supported

## Non-goals in this phase
- reviewer UI
- correction intake
- feedback loop activation
- rule promotion execution

## Next phases enabled by this design
- review session persistence
- correction event attachment to match_id
- feature snapshot persistence
- feedback-driven recommendation pipeline