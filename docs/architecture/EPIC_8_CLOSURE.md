# EPIC 8 - Export System (CLOSURE)

## 1. Objective

Establish a product-aligned export system for InvoMatch that is:

- deterministic
- explainable
- API-first
- run-centered
- independent from legacy file-centric export workflow design

This EPIC replaces placeholder export behavior with a real export pipeline built around finalized results.

---

## 2. What Was Wrong Before

Before EPIC 8:

- export behavior was placeholder-oriented at API level
- action export depended on file-centric workflow logic
- export logic was not grounded in finalized review-aware truth
- legacy export implementation introduced an artifact-first model instead of a product-first model
- product contract and export behavior were not aligned

This meant the system could expose "export" behavior without a trustworthy finalized export model.

---

## 3. What Was Built

### 3.1 Export Domain Contract

Introduced export-specific domain models under:

- `src/invomatch/domain/export/`

Key models:
- `ExportFormat`
- `FinalDecisionType`
- `FinalizedInvoiceRef`
- `FinalizedPaymentRef`
- `FinalizedMatchMeta`
- `FinalizedReviewMeta`
- `FinalizedResult`
- `ExportSummary`
- `ExportBundle`
- `ExportOutput`

---

### 3.2 Export Service Layer

Introduced export service structure under:

- `src/invomatch/services/export/`

Key components:
- `errors.py`
- `mapper.py`
- `source_loader.py`
- `finalized_projection.py`
- `run_finalized_result_reader.py`
- `serializers/json_exporter.py`
- `serializers/csv_exporter.py`
- `export_service.py`

Also retained:
- `finalized_result_reader.py` as protocol/interface contract

---

### 3.3 Finalized Projection Contract

Defined finalized export truth formally in:

- `docs/architecture/EPIC_8_FINALIZED_PROJECTION.md`

This contract established:
- review-aware export eligibility
- source reconstruction rules
- decision resolution rules
- deterministic ordering rules
- export integrity constraints

---

### 3.4 Source Data Gap Discovery and Resolution

A real schema gap was identified during implementation:

- export required currency
- ingestion/source contract did not reliably guarantee currency

This was captured in:

- `docs/architecture/EPIC_8_SOURCE_DATA_GAP.md`

Resolution:
- source schema and ingestion were updated to require `currency`
- export contract was not weakened

This preserved financial correctness.

---

### 3.5 API Export Path

API export was rebuilt around the new product-aligned export path:

- `src/invomatch/api/export.py`

Behavior now:
- validates requested format
- uses configured `ExportService`
- returns real JSON/CSV export output
- maps export errors to HTTP responses

Placeholder export response behavior was removed.

---

### 3.6 Action Export Path

Action-based export was migrated to the new export system.

Updated:
- `src/invomatch/services/actions/handlers/export_run.py`
- `src/invomatch/services/action_service.py`

Action export is now aligned with:
- `ExportService`
- finalized result projection
- product-level metadata response

---

## 4. Removed Legacy Components

The following legacy export components were removed:

- `src/invomatch/services/export/export_workflow.py`
- `src/invomatch/services/export/export_writer.py`

Reason:
- they enforced a file-centric export model
- they bypassed finalized export truth
- they created a parallel export path
- they were no longer aligned with product architecture

---

## 5. Architectural Outcome

EPIC 8 now provides a single coherent export path:

API / Action
-> ExportService
-> RunFinalizedResultReader
-> FinalizedResultProjection
-> ExportMapper
-> JSON / CSV Serializer

This is now the authoritative export flow.

---

## 6. Tests and Verification

Validated during implementation with focused export tests:

- export API tests
- export action tests

Verified outcomes:
- missing run handling
- non-exportable run handling
- incomplete review/export data handling
- JSON export generation
- CSV export generation
- action export metadata behavior

---

## 7. Important Design Decisions

### 7.1 Export is not file generation
Export is a product-facing representation of finalized truth.

### 7.2 Review-finalized state is required
Export must not guess or bypass unresolved review state.

### 7.3 Source data contract must remain strong
Financial correctness was prioritized over shortcut implementation.

### 7.4 Legacy parallel export paths were removed
Only one export path should remain in the system.

---

## 8. Remaining Follow-ups

EPIC 8 is functionally complete, but some hardening/follow-up work remains:

- reintroduce export contract hardening tests suited to the new export behavior
- decide whether a separate download/delivery layer is needed in a future EPIC
- evaluate whether additional end-to-end coverage should be added for export with sqlite-backed review storage
- review whether `ProductExportModel` should now be removed if no longer used elsewhere

---

## 9. Final Status

EPIC 8 status:

- architecture: complete
- implementation: complete
- legacy export path removal: complete
- focused export tests: passing
- hardening: partial follow-up remains

---

## 10. Conclusion

EPIC 8 successfully moved export in InvoMatch from a placeholder / artifact-centric behavior to a real SaaS-grade export architecture based on finalized, review-aware, deterministic truth.

This EPIC is now a valid foundation for future:
- delivery/download orchestration
- external integrations
- reporting pipelines
- audit-safe export extensions
