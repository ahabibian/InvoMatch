\# RUN\_STORE\_CONTRACT.md



\## Status

Proposed



\## Purpose



Define the backend-independent contract for reconciliation run persistence in InvoMatch.



This document specifies the required storage semantics for reconciliation runs so that:



\- workers can safely claim and process runs

\- lifecycle transitions remain valid

\- terminal states are enforced

\- retries are controlled

\- storage backends can be swapped without changing domain semantics

\- SQLite and PostgreSQL implementations can be validated against the same behavioral contract



This is not an implementation document.

This is the behavior contract that all run store backends must satisfy.



\---



\## 1. Contract Scope



This contract applies to the persistence of reconciliation run execution state.



It covers:



\- run creation

\- run retrieval

\- run listing

\- run claiming

\- lease renewal

\- progress updates

\- review-state transition

\- failure transition

\- terminal transition

\- retry-safe storage behavior

\- storage-visible concurrency behavior



It does not define:



\- reconciliation matching logic

\- OCR logic

\- report rendering

\- API response models

\- analytics pipelines

\- invoice and payment domain persistence outside run execution state



\---



\## 2. Design Principle



The run store is the authoritative persistence boundary for execution lifecycle state.



This means:



\- a worker may hold an active lease, but does not own the run

\- in-memory process state is never authoritative

\- UI-visible status must derive from durable storage state

\- retry and recovery decisions must be possible from stored state alone



\---



\## 3. Core Entity Requirements



Each persisted run must support, at minimum, the following logical fields:



\- `run\_id`

\- `tenant\_id`

\- `status`

\- `current\_stage`

\- `claimed\_by`

\- `claim\_expires\_at`

\- `retry\_count`

\- `max\_retries`

\- `created\_at`

\- `updated\_at`

\- `started\_at`

\- `completed\_at`

\- `error\_code`

\- `error\_message`

\- `invoice\_csv\_path`

\- `payment\_csv\_path`

\- `result\_artifact\_uri` or equivalent reference

\- `schema\_version`

\- `storage\_version`

\- `engine\_version`

\- `metadata\_json`



Backends may store more fields, but they must not weaken this contract.



\---



\## 4. Lifecycle State Model



\### 4.1 Required States



At minimum, the contract must support:



\- `pending`

\- `running`

\- `awaiting\_review`

\- `completed`

\- `failed`

\- `cancelled`



\### 4.2 Optional Future States



Implementations may later support:



\- `queued`

\- `retry\_scheduled`

\- `expired`



These optional states must not break existing semantics.



\---



\## 5. Terminal State Rules



The following states are terminal:



\- `completed`

\- `failed`

\- `cancelled`



Once a run enters a terminal state:



\- it must not be claimable

\- it must not transition back to a non-terminal state

\- `completed\_at` or terminal-equivalent timestamp must be set

\- subsequent terminal writes must be either rejected or idempotently ignored according to backend policy



Recommended contract behavior:

\- terminal writes for the same final state may be treated as idempotent

\- conflicting terminal rewrites must be rejected



Example:

\- `running -> completed` is valid

\- `completed -> running` is invalid

\- `failed -> completed` is invalid unless explicitly modeled as a new run, not a mutation



\---



\## 6. Run Creation Contract



\### 6.1 Operation



The run store must provide a `create\_run(...)` operation.



\### 6.2 Required Guarantees



When `create\_run(...)` succeeds:



\- `run\_id` is unique

\- the run is durably persisted

\- the initial status is valid

\- `created\_at` is set

\- `updated\_at` is set

\- no active claim exists

\- retry counters are initialized deterministically



\### 6.3 Failure Behavior



If creation fails:



\- the caller must receive a failure signal

\- partial creation must not be silently treated as success

\- duplicate `run\_id` creation must be rejected



\---



\## 7. Read Contract



\### 7.1 Get by ID



The run store must provide `get\_run(run\_id)`.



It must:



\- return the authoritative durable state of the run

\- return a clear not-found result for missing runs

\- not fabricate or infer state from external systems



\### 7.2 Listing



The run store must provide a list operation with filters.



Minimum supported filters should include:



\- status

\- created\_at range

\- tenant\_id

\- claimability-related views where needed



List ordering must be deterministic.

If two runs have equivalent sort priority, a stable tiebreaker must exist.



Recommended default ordering:

\- `created\_at ASC, run\_id ASC`

or another explicit stable ordering, but never unspecified ordering.



\---



\## 8. Claim Contract



This is the most critical part of the contract.



\### 8.1 Operation



The run store must provide a `claim\_next\_eligible\_run(worker\_id, now, lease\_duration, ...)` operation or equivalent.



\### 8.2 Eligibility



A run is eligible for claim only if all of the following hold:



