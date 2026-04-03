# RUN VIEW ARCHITECTURE

Status: Proposed  
EPIC: 11  
Title: Unified Run View Read Model

## 1. Purpose

EPIC 11 introduces a unified, product-facing run read model.

The current product read experience is fragmented across multiple endpoint surfaces:
- run details
- review state
- export state
- artifact state

This fragmentation makes the UI and future integration layers responsible for reconstructing a complete run picture by calling multiple endpoints and interpreting partial states.

That is not an acceptable long-term product boundary.

The system now requires a single, deterministic, contract-driven read surface for a run.

The result of this EPIC is a unified **Run View** projection:
- product-facing
- read-only
- deterministic
- contract-stable
- free from domain leakage

This Run View becomes the primary read surface for:
- UI
- integration consumers
- future product layers
- future reporting and analytics projections

---

## 2. Problem Statement

The system already contains implemented subsystems for:
- execution lifecycle
- matching
- review
- action execution
- export delivery
- artifact resources

However, these subsystems are exposed through separate product-facing or semi-product-facing routes.

As a result:
- the UI does not have one canonical read model for a run
- consumers must reconstruct product state from multiple calls
- state interpretation logic becomes duplicated outside the backend
- consistency becomes harder to enforce
- future product surfaces inherit avoidable complexity

This is a product architecture gap, not a missing domain capability.

---

## 3. Architectural Goal

Introduce a unified product read model named **ProductRunView**.

This model must aggregate:
- run lifecycle state
- match summary
- review summary
- export summary
- artifact references

This model is explicitly:
- NOT a domain model
- NOT a persistence model
- NOT an internal orchestration model

It is a **read model / projection** designed for stable product consumption.

---

## 4. Primary Design Principles

### 4.1 Product Boundary First
The Run View exists to define the product read boundary, not to mirror internal implementation.

### 4.2 No Domain Leakage
Internal domain entities, store-specific metadata, handler outputs, or storage implementation details must never appear in the Run View.

### 4.3 Read-Only Projection
The Run View performs no state changes, emits no events, and introduces no side effects.

### 4.4 Deterministic Output
For the same persisted system state, the Run View must produce the same response shape and ordering.

### 4.5 Explicitness Over Inference
Missing review, export unavailability, or absent artifacts must be represented explicitly in product terms, not hidden through omission.

### 4.6 Stable Contract Surface
Field names, timestamp semantics, nullability, and ordering rules must be deliberate and documented.

---

## 5. Proposed Read Model

## 5.1 ProductRunView

The product read model will contain:

- run_id
- status
- created_at
- updated_at
- match_summary
- review_summary
- export_summary
- artifacts

This is the canonical product-facing projection of a reconciliation run.

---

## 5.2 Model Sections

### A. Run Identity and Lifecycle
Contains:
- run_id
- status
- created_at
- updated_at

Purpose:
- identify the run
- expose the canonical product lifecycle state
- support list-to-detail navigation and stable UI rendering

### B. Match Summary
Contains a lightweight summary of reconciliation outcome.

Purpose:
- allow UI and integrations to understand result shape without consuming raw match internals
- expose high-level run outcome, not internal matching structures

Examples of suitable fields may include:
- total records
- matched count
- unmatched count
- ambiguous count

Exact field set will be finalized in the API contract document.

### C. Review Summary
Contains explicit review state for the run.

Purpose:
- indicate whether review exists
- indicate whether review is pending, in progress, completed, or not required
- avoid forcing consumers to infer review status from separate review endpoints

### D. Export Summary
Contains explicit export state for the run.

Purpose:
- communicate export readiness/status in product terms
- avoid leaking storage, delivery, or artifact implementation details

### E. Artifacts
Contains lightweight references to available export artifacts.

Purpose:
- expose product-usable artifact availability
- support download/navigation surfaces
- keep artifact representation lightweight and deterministic

Artifacts are references, not full storage entities.

---

## 6. Read Model Boundaries

The Run View must include:
- only product-safe fields
- only fields needed for run-centric consumption
- explicit summaries rather than raw internal objects

The Run View must not include:
- internal store metadata
- execution claims or lease details
- worker or orchestration internals
- internal review decision audit records unless explicitly projected into product-safe summary fields
- storage backend paths
- file system implementation details
- infrastructure-specific delivery state

---

## 7. Aggregation Service

## 7.1 Service Name
A dedicated service will be introduced:

**RunViewQueryService**

## 7.2 Responsibility
This service is responsible for assembling ProductRunView from existing product/domain-safe sources.

Core responsibilities:
- fetch the run
- derive lifecycle-facing product fields
- fetch review projection/safe review state
- fetch export/artifact product-safe metadata
- aggregate into a single ProductRunView

## 7.3 Service Characteristics
The service must:
- be read-only
- be deterministic
- produce stable projection output
- enforce product boundary rules
- avoid side effects
- avoid leaking subsystem internals

