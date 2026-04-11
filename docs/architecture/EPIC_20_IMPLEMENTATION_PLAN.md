# EPIC 20 - External Input Boundary Implementation Plan

---

## 1. Goal

Implement a safe, deterministic, and traceable external input boundary for InvoMatch.

This plan is execution-oriented and defines the delivery order.

---

## 2. Delivery Strategy

EPIC 20 must be implemented from boundary inward:

1. define product-facing contracts
2. define input session domain and repository
3. implement JSON path
4. implement file path
5. wire ingestion and run integration
6. validate traceability and failure behavior

This prevents uncontrolled coupling and preserves ingestion as the canonical intake boundary.

---

## 3. Work Breakdown

### Stage 1 - Domain and Contract Foundations

Deliver:

- InputSession domain model
- InputError model
- InputSessionStatus enum
- product-facing API models
- repository interface

Files likely needed:

- src/invomatch/domain/input_boundary/models.py
- src/invomatch/services/input_boundary/repository.py
- src/invomatch/api/product_models/input_boundary.py

Done when:

- models are stable
- repository boundary is explicit
- product response shapes are defined

### Stage 2 - JSON Input Path

Deliver:

- JsonInputService
- JSON request validation
- JSON submission API
- integration with ingestion and run creation

Files likely needed:

- src/invomatch/services/input_boundary/json_input_service.py
- src/invomatch/services/input_boundary/input_processing_service.py
- src/invomatch/api/routes/input_boundary.py

Done when:

- structured JSON can create input session
- validated JSON can enter ingestion
- run can be created deterministically
- failures are structured

### Stage 3 - File Intake Pipeline

Deliver:

- FileValidator
- FileDecoder
- CsvInputParser
- CsvInputMapper
- FileInputService

Files likely needed:

- src/invomatch/services/input_boundary/file_validator.py
- src/invomatch/services/input_boundary/file_decoder.py
- src/invomatch/services/input_boundary/csv_input_parser.py
- src/invomatch/services/input_boundary/csv_input_mapper.py
- src/invomatch/services/input_boundary/file_input_service.py

Done when:

- CSV files are validated
- malformed files fail safely
- rows map deterministically into canonical ingestion input

### Stage 4 - File API Exposure

Deliver:

- file submission endpoint
- multipart handling
- response mapping
- traceability linking

Done when:

- file upload API works
- file -> ingestion -> run flow is operational
- no direct bypass is possible

### Stage 5 - Input Session Query and Traceability

Deliver:

- input session lookup endpoint
- repository-backed traceability
- product session view model

Done when:

- input_id can be queried
- ingestion_batch_id and run_id can be traced
- failure states remain inspectable

### Stage 6 - Hardening and Test Closure

Deliver:

- contract tests
- API tests
- integration tests
- failure propagation tests
- closure document

Done when:

- deterministic behavior is test-proven
- no internal leakage exists
- closure evidence is repo-backed

---

## 4. Required Architectural Constraints

- no direct external payload to run integration
- no raw file bypass into ingestion
- all file flows must normalize into canonical ingestion objects
- all failures must be explicit and structured
- all successful flows must preserve traceability
- all routes must return product-facing models only

---

## 5. Initial File and Directory Targets

```text
src/invomatch/domain/input_boundary/
src/invomatch/services/input_boundary/
src/invomatch/api/routes/input_boundary.py
src/invomatch/api/product_models/input_boundary.py
tests/input_boundary/
tests/contracts/test_product_contract_input_boundary.py
tests/test_input_boundary_api.py
docs/architecture/EPIC_20_CLOSURE.md
```

---

## 6. Risk Areas

### Risk 1 - Direct Run Creation Bypass
Mitigation:
- all external flows must go through InputProcessingService
- service owns ingestion and run creation orchestration

### Risk 2 - Loose CSV Parsing
Mitigation:
- strict parser
- required headers
- no inferred mapping

### Risk 3 - Broken Traceability
Mitigation:
- InputSession created first
- ingestion_batch_id and run_id stored explicitly

### Risk 4 - Unclear Errors
Mitigation:
- stable ProductInputError schema
- typed failure branches

---

## 7. Closure Evidence Expected

EPIC 20 cannot be marked done without:

- architecture document
- design document
- implementation plan
- implementation merged into repo
- targeted tests green
- closure file written from actual repo state

---

## 8. Execution Rule

Implement the JSON path first.

Reason:
- lower ambiguity
- validates orchestration shape
- stabilizes response contract before file complexity is added

Only after JSON path is stable should the CSV path be implemented.