# EPIC 8 - Export & External Integration Layer (Architecture)

---

## 1. Objective

Provide a deterministic, API-first export capability for finalized reconciliation runs.

The system must allow consumers to retrieve a clean, reliable, and structured output from a completed run that has passed review.

This EPIC transforms InvoMatch from an internal processing engine into a usable product output layer.

---

## 2. User-Visible Outcome

A user, operator, or external system can:

- select a completed run
- export its finalized results
- receive output in:
  - JSON (canonical)
  - CSV (practical)

The output must be:

- deterministic
- complete
- review-approved
- directly usable outside the system

---

## 3. Placement in Product Flow

INGEST -> MATCH -> REVIEW -> EXPORT -> EXTERNAL SYSTEM

Export is only available after:

- run is COMPLETED
- review is finalized

---

## 4. Scope

### Included

- export schema v1
- export service
- JSON export
- CSV export
- export API endpoint
- deterministic output
- validation of export eligibility

### Explicitly Excluded

- ERP integrations (SAP, Fortnox, QuickBooks, etc.)
- webhooks
- export scheduling
- async jobs
- export history
- PDF, XML, XLSX, or other extra formats
- export dashboards or reporting UI
- external delivery adapters

---

## 5. Architectural Boundaries

The export layer:

- does NOT modify system state
- does NOT perform matching
- does NOT perform review workflow logic
- does NOT access intermediate or candidate states
- does NOT introduce external integration logic in v1

The export layer ONLY:

- reads finalized product state
- transforms finalized state into export format
- exposes export through the API

---

## 6. Core Design Principles

- Deterministic: same finalized run -> same logical output
- Explainable: every exported result must be traceable
- Minimal: no unnecessary internal fields
- System-agnostic: no ERP-specific coupling
- Immutable snapshot: export is a snapshot, not a live view
- Product-aligned: export must directly support the run-centered flow

---

## 7. Core Data Model

### FinalizedResult (read model)

FinalizedResult represents the final, exportable truth of a reconciliation decision.

It includes:

- invoice reference data
- payment references (one or many)
- final decision type
- match metadata
- review outcome

This model MUST be:

- complete
- self-contained
- export-ready
- independent of candidate-level internal logic

FinalizedResult is the single source of truth for export assembly.

### ExportBundle

ExportBundle is the top-level export structure.

It includes:

- schema_version
- run_id
- status
- exported_at
- currency
- summary
- results

---

## 8. Data Access Strategy

ExportService MUST NOT manually assemble raw data from multiple unrelated sources.

Instead, it depends on a finalized read contract:

FinalizedResultReader

Contract:

get_results_for_run(run_id) -> list[FinalizedResult]

Responsibilities of the reader:

- return ONLY finalized results
- ensure data completeness
- enforce integrity constraints for finalized export data
- avoid leaking candidate or intermediate states

---

## 9. Export Service Responsibilities

ExportService is an orchestration layer.

It must:

1. load the run
2. validate export eligibility
3. retrieve finalized results
4. build ExportBundle through a mapper
5. select the serializer
6. return ExportOutput

It must NOT:

- perform joins across repositories directly
- implement matching logic
- implement review logic
- mutate system state
- embed serializer-specific business logic

---

## 10. Export Formats

### JSON (canonical)

JSON is the source of truth for export.

It must provide:

- complete structure
- stable schema
- deterministic field presence
- traceable final results

### CSV (derived)

CSV is a flattened practical export derived from the same canonical export bundle.

CSV must be:

- human-readable
- stable in column order
- derived from the canonical bundle
- free from separate business logic paths

CSV MUST NOT introduce independent export rules.

---

## 11. API Contract

### Endpoint

GET /runs/{run_id}/export

### Query Parameter

format=json|csv

Default format: json

### Success Responses

- 200 OK with application/json for JSON export
- 200 OK with text/csv for CSV export

### Error Responses

- 404 NOT_FOUND -> RUN_NOT_FOUND
- 400 BAD_REQUEST -> UNSUPPORTED_EXPORT_FORMAT
- 409 CONFLICT -> RUN_NOT_EXPORTABLE
- 422 UNPROCESSABLE_ENTITY -> EXPORT_DATA_INCOMPLETE

The endpoint is read-only and must not mutate run state.

---

## 12. Eligibility Rules

Export is allowed ONLY if all of the following are true:

- run.status == COMPLETED
- review state is finalized
- finalized results exist
- finalized results are internally valid
- no required export data is missing
- no currency or integrity conflict exists in finalized export data

If any of the above is false, export must be rejected.

---

## 13. Determinism Rules

To keep export stable and predictable:

- results must be sorted by invoice_date, then invoice_id
- payments inside each result must be sorted by payment_date, then payment_id
- schema fields must remain stable
- JSON structure must remain stable
- CSV column order must remain stable
- summary must be derived from the finalized result set

---

## 14. Error Model

The export layer uses explicit errors.

Minimum required errors:

- RunNotFoundError
- RunNotExportableError
- UnsupportedExportFormatError
- ExportDataIncompleteError
- FinalizedResultIntegrityError

Errors must be specific enough to map cleanly into API responses.

---

## 15. File Structure

Expected file structure for EPIC 8:

domain/export/models.py

services/export/
  errors.py
  finalized_result_reader.py
  mapper.py
  export_service.py
  serializers/
    json_exporter.py
    csv_exporter.py

api/routes/export_routes.py

tests/export/
tests/api/

docs/architecture/EPIC_8_EXPORT_ARCHITECTURE.md

---

## 16. Implementation Order

1. architecture document
2. export models
3. error model
4. FinalizedResultReader contract
5. mapper
6. JSON serializer
7. CSV serializer
8. ExportService
9. API route
10. tests
11. closure

This order is intentional and should not be reversed.

---

## 17. Minimum Shippable Scope

The minimum shippable scope for EPIC 8 is:

- export a single run
- support JSON and CSV only
- allow export only for finalized runs
- provide a synchronous API endpoint
- avoid all external integrations in v1

Anything beyond this is out of scope unless explicitly approved.

---

## 18. Risks of Overbuilding

The main risks in this EPIC are:

- adding integration layers too early
- introducing async export pipelines
- adding too many formats
- building export configuration engines too early
- mixing export concerns with review or matching logic
- creating export resources or history systems before they are needed

These are explicitly avoided in EPIC 8.

---

## 19. Definition of Done

EPIC 8 is complete when:

- a finalized run can be exported successfully
- JSON output is stable and correct
- CSV output is usable and consistent
- non-finalized runs are rejected
- export is deterministic and read-only
- tests validate contract, ordering, and error behavior
- the implementation remains aligned with the run-centered product flow

---

## 20. Final Principle

Export must remain:

simple, predictable, trustworthy, and product-aligned

No complexity is allowed unless it directly improves:

INGEST -> MATCH -> REVIEW -> EXPORT