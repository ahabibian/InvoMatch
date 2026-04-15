# System Scenario 1 - Gap Notes and Resolution

## Context

System Scenario 1 (happy path full flow) was implemented as a real isolated system test under:

- `tests/system/test_happy_path_full_flow.py`

The scenario validates:

- valid JSON input submission
- input boundary validation and normalization
- ingestion batch assignment
- ingestion -> run integration
- runtime execution through `IngestionRunRuntimeAdapter`
- persisted run creation
- terminal run completion (`status=completed`)
- no review items created for the happy path
- export readiness for no-review completed runs
- explicit export artifact generation
- artifact query consistency
- unified run view consistency

---

## Original Gap

The first implementation exposed a real system gap:

- run completion succeeded
- export readiness stayed false
- reason:
  - `finalized_export_data_unavailable:no finalized review data found for run`

This showed that the export pipeline incorrectly required finalized review data even for no-review happy-path runs.

---

## Root Cause

The issue was in:

- `src/invomatch/services/export/finalized_projection.py`

The finalized projection required every exportable result to have a finalized review item.

That assumption was incorrect for no-review happy-path runs.

For completed runs where reconciliation ended in terminal non-review statuses such as:

- `matched`
- `unmatched`

the export layer should be able to derive finalized results directly without requiring review resolution data.

---

## Resolution

The export projection was updated so that:

- no-review `matched` results are exportable
- no-review `unmatched` results are exportable
- no-review `partial_match` results remain non-exportable until review is finalized
- no-review `duplicate_detected` results remain non-exportable until review is finalized

The export domain model was extended with:

- `FinalizedReviewStatus.NOT_REQUIRED`

This allows the finalized export contract to represent cases where no human review was needed.

---

## Current Status

System Scenario 1 is now fully green for the intended happy path.

This means the current system is coherent across:

- input boundary
- ingestion
- run creation
- runtime execution
- run completion
- finalized export projection for no-review runs
- export readiness
- artifact generation
- artifact query
- run view consistency

---

## Follow-up Hardening Required

The system scenario exposed and validated the architecture fix, but this behavior should also be protected with focused tests at the export projection level.

Recommended next tests:

1. no-review `matched` result is exportable
2. no-review `unmatched` result is exportable
3. no-review `partial_match` remains non-exportable
4. no-review `duplicate_detected` remains non-exportable

These tests should be added close to `FinalizedResultProjection`.