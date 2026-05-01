# EPIC 30 - Projection Integrity Enforcement and Completion-Time Guarantee

## Status

Closed.

EPIC 30 enforces a hard product invariant:

A reconciliation run must not become product-completed unless its finalized projection has already been created, persisted, and read back successfully.

This EPIC closes the gap left after EPIC 29.

EPIC 29 made completed product reads fail safely when finalized projection was missing. That was necessary, but it was still a read-side protection. EPIC 30 moves the guarantee earlier into the write/finalization path so the invalid state is prevented at completion time.

## Background

InvoMatch has been moving toward a projection-backed product model.

The intended production model is:

- completed product views must read from finalized projection,
- exports must read from finalized projection,
- completed runs must be immutable from the product perspective,
- finalized projection must be tenant-bound,
- finalized projection must be audit-safe,
- legacy report fallback must not be used for completed product views.

Before EPIC 30, the system already had stricter read behavior. A completed run without finalized projection failed hard in the product read layer and export path.

However, completion itself was still too weak.

Projection creation was called after the run had already been persisted as completed. That meant the system could temporarily or permanently create an invalid state:

completed run exists, but finalized projection is missing or unreadable.

For a production SaaS system, that is not acceptable.

## Problem Statement

The previous flow allowed this unsafe sequence:

1. run is evaluated as finalizable,
2. run is persisted as completed,
3. finalized projection creation is attempted afterward,
4. projection persistence or readback may fail,
5. system is left with a completed run that has no usable finalized projection.

This made product correctness dependent on later read-side failure handling.

That is not enough.

A completed run is a product-visible terminal state. Therefore, the finalized projection must be guaranteed before the completed state is written.

## Goal

Ensure a run cannot become product-completed unless finalized projection has been:

1. created,
2. persisted,
3. read back,
4. verified as non-empty,
5. tenant-bound,
6. and available to product/export readers.

## Non-Goals

EPIC 30 does not attempt to solve:

- projection schema redesign,
- projection indexing,
- projection performance optimization,
- projection caching,
- database-level distributed transactions,
- cross-store atomic transaction management,
- advanced projection version migration.

The goal is completion-time integrity enforcement at the service layer.

## Final Invariant

A run cannot be persisted as completed unless all of the following are true:

1. A finalized projection store is available.
2. Finalized projection persistence succeeds.
3. Finalized projection can be read back immediately after persistence.
4. Readback returns finalized results.
5. Only after successful readback is the run state persisted as completed.

If any of those steps fail, the run remains in its previous non-completed state.

Expected failure states:

- post-matching completion failure leaves run in processing,
- post-review-resolution completion failure leaves run in review_required,
- direct reconciliation completion failure leaves run in processing.

## Design Decision

The implementation uses a candidate completed run model.

Instead of immediately persisting status=completed, completion flows now:

1. build the next run state in memory,
2. treat that model as the completed candidate,
3. create/persist finalized projection from the completed candidate,
4. read the projection back,
5. only then persist the completed run state.

This avoids relying on rollback from completed.

Rollback would be unsafe because completed is terminal in the lifecycle model. The lifecycle does not allow completed to move back to processing, review_required, or failed.

Therefore, the correct design is:

validate projection before persisting terminal completion.

## Production Code Changes

### 1. CompletedRunProjectionService

Updated file:

- src/invomatch/services/completed_run_projection_service.py

Added:

- CompletedRunProjectionIntegrityError
- ensure_for_completed_run(run)

New behavior:

- persist_if_completed(run) still returns immediately for non-completed runs.
- For completed runs, persist_if_completed(run) now delegates to ensure_for_completed_run(run).
- ensure_for_completed_run(run) raises if the run is not completed.
- ensure_for_completed_run(run) raises if projection_store is missing.
- ensure_for_completed_run(run) persists finalized projection through FinalizedProjectionWriter.
- ensure_for_completed_run(run) immediately reads the projection back.
- ensure_for_completed_run(run) raises if readback returns no finalized results.

This converts projection persistence from a best-effort side effect into a required completion invariant.

