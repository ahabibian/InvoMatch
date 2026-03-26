# STORAGE_ARCHITECTURE.md

## Status
Proposed

## Purpose

Define the long-term storage architecture for reconciliation runs in InvoMatch, with a clean migration path from local development storage to a production-grade PostgreSQL-backed persistence layer.

This document focuses on:

- reconciliation run persistence
- scalability limits of the current storage model
- backend abstraction boundaries
- migration path to PostgreSQL
- operational and schema evolution concerns

This document is specific to reconciliation run storage. It is not a generic database note.

The architecture must ensure that:

- workers remain stateless
- runs are recoverable
- concurrent execution is safe
- migration does not require domain rewrites
- future audit and analytics needs remain possible

---

## 1. Architectural Goals

The storage architecture must satisfy the following goals:

1. **Durability**  
   Reconciliation runs must survive process restarts, worker crashes, and host restarts.

2. **Deterministic recovery**  
   The system must be able to reconstruct the authoritative state of a run from durable storage.

3. **Concurrency safety**  
   Multiple workers must not process the same run concurrently unless explicitly allowed by design.

4. **Backend portability**  
   The service layer must not depend on SQLite-specific or PostgreSQL-specific behavior.

5. **Migration readiness**  
   The storage model must allow gradual movement from SQLite to PostgreSQL without changing domain semantics.

6. **Scalable read/write patterns**  
   The architecture must support growth in:
   - number of runs
   - concurrent workers
   - historical retention
   - audit and reporting needs

7. **Operational simplicity**  
   Local development should remain simple, but not at the cost of production correctness.

---

## 2. Scope

This document covers persistence for reconciliation execution state, including:

- reconciliation run metadata
- lifecycle status
- stage progress
- worker claim and lease data
- retry metadata
- timestamps
- references to input files and generated outputs
- execution diagnostics needed for recovery

This document does **not** define the full persistence model for invoices, payments, correction learning, or analytics warehouses. Those belong to separate architecture documents.

---

## 3. Core Principle

The authoritative unit of persistence is the **reconciliation run**.

A run is the storage boundary for execution state.

This means:

- the worker is not authoritative
- the API process is not authoritative
- the UI is not authoritative
- files on disk are not authoritative by themselves

The durable run record is the source of truth.

---

## 4. Storage Responsibilities

Storage for reconciliation runs is responsible for:

- creating run records
- reading run records
- updating run lifecycle state
- safely claiming runs for execution
- renewing claims and leases
- releasing or expiring claims
- marking terminal outcomes
- listing runs for operational views
- preserving enough metadata for audit and debugging

Storage is **not** responsible for:

- business matching decisions
- OCR logic
- orchestration policy
- UI formatting
- report rendering

Those components may write to storage, but storage does not own those decisions.

---

## 5. Non-Goals

This architecture does not try to:

- turn the run store into an event bus
- collapse all system persistence into a single table
- encode long-term analytics in the operational run store
- optimize first for ad hoc SQL convenience
- depend on engine-specific stored procedures as the primary domain mechanism

---

## 6. Logical Storage Model

### 6.1 Primary Entity: ReconciliationRun

Each reconciliation run represents one execution attempt over a specific set of inputs.

Recommended logical fields:

- `run_id`
- `tenant_id`
- `status`
- `current_stage`
- `claimed_by`
- `claim_expires_at`
- `retry_count`
- `max_retries`
- `invoice_csv_path`
- `payment_csv_path`
- `result_artifact_path` or `result_artifact_uri`
- `error_code`
- `error_message`
- `created_at`
- `updated_at`
- `started_at`
- `completed_at`
- `schema_version`
- `storage_version`
- `engine_version`
- `metadata_json`

### 6.2 Status Model

Recommended lifecycle states:

- `pending`
- `running`
- `awaiting_review`
- `completed`
- `failed`
- `cancelled`

Optional future states:

- `queued`
- `retry_scheduled`
- `expired`

### 6.3 Claim Model

To support safe worker concurrency, a run may be temporarily claimed by a worker using:

- `claimed_by`
- `claim_expires_at`

A claim is a lease, not ownership. If a worker dies, the lease expires and another worker may reclaim the run.

---

## 7. Physical Storage Layers

Long-term architecture should separate storage categories even if early implementations colocate them.

### 7.1 Operational Run Store

Authoritative storage for reconciliation run state.

Examples:

- SQLite in early stages
- PostgreSQL as the target store

### 7.2 Artifact Store

Storage for input and output files.

Examples:

- local filesystem in early stages
- object storage or S3-compatible storage later

### 7.3 Logs and Diagnostics

Structured logs should not be stored only inside the run row. Use application logs plus narrow storage references where needed.

---

## 8. Storage Backends by Phase

### Phase 1: Local Development / Early Single-Node

**Backend: SQLite with WAL mode**

Use cases:

- local development
- deterministic tests
- low-throughput single-node execution
- rapid iteration

Why it is acceptable:

- zero operational overhead
- simple file-based durability
- sufficient for one-process or low-concurrency scenarios

Limits:

- weak scaling for multiple writers
- operational fragility on network filesystems
- limited concurrency characteristics
- awkward fit for production-grade worker fleets

### Phase 2: Early Production / Controlled Deployment

**Backend: PostgreSQL**

Use cases:

- multi-worker execution
- production durability
- operational monitoring
- safer concurrency semantics
- richer indexing and migrations

Why it is the target:

- robust transaction semantics
- row-level locking support
- mature migration ecosystem
- strong operational tooling
- scalable enough for near and mid-term workloads

### Phase 3: Growth / Scale

**Backend: PostgreSQL with operational refinements**

Potential additions:

- partitioning by creation month or tenant
- read replicas for reporting
- archival strategy for historical runs
- dedicated artifact or object storage
- optional analytics offload

---

## 9. Storage Abstraction Boundary

This is the critical design decision.

The application must depend on a **Run Store interface**, not directly on SQLite or PostgreSQL.

### 9.1 Required Interface Characteristics

The storage boundary must expose domain-relevant operations such as:

- create run
- get run by id
- list runs with filters
- claim next eligible run
- renew claim
- update run progress
- mark awaiting review
- mark completed
- mark failed
- release claim when appropriate

### 9.2 What the Interface Must Not Leak

The abstraction must not expose:

- raw SQL semantics to service code
- SQLite cursor details
- PostgreSQL locking syntax
- engine-specific upsert behavior
- vendor-specific transaction quirks

If service code needs to know which database engine is active, the abstraction is already broken.

---

## 10. Recommended Repository Structure