\- it is in a claimable state

\- it is not terminal

\- it has no active unexpired claim

&#x20; OR its existing claim has expired

\- it satisfies any explicit queue or retry constraints



\### 8.3 Required Guarantees



A successful claim must guarantee:



\- exactly one worker receives the claim result for that claim event

\- the run becomes leased to that worker in durable storage

\- `claimed\_by` is set

\- `claim\_expires\_at` is set

\- `updated\_at` is updated

\- the run is not simultaneously claimable by another worker before lease expiry



\### 8.4 Failed Claim Behavior



If no eligible run exists:



\- the operation must return a clean no-result outcome

\- it must not throw a fake error

\- it must not mutate unrelated runs



\### 8.5 Atomicity Requirement



Claim must be logically atomic.



This means the backend must guarantee that:



\- selection of the eligible run

\- assignment of the claim

\- persistence of lease metadata



happen as one storage-visible unit of correctness.



Backend implementations may achieve this differently, but the contract guarantee must remain the same.



\---



\## 9. Lease Renewal Contract



\### 9.1 Operation



The run store must provide `renew\_claim(run\_id, worker\_id, now, lease\_duration)` or equivalent.



\### 9.2 Required Guarantees



Renewal succeeds only if:



\- the run is currently claimed by the same worker

\- the run is not terminal

\- the claim has not been superseded



On success:



\- `claim\_expires\_at` is extended

\- `updated\_at` is updated



\### 9.3 Renewal Rejection



Renewal must fail if:



\- a different worker owns the claim

\- the run is terminal

\- the run does not exist

\- the lease is already lost under backend rules



Renewal must not silently steal ownership.



\---



\## 10. Release Contract



If the system supports explicit lease release, it must provide `release\_claim(run\_id, worker\_id)`.



Release may succeed only if:



\- the caller holds the active claim

\- the run is not terminal, unless the implementation combines release with terminalization



On success:



\- `claimed\_by` is cleared or equivalent ownership is removed

\- claim expiry is cleared or invalidated

\- `updated\_at` is updated



Explicit release is optional if terminal transitions always clear claim ownership automatically, but the backend behavior must be documented and consistent.



\---



\## 11. Progress Update Contract



\### 11.1 Operation



The run store must provide a progress update operation, such as:



\- `update\_progress(...)`

\- `update\_stage(...)`

\- `update\_status(...)`



\### 11.2 Required Guarantees



Progress updates must:



\- apply only to valid lifecycle transitions

\- update `updated\_at`

\- preserve run identity

\- preserve historical correctness of terminal state rules

\- reject invalid transitions



\### 11.3 Ownership Expectation



For mutable execution-stage updates, the active worker is normally expected to hold the claim.



Backends may enforce this strictly or the service layer may enforce part of it, but the contract must not allow ambiguous ownership semantics.



\---



\## 12. Awaiting Review Contract



The run store must support transition of a run into `awaiting\_review`.



This transition is valid only from explicitly allowed states such as:



\- `running`



When this transition succeeds:



\- the new status becomes durable

\- `updated\_at` is updated

\- the run is no longer claimable for normal processing unless explicitly modeled otherwise

\- any active claim should be cleared unless review is intentionally modeled under an active claim



Recommended behavior:

\- entering `awaiting\_review` clears active claim ownership



\---



\## 13. Failure Contract



The run store must support marking a run as failed.



A failure write must:



\- set status to `failed`

\- set terminal timestamp

\- store failure metadata where applicable

\- clear active lease ownership

\- prevent further claim



Failure writes may be idempotent when repeating the same outcome, but conflicting rewrites must not silently succeed.



\---



\## 14. Completion Contract



The run store must support marking a run as completed.



A completion write must:



\- set status to `completed`

\- set terminal timestamp

\- persist result artifact reference if available

\- clear active lease ownership

\- prevent further claim



Completion must be durable and must not depend on in-memory worker state after success is returned.



\---



\## 15. Retry Contract



\### 15.1 Principle



Retries must be visible in durable storage.

They must not exist only in process memory.



\### 15.2 Minimum Fields



Retry-aware behavior requires at minimum:



\- `retry\_count`

\- `max\_retries`



Optional fields may include:



\- `next\_retry\_at`

\- `last\_error\_code`

\- `last\_error\_at`



\### 15.3 Required Guarantees



If a run is retryable:



\- retry\_count increments durably

\- retry eligibility must be derivable from stored state

\- retry must not violate terminal state rules

\- exhausted retries must lead to a durable non-claimable outcome



\### 15.4 Recommended Rule



A run that exceeds retry policy should become terminally failed or move to a clearly non-claimable state such as `failed` or `awaiting\_review`, depending on policy.



\---



\## 16. Idempotency Expectations



