# EPIC 26 - Audit & Traceability Persistence

## 1. Problem

The system currently generates audit signals across:

- operational lifecycle
- recovery and repair
- security (authentication / authorization)
- ingestion traceability

However:

- audit data is not persisted
- audit data is not queryable
- audit streams are fragmented (operational vs security)
- no durable audit evidence exists

This makes:

- debugging unreliable
- root cause analysis incomplete
- security investigation weak
- system trust unverifiable

---

## 2. Objective

Introduce a durable, append-only, queryable audit subsystem that:

- persists all critical system events
- provides deterministic ordering
- survives restart and recovery
- enables traceability across ingestion -> run -> review -> export -> security

---

## 3. Existing Foundations

### Operational Audit
- event_id
- run_id
- lifecycle transitions
- correlation_id
- in-memory repository

### Security Audit
- user / role / request context
- in-memory service
- no repository abstraction

### Traceability
- ingestion-level references (payload fingerprint, schema version)

---

## 4. Design Strategy

We do NOT rewrite existing audit systems.

We introduce:

### 4.1 Persistent Audit Envelope

A unified storage model:

- sequence_id (ordering)
- event_id
- occurred_at
- recorded_at
- event_type
- category (operational | security)
- run_id (optional)
- user_id (optional)
- correlation_id (optional)
- outcome
- metadata_json

The persistent model must preserve operationally important fields through structured columns or deterministic metadata mapping, including:

- decision
- reason_code
- previous_operational_state
- new_operational_state
- related_failure_code
- attempt_number
- capability
- request_path
- request_method

### 4.2 Adapter Layer

We wrap existing audit emitters:

- OperationalAuditService -> persistent audit repository
- SecurityAuditService -> persistent audit repository

No direct SQL calls from domain services.

### 4.3 Audit Store

- SQLite-based
- append-only
- no mutation
- deterministic ordering via sequence_id

### 4.4 Query Surface

Minimal API:

- fetch by run_id
- fetch by user_id
- fetch by event_type
- time filtering
- deterministic ordering

---

## 5. Integrity Rules

- no silent loss of critical events
- no mutation of historical records
- deterministic ordering required
- timestamps must be consistent
- audit must not corrupt lifecycle state

---

## 6. Non-Goals

- dashboards
- analytics UI
- external observability integration
- multi-tenant partitioning

---

## 7. Implementation Plan

1. Define persistent audit event model
2. Implement SQLite audit store
3. Build audit recorder / query services
4. Integrate persistence for:
   - operational audit
   - security audit
5. Add query surface
6. Execute regression scenarios
7. Validate audit integrity (Scenario 9)

---

## 8. Test Strategy

### Unit
- append-only guarantee
- ordering correctness
- event model validation
- query filtering

### Integration
- lifecycle -> audit
- security -> audit
- recovery -> audit
- startup repair -> audit

### Scenario
- Scenario 9 - Audit Persistence Integrity

---

## 9. Closure Criteria

- audit persists all critical events
- audit survives restart
- audit reflects real system behavior
- audit is queryable
- no critical event is lost
- all scenarios pass

---

## 10. Key Principle

If the system cannot explain what happened, it cannot be trusted.