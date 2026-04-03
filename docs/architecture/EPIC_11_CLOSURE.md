# EPIC 11 CLOSURE

Status: Closed
EPIC: 11
Title: Unified Run View Read Model

## 1. Objective

EPIC 11 introduced a unified, run-centric product read model for InvoMatch.

The objective was to replace fragmented product-facing read behavior across multiple surfaces with a single, contract-driven run view that aggregates:
- run lifecycle state
- match summary
- review summary
- export summary
- artifact availability

The resulting endpoint is intended to become the primary single-run read surface for UI and future product consumers.

---

## 2. Problem Addressed

Before EPIC 11, product-facing read behavior for a run was fragmented across separate routes and subsystem-specific surfaces.

This created several product architecture issues:
- no single canonical run view
- duplicated client-side interpretation logic
- inconsistent read composition across consumers
- avoidable coupling between UI and backend internals

EPIC 11 closed that gap by introducing a unified read projection.

---

## 3. Deliverables Completed

The following deliverables were completed:

### Architecture and Contract
- RUN_VIEW_ARCHITECTURE.md
- RUN_VIEW_API_CONTRACT.md
- EPIC_11_CLOSURE.md

### Product Models
- ProductRunView
- ProductRunMatchSummary
- ProductRunReviewSummary
- ProductRunExportSummary
- ProductRunArtifactReference

### Services
- RunViewQueryService

### API Surface
- GET /api/reconciliation/runs/{run_id}/view

### Tests
- test_run_view_query_service.py
- test_run_view_api.py
- test_run_view_contract.py

Additional related validation was also executed across export and artifact test coverage to verify compatibility with the new run view surface.

---

## 4. Implemented Read Model

The unified ProductRunView now returns the following top-level shape:
- run_id
- status
- created_at
- updated_at
- match_summary
- review_summary
- export_summary
- artifacts

This shape is stable, explicit, and product-facing.

It does not expose raw domain objects or infrastructure-level storage details.

---

## 5. Implemented Aggregation Behavior

RunViewQueryService now composes the run view from existing subsystem boundaries:

- run lifecycle data from run registry / run store access
- review summary from review-store-backed aggregation
- artifact references from artifact query service
- export summary from run lifecycle plus artifact availability

The service is read-only and does not mutate state.

---

## 6. Review Summary Behavior

Review summary is now based on aggregation across all review items associated with the run, not just a single review case.

Current summary rules:
- no review items -> status = not_started
- any open review items -> status = in_review
- all review items resolved -> status = completed

Current open item statuses:
- PENDING
- IN_REVIEW
- DEFERRED

Current resolved item statuses:
- APPROVED
- REJECTED
- MODIFIED
- CLOSED

This behavior is now test-covered.

---

## 7. Export and Artifact Behavior

Export summary is intentionally product-facing and does not leak storage implementation details.

Current rules:
- non-completed runs -> export_summary.status = not_ready
- completed run with no artifacts -> export_summary.status = ready
- completed run with artifacts -> export_summary.status = exported

Artifact references are returned as lightweight product-safe objects only.

Artifacts are sorted deterministically by:
1. created_at ascending
2. artifact_id ascending

---

## 8. Contract Enforcement

EPIC 11 added explicit contract boundary tests to verify that the run view does not leak internal fields.

Validated non-leakage examples include:
- storage_key
- expires_at
- source_reference
- reviewed_payload
- internal raw flags or internal-only payload fields

Artifact shape is also enforced as a lightweight product-safe contract rather than a raw artifact domain object.

---

## 9. Validation Performed

The EPIC-specific test suite passed:
- run view query service tests
- run view API tests
- run view contract tests

A broader related validation pass also succeeded across export and artifact behavior.

Latest validation snapshot during closure:
- 50 passed

This gives sufficient confidence that the run view integrates correctly with the existing export/artifact product surface.

---

## 10. Files Added or Updated

Primary files added or updated during EPIC 11 include:

### Documentation
- docs/architecture/RUN_VIEW_ARCHITECTURE.md
- docs/architecture/RUN_VIEW_API_CONTRACT.md
- docs/architecture/EPIC_11_CLOSURE.md

### Product/API
- src/invomatch/api/product_models/run_view.py
- src/invomatch/api/reconciliation_runs.py

### Services
- src/invomatch/services/run_view_query_service.py

### Tests
- tests/test_run_view_query_service.py
- tests/test_run_view_api.py
- tests/test_run_view_contract.py

---

## 11. Known Limitations

EPIC 11 is complete, but the following limitations remain intentionally documented:

### 11.1 Review Summary Status Compression
The review_summary contract currently uses a simplified practical status interpretation:
- not_started
- in_review
- completed

The broader contract enum space is not yet fully exercised by current subsystem semantics.

### 11.2 Minimal Match Summary
match_summary remains intentionally lightweight and depends on the currently available run report shape.

### 11.3 No Performance Layer
This EPIC did not introduce caching, read-side materialization, or performance optimization.

### 11.4 No Expanded Review Analytics
The run view does not yet expose richer review analytics such as reason-code buckets, reviewer-level metadata, or multi-case drilldown summaries.

These are future enhancements, not closure blockers for EPIC 11.

---

## 12. Architectural Outcome

EPIC 11 successfully established a unified, deterministic, product-facing run read surface.

This is an important product architecture milestone because it shifts run consumption away from fragmented endpoint reconstruction and toward a single canonical read model.

The backend now owns run-state composition instead of forcing the UI to reconstruct it.

---

## 13. Exit Criteria Review

Exit criteria defined for EPIC 11 are satisfied:

- a single endpoint returns a complete run view -> satisfied
- UI can rely on this endpoint as primary single-run read surface -> satisfied
- no domain leakage -> satisfied by contract tests
- deterministic and test-covered behavior -> satisfied
- consistent product contract -> satisfied

---

## 14. Closure Decision

EPIC 11 is closed.

The implemented Run View is production-meaningful, contract-driven, and sufficiently validated for the current architecture stage.

Future improvements should build on this read surface rather than bypass it.