```text
src/invomatch/
  domain/
    models.py
    enums.py

  services/
    reconciliation.py
    reconciliation_runs.py

  persistence/
    base.py
    sqlite/
      run_store.py
      schema.py
    postgres/
      run_store.py
      schema.py

  migrations/
    sqlite/
    postgres/

Alternative naming is fine, but the important part is:

one shared contract
backend-specific implementations isolated
migrations separated by engine where needed
11. SQLite Architecture Guidance

SQLite is acceptable only if treated honestly.

11.1 Recommended Usage
enable WAL mode
keep rows narrow
use explicit indexes
use UTC timestamps everywhere
normalize stored file paths deterministically
avoid storing large blobs in the run table
avoid long write transactions
keep claim and update flows explicit and short
11.2 Constraints to Respect

SQLite is not a worker-fleet database.

Do not pretend it is equivalent to PostgreSQL under load.

Specific concerns:

writer concurrency is limited
lock contention rises quickly under parallel execution
operational introspection is weaker
filesystem assumptions matter
container or distributed deployment patterns become fragile
11.3 When SQLite Must Be Considered Insufficient

Move off SQLite when any of the following becomes true:

multiple concurrent workers are standard
reconciliation runs are created continuously in production
claim races become operationally meaningful
uptime and recovery expectations increase
audit and operational visibility become customer-facing requirements
deployment involves multiple application instances
12. PostgreSQL Target Architecture

PostgreSQL is the target operational store for reconciliation runs.

12.1 Why PostgreSQL

PostgreSQL provides:

stronger concurrency handling
row-level locking primitives
durable transactional updates
mature indexing and migration workflows
better production observability
safer multi-instance deployment
12.2 Expected Table Shape

A primary reconciliation_runs table should remain narrow and operational.

Possible secondary tables later:

reconciliation_run_events
reconciliation_run_artifacts
reconciliation_run_errors
reconciliation_run_reviews

Do not overload the main run table with everything from day one.

12.3 Indexing Priorities

At minimum, expect indexes around:

run_id
status
created_at
claim_expires_at
tenant_id, created_at
13. Claiming and Concurrency Strategy

Concurrency correctness is a storage concern as much as a worker concern.

13.1 Desired Behavior

A worker should be able to claim one eligible run atomically.

Eligibility usually means:

status is claimable
no active lease exists, or lease has expired
13.2 Early SQLite Reality

SQLite does not provide the same concurrency profile as PostgreSQL. Early implementations may rely on carefully scoped transactions and conditional updates, but this is only acceptable for limited concurrency.

13.3 PostgreSQL Direction

In PostgreSQL, claim operations should be designed around atomic row selection and update semantics, typically using transactional locking patterns.

The important point is that the service contract should express claim_next_eligible_run(...), while backend implementations decide how to enforce it safely.

14. Data Model Evolution Strategy

Schema evolution must be treated as normal, not exceptional.

14.1 Version Fields

Persist version markers such as:

schema_version
storage_version
engine_version

These help with:

migration compatibility
audit and debugging
backfill tooling
behavior traceability across deployments
14.2 Forward-Compatible Expansion

Prefer additive changes first:

add nullable columns
backfill if needed
switch application reads
later enforce stricter constraints

Avoid destructive schema changes unless clearly scheduled and operationally safe.

14.3 Avoid JSON-as-Escape-Hatch Abuse

A bounded metadata_json field is acceptable.

It is not acceptable to continuously bypass schema design by dumping evolving state into arbitrary JSON blobs.

That path creates:

poor queryability
migration ambiguity
hidden coupling
audit weakness
15. Migration Path: SQLite to PostgreSQL

This section is the main point of the document.

15.1 Rule 1: Migrate the Backend, Not the Domain

The migration must not require rewriting:

reconciliation services
domain models
lifecycle semantics
worker orchestration logic

If those layers must change significantly, the abstraction was poorly designed.

15.2 Rule 2: Freeze the Contract Before Migrating Engines

Before moving to PostgreSQL:

stabilize the run store interface
stabilize lifecycle semantics
stabilize status transitions
stabilize claim semantics
remove SQLite-specific assumptions from service code
15.3 Rule 3: Keep IDs and State Semantics Stable

The following must remain stable across migration:

run_id
lifecycle statuses
timestamp meanings
retry semantics
claim and lease meaning
artifact reference semantics
15.4 Recommended Migration Sequence
Step 1

Harden the storage interface and tests.

Step 2

Ensure the SQLite implementation conforms strictly to the interface contract.

Step 3

Create a PostgreSQL implementation behind the same contract.

Step 4

Run the same contract tests against both backends.

Step 5

Introduce migration tooling for historical data export and import.

Step 6

Deploy PostgreSQL in non-critical or shadow mode.

Step 7

Switch production write and read paths to PostgreSQL.

Step 8

Retain SQLite only for local development and selected test scenarios.

16. Testing Strategy for Storage Portability

A migration path without backend contract tests is fake.

16.1 Required Test Layers
Contract Tests

The same test suite must run against:

SQLite implementation
PostgreSQL implementation

These tests verify:

create, read, and update behavior
lifecycle transitions
claim semantics
lease expiry behavior
terminal state enforcement
Migration Tests

Verify that:

exported SQLite runs can be imported into PostgreSQL
timestamps remain intact
statuses remain intact
artifact references remain intact
Failure Recovery Tests

Verify:

worker crash after claim
lease expiry
reclaim by a new worker
idempotent terminal writes where applicable
17. Scalability Strategy

Scalability should be approached by separating operational load types.

17.1 Operational Writes

Primary operational writes:

run creation
claim updates
progress updates
terminal state writes

These must remain fast and narrow.

17.2 Historical Reads

Operational UIs may need:

recent runs
status filters
failure inspection
review queues

These should be index-supported, not full-table scans.

17.3 Analytics and BI

Do not burden the operational run store with all reporting use cases.

As scale increases:

emit analytics asynchronously
replicate or export historical run data
build reporting views outside the hot execution path
18. Retention and Archival

Long-term storage needs an explicit retention policy.

Recommended approach:

keep recent operational runs in the hot table
archive old terminal runs by time window
preserve artifacts according to retention class
keep audit-relevant metadata longer than ephemeral diagnostics

Future options:

cold PostgreSQL partitions
object-storage archival for reports
warehouse export for historical analytics
19. Operational Concerns
19.1 Time

Use UTC consistently for all persisted timestamps.

19.2 Path Handling

Do not store OS-dependent path formats inconsistently. Normalize persisted file references deterministically.

19.3 Large Payloads

Do not store large OCR blobs or full reports directly in the main run row.

19.4 Observability

Storage operations should emit structured logs and metrics around:

create latency
claim latency
claim conflicts
update failures
stale lease recovery
terminalization counts
20. Risks
Risk 1: Overfitting to SQLite

If service code relies on SQLite quirks, PostgreSQL migration will become a rewrite.

Risk 2: Overloading the Run Row

If the main table becomes a dumping ground, performance and migration clarity degrade.

Risk 3: Weak Claim Semantics

If claims are not stored and enforced properly, duplicate execution becomes likely.

Risk 4: Mixing Artifacts with Operational State

If large files or blobs are mixed into hot operational storage, scalability suffers.

Risk 5: Premature PostgreSQL-Specific Design

If the abstraction is skipped and code targets PostgreSQL directly too early, local development and portability degrade.

21. Decisions
Decision 1

The authoritative persistent unit for execution state is the reconciliation run.

Decision 2

The application will depend on a storage interface, not a database engine.

Decision 3

SQLite remains acceptable for local development and low-concurrency environments only.

Decision 4

PostgreSQL is the target production-grade operational store.

Decision 5

Artifacts and operational run state are separate storage concerns.

Decision 6

Migration to PostgreSQL must preserve domain semantics and service contracts.

22. Immediate Implementation Guidance

The next implementation steps should be:

finalize the run store interface
ensure current SQLite code conforms to that interface cleanly
remove engine leakage from service code
document lifecycle-safe storage operations
create PostgreSQL implementation skeleton
add backend contract test suite
define export and import format for run migration
23. Exit Criteria for This Epic

This epic is complete when all of the following are true:

a clear storage contract exists for reconciliation runs
SQLite is treated as an implementation, not the architecture
PostgreSQL target design is explicit
migration path is defined step by step
contract tests are planned for both backends
storage responsibilities and non-goals are clear
scalability boundaries are documented honestly
24. Summary

InvoMatch should treat reconciliation run persistence as a durable operational subsystem, not a convenience layer.

SQLite is a valid early backend, but not the long-term architecture.

The long-term architecture is:

domain-defined storage contract
backend-isolated implementations
PostgreSQL as the production operational store
separate artifact storage
explicit migration and testing strategy

That is the only path that keeps execution semantics stable while allowing the system to scale.