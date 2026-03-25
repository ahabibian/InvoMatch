\# InvoMatch — V3 Architecture Blueprint



\## Vision



InvoMatch is evolving from an invoice-matching utility into a \*\*deterministic financial execution platform\*\*.



The system is designed to execute financial processing jobs (such as reconciliation, validation, anomaly detection, staged financial workflows) with:



\* deterministic state transitions

\* optimistic concurrency guarantees

\* lease-based execution ownership

\* replayability and auditability

\* versioned pipelines

\* event-driven execution trace



This architecture intentionally prioritizes \*\*execution correctness, traceability, and extensibility\*\* over UI-first or dashboard-first product design.



\---



\## Product Positioning



\### What InvoMatch V3 is



\* An execution kernel for financial processing jobs

\* A lifecycle-aware orchestration layer

\* An API-first reconciliation and validation engine

\* A deterministic state machine for financial workflows

\* A platform foundation for future financial pipelines



\### What it is not



\* Not an accounting system

\* Not an ERP

\* Not an OCR tool

\* Not a reporting dashboard

\* Not a lightweight SMB bookkeeping helper



\---



\## High-Level Architecture



```

Client / Integrator / UI

&#x20;         |

&#x20;         v

&#x20;      API Layer

&#x20;         |

&#x20;         v

&#x20;  Application Use-Cases

&#x20;         |

&#x20;         v

&#x20;     Execution Core

&#x20;         |

&#x20;  +------+-------+

&#x20;  |              |

&#x20;  v              v

Pipeline Registry  Audit/Event Log

&#x20;  |              |

&#x20;  +------v-------+

&#x20;         |

&#x20;    Domain Services

&#x20;         |

&#x20;         v

&#x20;   Persistence Layer

&#x20;         |

&#x20;         v

&#x20;     Worker Runtime

```



\---



\## Core Layers



\### 1. Domain Layer



Contains \*\*pure deterministic financial logic\*\*.



Responsibilities:



\* invoice / payment models

\* matching logic

\* scoring rules

\* mismatch taxonomy

\* reconciliation report structure

\* lifecycle transition rules



Constraints:



\* no I/O

\* no database access

\* no HTTP

\* no orchestration logic



\---



\### 2. Application Layer



Implements \*\*use-cases and execution policies\*\*.



Examples:



\* submit reconciliation run

\* claim run

\* heartbeat lease

\* complete run

\* fail run

\* replay run

\* cancel run

\* requeue expired run



This layer understands \*\*workflow intent\*\*, not financial matching algorithms.



\---



\### 3. Execution Core (Primary Moat Layer)



This is the most strategically valuable component.



Responsibilities:



\* lifecycle state machine

\* optimistic concurrency enforcement

\* lease ownership semantics

\* retry eligibility

\* timeout recovery

\* idempotent execution guarantees

\* execution versioning



The execution core must remain:



\* deterministic

\* replay-safe

\* side-effect controlled



\---



\### 4. Pipeline Registry



Allows the system to scale beyond a single reconciliation workflow.



Capabilities:



\* pipeline type registration

\* step graph definition

\* ordered execution stages

\* required inputs contract

\* versioned pipeline definitions



Example pipeline types (future):



\* reconciliation

\* invoice validation

\* payment anomaly detection

\* batch classification

\* aggregation workflows



\---



\### 5. Persistence Layer



Current:



\* SQLite with WAL mode



Target:



\* PostgreSQL



Must persist:



\* runs

\* run versions

\* claims and leases

\* reports

\* decisions / corrections

\* audit events

\* pipeline definitions



\---



\### 6. Worker Runtime



Execution engine responsible for:



\* claiming eligible runs

\* executing pipeline stages

\* emitting execution events

\* lease heartbeat

\* failure recovery

\* replay execution



Workers must be \*\*stateless and replaceable\*\*.



\---



\## Execution Lifecycle



Target lifecycle vocabulary:



\* `created`

\* `queued`