### 2. Reconciliation Run Update Builder

Updated file:

- src/invomatch/services/reconciliation_runs.py

Added:

- build_reconciliation_run_update(...)

Purpose:

- build the next ReconciliationRun state without persisting it.

Before EPIC 30:

- update_reconciliation_run(...) validated transition,
- built the updated run,
- immediately persisted it.

After EPIC 30:

- build_reconciliation_run_update(...) validates transition and builds the updated run model.
- update_reconciliation_run(...) delegates to the builder and then persists the model.

This allows completion flows to build a completed candidate, enforce projection integrity, and only then persist the completed state.

### 3. Direct Reconciliation Completion Path

Updated file:

- src/invomatch/services/reconciliation.py

Changed function:

- reconcile_and_save(...)

New completion flow:

1. Reconciliation executes.
2. Match records are persisted.
3. Final status is calculated.
4. A candidate run update is built.
5. If candidate status is completed, projection integrity is enforced.
6. Only after successful projection persistence and readback is the candidate persisted.

Failure behavior:

- projection store missing blocks completion,
- projection save failure blocks completion,
- projection readback failure blocks completion,
- run remains processing,
- report is not persisted into a false completed state.

### 4. Orchestration Completion Path

Updated file:

- src/invomatch/services/orchestration/run_orchestration_service.py

Changed functions:

- orchestrate_and_persist_post_matching(...)
- orchestrate_and_persist_post_review_resolution(...)

New post-matching completion flow:

1. Orchestration evaluates whether review is required.
2. If run is finalizable, a completed candidate is built.
3. Finalized projection integrity is enforced.
4. Only after successful projection persistence and readback is completed persisted.

New post-review-resolution completion flow:

1. Active review cases are checked.
2. If no blockers remain and matching is complete, a completed candidate is built.
3. Finalized projection integrity is enforced.
4. Only after successful projection persistence and readback is completed persisted.

Failure behavior:

- post-matching projection failure leaves run in processing,
- post-review-resolution projection failure leaves run in review_required,
- missing projection store blocks completion.

## Test Changes

### 1. Orchestration Persistence Tests

Updated file:

- tests/test_run_orchestration_persistence.py

Added coverage for:

- completed post-matching requires projection store,
- completed post-review-resolution requires projection store,
- post-matching completion is blocked when projection persistence fails,
- post-matching completion is blocked when projection readback fails,
- post-review-resolution completion is blocked when projection persistence fails,
- post-review-resolution completion is blocked when projection readback fails,
- run status remains non-completed after projection failure.

Important state guarantees tested:

- failed post-matching projection leaves run as processing,
- failed post-review-resolution projection leaves run as review_required.

### 2. Direct Reconciliation Tests

Updated file:

- tests/test_reconciliation_service.py

Added coverage for:

- reconcile_and_save does not persist completed when projection save fails,
- reconcile_and_save does not persist completed when projection readback fails,
- successful completed reconciliation has readable finalized projection.

Important state guarantees tested:

- failed projection save leaves run as processing,
- failed projection readback leaves run as processing,
- false completed state is not persisted.

### 3. Export API Test Fixtures

Updated file:

- tests/test_export_api.py

Reason:

- export tests create completed runs.
- completed runs now require finalized projection at creation time.

Changes:

- completed-run helper now accepts/provides a finalized projection store,
- test app projection store is passed into helper where needed,
- export tests remain projection-backed.

### 4. Export Artifact API Test Fixtures

Updated file:

- tests/test_export_artifact_api.py

Reason:

- artifact tests create completed runs.
- completed runs now require finalized projection at creation time.

Changes:

- completed-run helper now creates a SqliteFinalizedProjectionStore,
- reconcile_and_save receives the projection store,
- completed fixture creation now satisfies EPIC 30 invariant.

### 5. Resolve Review Action Test Wiring

Updated file:

- tests/test_actions/test_resolve_review.py

Reason:

- resolve-review action test completes a run through persisted orchestration path.
- that path now requires projection availability.

Changes:

