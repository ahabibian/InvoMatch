# FEEDBACK INTELLIGENCE ARCHITECTURE

## Goal
Build a production-grade correction intelligence layer for InvoMatch so that user feedback is captured, normalized, audited, and transformed into safe learning signals without breaking determinism, traceability, or compliance.

## Why this exists
The matching engine is not enough. InvoMatch becomes stronger only when manual reviewer corrections are captured as structured intelligence and safely reused.

## Core principles
- no hidden learning
- no direct production mutation from raw feedback
- deterministic decision traceability
- human-in-the-loop enforcement
- versioned promotion and rollback
- tenant-safe boundaries
- auditability first

## Architecture scope
- correction event model
- reviewer action taxonomy
- reason codes
- feature snapshot linkage
- feedback persistence
- learning signal extraction
- recommendation pipeline
- promotion policy
- rollback strategy
- reviewer weighting

## Non-goals
- black-box self-modifying AI
- uncontrolled auto-learning
- direct production updates from single corrections
- unbounded tenant-wide rule propagation

## Main flow
1. matching engine creates decision
2. feature snapshot is persisted
3. reviewer accepts/rejects/overrides
4. correction event is stored
5. correction is normalized into learning input
6. learning signals are aggregated
7. candidate rules are generated
8. promotion policy evaluates safety
9. approved rules become versioned active rules
10. rollback remains available

## Required invariants
- every correction must reference an original decision
- every correction must reference a feature snapshot
- every learning signal must be reproducible
- every promoted rule must be versioned
- every promoted rule must be rollbackable
- reviewer disagreement must be measurable

## Open design questions
- tenant isolation boundary
- reviewer trust weighting design
- correction replay strategy
- storage partitioning for long-term audit history