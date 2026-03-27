# InvoMatch - EPIC TRACKER

## Project Goal
AI-driven financial reconciliation system with:
- deterministic execution
- explainable matching
- learning from human feedback
- enterprise-grade auditability

---

## EPIC STATUS OVERVIEW

| Epic | Name | Status | Notes |
|------|------|--------|------|
| 1 | Execution Lifecycle Engine | DONE | lease + concurrency + retry implemented |
| 2 | Persistence & Storage Strategy | PARTIAL | sqlite stable, postgres/migration missing |
| 3 | Matching Intelligence Engine | PARTIAL | base scoring exists, not production-ready |
| 4 | Feedback & Learning System | IN PROGRESS | structure exists, no governance |
| 5 | Review & Audit System | NOT STARTED | critical for feedback validation |
| 6 | Rule Engine & Governance | NOT STARTED | no promotion / rollback logic |
| 7 | Replay & Evaluation Engine | NOT STARTED | no regression safety |
| 8 | API & Product Layer | PARTIAL | base endpoints exist, not productized |
| 9 | Observability & Reliability | NOT STARTED | no real telemetry layer |
| 10 | SaaS & Scalability | NOT STARTED | no tenant model / infra design |

---

## CURRENT PHASE

System Stage:
Core Engine (NOT production-ready)

Reality Check:
- System is NOT safe for production
- Learning is NOT controlled
- No evaluation or rollback mechanism exists
- No audit-grade guarantees yet

---

## BLOCKERS

1. Feedback system without review -> unsafe learning
2. No replay -> no way to verify improvements
3. No rule governance -> risk of model drift
4. Weak observability -> no debugging capability

---

## NEXT REQUIRED EPICS (STRICT ORDER)

1. EPIC 5 - Review & Audit System
2. EPIC 6 - Rule Engine & Governance
3. EPIC 7 - Replay & Evaluation Engine

DO NOT continue learning work before these are defined.

---

## DEFINITION OF "SYSTEM READY"

System can be considered "real" only if:

- deterministic execution
- persistent storage
- explainable matching
- feedback loop
- review system
- rule governance
- replay capability
- observability
- API boundary

Until then -> this is a prototype system, NOT a product.

---

## NOTES

This tracker is the single source of truth.

Every EPIC must:
- produce a document
- pass exit criteria
- be closed with a closure file

No EPIC is considered DONE without:
- documentation
- tests
- clear boundaries