- test uses explicit readable fake projection store where projection creation is not the subject of the test.

### 6. System Happy Path Test Wiring

Updated file:

- tests/system/test_happy_path_full_flow.py

Reason:

- completed RunView is projection-only.
- RunViewQueryService must receive the same projection store used by completion/export readiness.

Changes:

- RunViewQueryService is wired with projection_store.

### 7. System Review Resolution Flow Test Wiring

Updated file:

- tests/system/test_review_resolution_flow.py

Reason:

- review resolution completes a run.
- completed RunView is projection-only.

Changes:

- RunViewQueryService is wired with projection_store.

### 8. Restart Recovery Consistency Test Wiring

Updated file:

- tests/system/test_restart_recovery_consistency.py

Reason:

- restart repair can move a run from review_required to completed.
- completed state now requires projection availability.
- completed RunView also requires projection store.

Changes:

- restart repair completion path receives readable fake projection store,
- RunViewQueryService receives readable fake projection store.

## Validation Evidence

### Compile Check

Command executed:

cd C:\dev\InvoMatch
$env:PYTHONPATH = "src"
py -m compileall src tests -q

Result:

passed

### Focused Export and Restart Pack

Command executed:

pytest -q tests\test_export_api.py tests\test_export_artifact_api.py tests\system\test_restart_recovery_consistency.py --basetemp=.pytest_tmp

Result:

18 passed in 7.73s

### EPIC 30 Regression Pack

Command executed:

pytest -q tests\test_run_orchestration_persistence.py tests\test_finalized_projection_lifecycle.py tests\test_reconciliation_service.py tests\test_export_readiness_evaluator.py tests\test_run_view_query_service.py tests\test_projection_invariant.py tests\test_run_view_contract.py tests\test_export_api.py tests\test_export_artifact_api.py tests\test_actions\test_export_run.py tests\test_actions\test_resolve_review.py tests\system\test_happy_path_full_flow.py tests\system\test_review_resolution_flow.py tests\system\test_restart_recovery_consistency.py --basetemp=.pytest_tmp

Result:

84 passed in 9.59s

## Files Changed

### Production Code

- src/invomatch/services/completed_run_projection_service.py
- src/invomatch/services/orchestration/run_orchestration_service.py
- src/invomatch/services/reconciliation.py
- src/invomatch/services/reconciliation_runs.py

### Tests

- tests/test_run_orchestration_persistence.py
- tests/test_reconciliation_service.py
- tests/test_export_api.py
- tests/test_export_artifact_api.py
- tests/test_actions/test_resolve_review.py
- tests/system/test_happy_path_full_flow.py
- tests/system/test_review_resolution_flow.py
- tests/system/test_restart_recovery_consistency.py

### Documentation

- docs/architecture/EPIC_30_CLOSURE.md

## Risk Assessment

### Risk: service-level guarantee is not database-atomic

The run store and projection store are separate persistence concerns. EPIC 30 does not introduce a shared database transaction across both stores.

Mitigation:

- completed state is not persisted until projection persistence and readback succeed,
- no known completion path writes completed before projection verification,
- read-side completed projection checks remain strict from EPIC 29.

### Risk: tests using completed fixtures must now provide projection

This is expected and correct.

A completed run without projection is no longer a valid fixture unless the test explicitly validates inconsistent-state failure behavior.

### Risk: fake projection stores in tests may hide projection creation behavior

Fake readable projection stores are only used in tests whose subject is not projection creation, such as action dispatch or restart repair behavior.

Projection creation and readback are covered separately by:

- tests/test_run_orchestration_persistence.py
- tests/test_reconciliation_service.py
- tests/test_finalized_projection_lifecycle.py

## Final Outcome

EPIC 30 is complete.

The system now enforces completion-time projection integrity:

- completed runs require finalized projection store,
- finalized projection must persist successfully,
- finalized projection must be readable immediately,
- failed projection creation/readback prevents completed persistence,
- product/export/read paths remain projection-backed.

A run can no longer silently become product-completed without a persisted and readable finalized projection.