\* `claimed`

\* `running`

\* `awaiting\_review`

\* `completed`

\* `failed`

\* `cancelled`

\* `expired`



\### Transition Model



```

created -> queued

queued -> claimed

claimed -> running

running -> awaiting\_review

running -> completed

running -> failed

claimed -> expired

running -> expired

awaiting\_review -> completed

awaiting\_review -> failed

expired -> queued

any\_non\_terminal -> cancelled

```



\---



\## Core Data Flow



\### Submit



1\. Client submits job input references

2\. Run entity is created

3\. Initial state persisted

4\. Run becomes eligible for queue



\### Claim



1\. Worker claims run

2\. Lease window is granted

3\. Attempt counter increments

4\. Ownership recorded



\### Execute



1\. Pipeline step resolved

2\. Domain service executes

3\. Intermediate outputs persisted

4\. Lease heartbeat maintained



\### Finalize



1\. Report stored

2\. Run transitions to terminal state

3\. Lease cleared

4\. Audit event appended



\### Recover



1\. Expired lease detected

2\. Run marked eligible

3\. New worker claims

4\. Execution resumes or retries



\---



\## Public API Boundaries (Planned)



Run management:



\* `POST /runs`

\* `GET /runs/{id}`

\* `GET /runs`

\* `POST /runs/{id}/cancel`

\* `POST /runs/{id}/replay`



Execution control:



\* `POST /runs/{id}/claim`

\* `POST /runs/{id}/heartbeat`

\* `POST /runs/{id}/complete`

\* `POST /runs/{id}/fail`



Results:



\* `GET /runs/{id}/report`

\* `GET /runs/{id}/events`



Human review:



\* `POST /runs/{id}/decisions`

\* `POST /runs/{id}/corrections`



\---



\## Storage Model (Conceptual)



\### reconciliation\_runs



\* run\_id

\* pipeline\_type

\* pipeline\_version

\* status

\* version

\* claimed\_by

\* lease\_expires\_at

\* attempt\_count

\* created\_at

\* updated\_at

\* started\_at

\* finished\_at

\* input\_ref

\* output\_ref

\* error\_message



\### run\_events (append-only)



\* event\_id

\* run\_id

\* event\_type

\* payload

\* actor

\* created\_at



\### run\_reports



\* run\_id

\* report\_version

\* payload



\### run\_decisions



\* decision\_id

\* run\_id

\* item\_id

\* decision\_type

\* reason

\* actor

\* created\_at



\### pipeline\_definitions



\* pipeline\_type

\* pipeline\_version

\* definition\_json



\---



\## Architecture Principles



1\. No direct state mutation outside use-cases

2\. All execution changes must be versioned

3\. Worker actions must be lease-aware

4\. Important lifecycle changes must emit events

5\. Pipelines must be versioned artifacts

6\. Domain logic must remain deterministic

7\. AI components (if added) must remain advisory



\---



\## Roadmap Phases



\### Phase A — Execution Kernel Completion



\* expired-run scanner

\* replay contract

\* event log

\* ownership-safe finalize

\* retry policy



\### Phase B — Pipeline Abstraction



\* step interface

\* pipeline registry

\* stage contracts

\* pipeline versioning



\### Phase C — Human Review Layer



\* awaiting\_review state

\* decision storage

\* correction capture

\* report diffing



\### Phase D — Runtime \& Scale



\* PostgreSQL migration

\* worker pool orchestration

\* retry backoff strategies

\* dead-letter semantics



\### Phase E — External Platformization



\* partner API

\* webhook delivery

\* tenant isolation

\* integration adapters



\---



\## Strategic Outcome



When completed, InvoMatch should function not as a feature tool, but as \*\*financial execution infrastructure\*\* suitable for:



\* enterprise finance teams

\* embedded fintech platforms

\* reconciliation service providers

\* financial data processors



The architecture is intentionally designed for \*\*high reliability, high traceability, and high extensibility\*\*.



