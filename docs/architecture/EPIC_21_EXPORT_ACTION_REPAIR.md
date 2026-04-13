# EPIC 21 — Export Action / Export Readiness Repair

## Status
Integration repair discovered and resolved during EPIC 21 minimal operator UI implementation.

---

## 1. Defect Summary

During EPIC 21 UI implementation, the minimal action surface began calling:

- POST /api/reconciliation/runs/{run_id}/actions

using:

- `action_type = export_run`
- `payload.format = json`

Two backend defects were discovered during this real UI-driven action execution.

### Defect A
The `export_run` action path raised an unhandled exception and returned HTTP 500.

### Defect B
The run view export summary reported:

- `export_summary.status = ready`

for runs that were not actually exportable due to missing finalized review data.

This created truth inconsistency between:

- action execution behavior
- run detail export status visibility

---

## 2. Root Cause

### 2.1 Unhandled Export Failure
The export action path reached finalized export generation and failed with:

- `ExportDataIncompleteError: no finalized review data found for run`

This exception was not converted into a product-facing action response, causing HTTP 500.

### 2.2 Run View Readiness Drift
`RunViewQueryService` supports `export_readiness_evaluator`, but the route wiring did not pass the evaluator into the query service.

As a result, run view export summary fell back to simplified readiness logic:

- run status is completed
- review summary open items is zero

That fallback incorrectly reported `ready` even when finalized export data was unavailable.

---

## 3. Repair Applied

### 3.1 Action Error Handling Repair
`ActionService` was updated to catch:

- `ExportDataIncompleteError`
- `RunNotExportableError`

and convert them into controlled product-facing action responses with:

- `accepted = false`
- `status = conflict`
- meaningful message text

This removed the HTTP 500 behavior.

### 3.2 Export Readiness Evaluation Repair
`ExportReadinessEvaluator` was strengthened to validate finalized exportability by calling:

- `RunFinalizedResultReader.read(run_id=...)`

If finalized export data is unavailable, readiness now returns:

- `is_export_ready = false`

with a reason derived from finalized export availability.

### 3.3 Run View Wiring Repair
`api/reconciliation_runs.py` was updated so `RunViewQueryService` receives:

- `export_readiness_evaluator=request.app.state.export_readiness_evaluator`

This removed readiness drift in the run detail view.

---

## 4. Validation Evidence

### Before Repair
- export action with valid payload returned HTTP 500
- run detail export summary incorrectly showed `ready`

### After Repair
- export action returns controlled conflict response:
  - `accepted = false`
  - `status = conflict`
  - `message = no finalized review data found for run`
- run detail export summary now shows:
  - `status = not_ready`

### UI Result
The EPIC 21 Run Detail action surface now truthfully displays export action failure without crashing the UI.

---

## 5. Scope Impact

This repair was required for EPIC 21 because the minimal operator UI must expose:

- action execution
- export visibility
- truthful backend state

Without this repair, the UI would either:
- crash on action execution, or
- display misleading export readiness state

---

## 6. Final Note

This repair materially improves EPIC 21 product truthfulness and action safety.

The system now exposes:

- controlled action outcomes
- truthful export readiness visibility
- no silent crash path for export action execution