Not all operations must be globally idempotent, but the contract must define the safe cases.



\### Recommended idempotent or conditionally idempotent operations:



\- `get\_run(run\_id)`

\- repeated terminal write of the same terminal state

\- repeated release by the same owner when already released, if explicitly designed that way



\### Non-idempotent operations:



\- `claim\_next\_eligible\_run(...)`

\- retry increment operations

\- state transitions that intentionally advance lifecycle



Implementations must not falsely imply idempotency where none exists.



\---



\## 17. Concurrency Guarantees



The run store must provide enough safety that two workers do not both successfully acquire the same active claim for the same run.



At minimum, the contract guarantees:



\- one active claim at a time per run

\- no valid double-claim before lease expiry

\- no terminal transition back to claimable state

\- no silent ownership theft on renewal



This does not require identical SQL or lock behavior across backends.

It requires identical externally visible correctness.



\---



\## 18. Time Semantics



All persisted timestamps must use UTC semantics.



The contract must treat the following as storage-visible time fields:



\- `created\_at`

\- `updated\_at`

\- `started\_at`

\- `completed\_at`

\- `claim\_expires\_at`



If the backend truncates precision differently, the implementation must still preserve correctness of ordering and lease logic.



\---



\## 19. Deterministic Ordering Requirement



Wherever the run store returns multiple runs, the ordering must be deterministic.



This applies to:



\- list operations

\- claim candidate selection

\- retry candidate selection



If priority ordering exists, it must have a deterministic fallback tiebreaker.



Never rely on implicit engine row order.



\---



\## 20. Backend Independence Rules



The contract must not encode storage-engine-specific assumptions into service semantics.



Service code must not need to know:



\- whether the backend uses SQLite or PostgreSQL

\- how row locking is implemented

\- whether upsert syntax differs

\- what cursor or transaction primitive is used internally



If service behavior changes by backend, the contract is broken.



\---



\## 21. Error Model Expectations



The run store should expose failures in stable categories such as:



\- not found

\- invalid transition

\- claim conflict

\- ownership conflict

\- terminal state violation

\- persistence failure



Exact exception classes may vary by language layer, but the semantic categories must remain stable.



Backends must not collapse all failures into generic storage exceptions if doing so destroys domain meaning.



\---



\## 22. Contract Test Requirements



Every backend implementation must pass the same contract-oriented tests.



At minimum, tests must cover:



\- create then get

\- duplicate create rejection

\- deterministic list ordering

\- single successful claim

\- no double-claim under contention

\- lease renewal by owner

\- renewal rejection by non-owner

\- transition to awaiting\_review

\- mark completed

\- mark failed

\- terminal state immutability

\- retry visibility in storage

\- reclaim after lease expiry

\- not-found behavior

\- invalid transition rejection



A backend that fails contract tests is not a valid run store backend.



\---



\## 23. SQLite Conformance Notes



SQLite may satisfy this contract for early-stage deployments, but only if:



\- claim logic is carefully scoped

\- writes are short

\- deterministic ordering is explicit

\- lease semantics are storage-visible

\- concurrency expectations remain within SQLite’s real limits



SQLite conformance does not imply worker-fleet scale readiness.



\---



\## 24. PostgreSQL Conformance Notes



PostgreSQL is expected to satisfy this contract in production environments with stronger concurrency characteristics.



The PostgreSQL backend should be designed so that:



\- claim atomicity is robust

\- transaction boundaries are explicit

\- indexing supports operational filters

\- lease and retry semantics remain identical to the contract



PostgreSQL may improve implementation strength, but it must not redefine domain semantics.



\---



\## 25. Decisions



\### Decision 1

The run store contract is backend-independent.



\### Decision 2

Claim semantics are part of the persistence contract, not just worker behavior.



\### Decision 3

Terminal state enforcement is mandatory.



\### Decision 4

Deterministic ordering is mandatory.



\### Decision 5

Retry visibility must be durable.



\### Decision 6

All backends must pass the same behavioral contract tests.



\---



\## 26. Exit Criteria



This contract is considered locked when:



\- the required operations are accepted

\- lifecycle semantics are explicit

\- terminal behavior is explicit

\- claim and lease rules are explicit

\- retry visibility is explicit

\- backend independence rules are explicit

\- contract tests can be derived directly from this document



\---



\## 27. Summary



The run store is not just a CRUD wrapper.

It is the durable lifecycle authority for reconciliation execution.



A valid run store backend must provide:



\- safe claim semantics

\- durable lifecycle transitions

\- terminal enforcement

\- deterministic ordering

\- retry visibility

\- backend-independent behavior



Without this contract, SQLite-to-PostgreSQL migration becomes guesswork and worker correctness becomes fragile.

