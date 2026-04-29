# EPIC 27 — Multi-Tenant & Data Isolation Model

## Objective

Introduce a multi-tenant data isolation model so that each organization operates inside an enforced logical boundary.

After this EPIC, InvoMatch must support:

- multiple organizations
- isolated ingestion batches
- isolated runs
- isolated review items
- isolated export artifacts
- isolated audit events
- tenant-safe recovery and restart behavior

This EPIC is about correctness of isolation, not billing, SSO, RBAC hierarchy, or cross-tenant collaboration.

---

## Core Principle

A SaaS system is not merely multi-user.

It is multi-boundary.

Every data access path must be scoped to a tenant boundary, and that boundary must be enforced by the system, not trusted from the client.

---

## Tenant Model

A tenant represents an organization boundary.

Canonical fields:

- tenant_id
- name
- status
- created_at
- updated_at

Initial tenant status values:

- active
- suspended
- disabled

Tenant identity must be system-generated and must not be supplied directly by public API clients for normal product operations.

---

## User to Tenant Association

Initial phase supports single-tenant users.

Every authenticated request must resolve:

user_id -> tenant_id

Rules:

- every authenticated user must belong to exactly one active tenant
- API handlers must receive tenant context from authentication/session context
- endpoints must not accept arbitrary tenant_id overrides
- tenant_id must not be trusted from request body, query params, or UI state

Future multi-tenant user switching is explicitly out of scope.

---

## Tenant Context

A canonical tenant context must be available to service and persistence layers.

Required context:

- tenant_id
- user_id
- authentication source
- request correlation id where available

This context becomes the execution boundary for all product operations.

---

## Tenant-Scoped Entities

The following entities must become tenant-scoped:

- ingestion batches
- ingestion source records
- reconciliation runs
- review cases
- review items
- user actions
- export artifacts
- audit events
- operational recovery records where applicable

Every persisted entity that belongs to product data must carry tenant_id.

---

## Data Isolation Rules

Hard rules:

1. No cross-tenant reads.
2. No cross-tenant writes.
3. No implicit default tenant.
4. No global queries in product paths.
5. No tenant_id accepted from client-controlled API payloads.
6. All store methods that read product data must require tenant_id.
7. All write paths must persist tenant_id.
8. Audit and traceability records must include tenant_id.
9. Recovery, retry, and startup repair must preserve tenant boundaries.
10. Tests must prove tenant A cannot access tenant B data.

---

## Persistence Layer Rules

Persistence models must include tenant_id.

Indexes must support tenant-scoped lookup patterns.

Minimum required index strategy:

- tenant_id + run_id
- tenant_id + ingestion_batch_id
- tenant_id + review_case_id
- tenant_id + artifact_id
- tenant_id + event_id
- tenant_id + timestamp for audit queries

Store interfaces must change from global access to tenant-scoped access.

Examples:

- get_run(run_id) becomes get_run(tenant_id, run_id)
- list_runs() becomes list_runs(tenant_id)
- get_review_cases(run_id) becomes get_review_cases(tenant_id, run_id)
- list_artifacts(run_id) becomes list_artifacts(tenant_id, run_id)
- query_audit_events(...) becomes query_audit_events(tenant_id, ...)

Global administrative queries are out of scope unless explicitly marked as internal-only and not reachable from product APIs.

---

## API Boundary Enforcement

Tenant isolation is enforced at the API boundary.

Rules:

- request auth resolves user_id and tenant_id
- API handlers pass tenant context downward
- clients cannot override tenant_id
- product responses may include tenant_id only if intentionally part of contract
- error responses must not reveal whether another tenant's resource exists

Forbidden behavior:

- /runs/{run_id} searching globally
- /review/{case_id} searching globally
- /artifacts/{artifact_id} searching globally
- audit query without tenant_id
- accepting tenant_id in request body for normal product APIs

---

## Audit Isolation Extension

Audit events must include tenant_id.

Audit queries must always be tenant-scoped.

Traceability chains must remain tenant-consistent:

- ingestion_batch tenant_id must match run tenant_id
- run tenant_id must match review tenant_id
- review tenant_id must match export tenant_id
- export tenant_id must match audit tenant_id

Cross-tenant trace links are invalid and must be rejected or treated as integrity violations.

---

## Runtime, Recovery, and Startup Repair Safety

Recovery and repair logic must be tenant-safe.

Rules:

- recovery scans must preserve tenant_id
- retry decisions must apply only to runs inside the same tenant
- startup repair must not repair or expose cross-tenant records
- operational visibility must be tenant-scoped in product paths

---

## UI Isolation

Minimal UI must reflect tenant scope.

Rules:

- users only see runs for their tenant
- tenant context is implicit in the authenticated session
- UI must not send arbitrary tenant_id for product operations
- no cross-tenant selector in this EPIC

---

## Implementation Plan

Phase 1 — Architecture and Contracts

- define Tenant model
- define UserTenantContext
- define tenant resolution rule
- update product and persistence contracts
- document forbidden global query patterns

Phase 2 — Persistence Foundations

- add tenant_id to core persisted entities
- update SQLite schemas and repositories
- update indexes
- update store interfaces to require tenant_id
- remove or isolate global query methods

Phase 3 — API and Service Enforcement

- resolve tenant context from authentication
- pass tenant context through service layer
- prevent request payload tenant override
- map unauthorized cross-tenant access to safe not-found or forbidden behavior

Phase 4 — Audit and Traceability

- extend audit event model with tenant_id
- enforce tenant-scoped audit queries
- validate tenant consistency across traceability chains

Phase 5 — UI Alignment

- ensure run lists are tenant-scoped
- ensure actions, review, export, and artifact views use implicit tenant context
- avoid tenant selector or manual tenant override

Phase 6 — Scenario and Regression Validation

- add Scenario 10 — Tenant Isolation Integrity
- re-run Scenario 1
- re-run Scenario 2
- re-run Scenario 4
- re-run Scenario 7
- re-run Scenario 8
- re-run Scenario 9

---

## Test Strategy

Required test categories:

1. Tenant model tests
2. User to tenant resolution tests
3. Persistence tenant-scope tests
4. API isolation contract tests
5. Audit tenant isolation tests
6. Runtime and recovery tenant-safety tests
7. UI tenant visibility tests
8. Scenario 10 system test
9. Regression scenario re-runs

Scenario 10 must validate:

- tenant A cannot read tenant B runs
- tenant A cannot resolve tenant B review items
- tenant A cannot export tenant B data
- tenant A cannot access tenant B artifacts
- tenant A audit query does not return tenant B events
- simultaneous tenant flows remain isolated
- recovery and restart preserve tenant boundaries

---

## Closure Criteria

EPIC 27 is complete only if:

- all core entities are tenant-scoped
- no product API performs unscoped data access
- no client-controlled tenant override exists
- audit events include tenant_id
- audit queries are tenant-scoped
- traceability chains remain tenant-consistent
- UI only shows tenant-local data
- Scenario 10 passes
- regression Scenarios 1, 2, 4, 7, 8, and 9 pass
- closure document captures implementation evidence and test evidence

---

## Non-Goals

This EPIC does not include:

- billing
- subscriptions
- advanced RBAC hierarchy
- cross-tenant sharing
- SSO
- external identity providers
- tenant analytics dashboards
- database sharding

---

## Status

Planned.