## 7.4 What This Service Must Not Become
RunViewQueryService must not become:
- a workflow engine
- an orchestration coordinator
- a mutation entry point
- a storage abstraction bypass
- a dumping ground for raw subsystem models

Its role is projection assembly only.

---

## 8. Source-of-Truth Strategy

The Run View is an assembled projection. Its sections come from different existing sources of truth.

Expected source domains:

- run lifecycle data → run store / run product mapping
- match summary → run result summary or existing product-safe reconciliation summary
- review summary → review subsystem projection
- export summary → export subsystem product-safe state
- artifacts → artifact resource repository / product-safe artifact references

This EPIC does not redefine subsystem ownership.
It defines the product-level read composition across them.

---

## 9. State Consistency Rules

The Run View must apply explicit consistency rules so that the product contract stays coherent.

### 9.1 Export Readiness Rule
If the run is not in a completed-compatible state, export_summary must represent a product-safe not_ready state.

Export readiness must not be inferred merely from artifact existence.

### 9.2 Review Explicitness Rule
If there is no review state for a run, review_summary must still be present in explicit product form.
No hidden omission.

### 9.3 Artifact Non-Inference Rule
Artifact presence must not automatically imply:
- export readiness
- review completion
- run completion correctness

Artifacts only represent artifact availability.

### 9.4 Storage Isolation Rule
Export summary and artifact fields must not reveal storage implementation behavior such as:
- filesystem paths
- storage driver type
- internal bucket/container naming
- local delivery mechanics

### 9.5 Timestamp Consistency Rule
Timestamps must use a single documented format and semantic interpretation across the entire Run View contract.

### 9.6 Ordering Rule
Artifacts must be returned in deterministic order.
The contract document will define the exact ordering basis.

---

## 10. API Surface

A new endpoint will be introduced:

GET /api/reconciliation/runs/{run_id}/view

This endpoint becomes the primary read entry point for a single run.

Its role:
- provide one canonical run-centric product read response
- reduce client-side reconstruction logic
- centralize product-state interpretation in backend
- prepare the platform for future richer product read models

This endpoint is read-only.

---

## 11. Error Behavior

At minimum:
- missing run must return a not found response
- partial subsystem absence must not crash the projection if product-safe defaults can be produced
- response shape must remain contract-consistent

Subsystem gaps should be translated into explicit product-safe summaries when possible rather than exposed as internal failures.

Precise error behavior will be finalized in the API contract document.

---

## 12. Nullability and Explicitness Strategy

The Run View should prefer explicit structured summaries over silent omission.

Guiding rule:
- if a section is conceptually part of the run product view, it should usually be present
- lack of underlying subsystem data should be represented through explicit summary state, not hidden absence

This matters especially for:
- review_summary
- export_summary
- artifacts

---

## 13. Relationship to Existing Endpoints

This endpoint does not necessarily remove existing endpoints immediately.

Existing endpoints may still exist for:
- focused subsystem detail
- deeper drill-down
- backward compatibility
- specialized workflows

However, the Run View becomes the primary UI-facing single-run read surface.

That means new UI/product consumers should not need to reconstruct the run state from multiple endpoints.

---

## 14. Non-Goals

This EPIC does not introduce:
- mutation endpoints
- background aggregation jobs
- caching
- denormalized persistence projections
- pagination inside run view
- performance tuning beyond correctness and determinism

This is a contract and architecture hardening EPIC.

---

## 15. Risks

### 15.1 Boundary Creep
Risk:
The projection starts absorbing raw subsystem internals.

Mitigation:
Use explicit product schemas and mapping boundaries only.

### 15.2 Ambiguous State Semantics
Risk:
Review/export/artifact meaning becomes unclear or overlapping.

Mitigation:
Document explicit consistency rules and contract-level states.

### 15.3 Hidden Coupling
Risk:
The query service becomes tightly coupled to volatile internal structures.

Mitigation:
Depend on product-safe access patterns and summary abstractions where possible.

### 15.4 Client Contract Instability
Risk:
The model changes frequently after introduction.

Mitigation:
Define strict contract document before implementation.

---

## 16. Implementation Plan

Phase 1:
- define architecture
- define contract
- finalize section semantics

Phase 2:
- introduce ProductRunView schema(s)
- implement RunViewQueryService
- add API route

Phase 3:
- add service tests
- add API tests
- add contract-shape tests
- verify deterministic ordering and explicit defaults

Phase 4:
- write EPIC closure document

---

## 17. Exit Criteria

EPIC 11 is complete when:

- a single endpoint returns a complete product run view
- the UI can rely on this endpoint as its primary single-run read surface
- no domain internals leak into the response
- review/export/artifact semantics are explicit and deterministic
- contract rules are documented and test-enforced
- implementation remains read-only and side-effect free

---

## 18. Summary

EPIC 11 closes a product architecture gap.

The system already performs execution, matching, review, export, and artifact delivery.
What is missing is a single, trustworthy, product-level run projection.

The Run View provides that projection.

It is not new core business logic.
It is the stabilization of the product read boundary.