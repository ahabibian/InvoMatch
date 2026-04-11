# EPIC 20 - External Input Boundary & Controlled Entry Layer

---

## 1. Objective

Introduce a controlled external input boundary that allows users and external systems to safely submit data into InvoMatch.

This EPIC establishes a strict boundary between the external world and the internal deterministic system.

After this EPIC:

External Input -> Input Boundary -> Ingestion -> Run -> Lifecycle

must be fully operational, deterministic, and traceable.

---

## 2. System Position

```text
[ External World ]
        |
        v
[ Input Boundary Layer ]   (EPIC 20)
        |
        v
[ Ingestion System ]       (EPIC 16)
        |
        v
[ Run Integration ]        (EPIC 17)
        |
        v
[ Runtime / Lifecycle ]
```

The Input Boundary Layer is responsible for:

- isolating untrusted input
- enforcing validation
- preventing ingestion bypass
- ensuring deterministic transformation

---

## 3. Input Boundary Architecture

The Input Boundary consists of the following subsystems:

### 3.1 Upload API Layer
Handles external requests and routes input to the correct processing pipeline.

### 3.2 Input Session Management
Tracks every external input as a first-class entity.

### 3.3 File Intake System
Handles file validation, decoding, and parsing.

### 3.4 Input Normalization Layer
Transforms external input into canonical ingestion format.

### 3.5 Input Processing Orchestrator
Coordinates full flow from input to run creation.

---

## 4. API Design

### 4.1 Endpoints

POST /api/reconciliation/input/json
POST /api/reconciliation/input/file

### 4.2 JSON Input Contract

Must match ingestion schema exactly.

Invalid payloads are rejected before ingestion.

### 4.3 File Input Contract

Supported format:

- CSV (first-class)
- UTF-8 encoding only

---

## 5. Input Session Model

Each input creates an InputSession:

```text
InputSession
- input_id
- input_type (json | file)
- status (received, validated, rejected, processed)
- validation_result
- ingestion_batch_id
- run_id
- errors
- created_at
```

This ensures full traceability.

---

## 6. File Ingestion Design

### 6.1 Pipeline

```text
file -> validation -> decoding -> parsing -> canonical input
```

### 6.2 Components

- FileValidator
- FileDecoder
- CSVParser
- FileRejectionPolicy

### 6.3 Rules

- No direct file -> ingestion allowed
- All files must pass validation first
- Parsing must be strict and deterministic

---

## 7. Input Mapping Rules

### 7.1 JSON

Direct validation against ingestion contract.

### 7.2 CSV

Explicit mapping:

- columns -> canonical fields
- no dynamic inference
- missing columns = rejection

---

## 8. Upload-to-Run Flow

```text
Input ->
  Validate ->
  Normalize ->
  Ingestion ->
  Run Creation ->
  Lifecycle Execution
```

Must be:

- atomic from user perspective
- fully traceable
- failure-safe

---

## 9. Error Model

### 9.1 Validation Errors
- missing fields
- invalid schema

### 9.2 File Errors
- invalid encoding
- malformed CSV
- invalid headers

### 9.3 Ingestion Rejection
- duplicates
- invalid business rules

### 9.4 Error Format

```text
{
  type: "...",
  code: "...",
  message: "...",
  field: "..."
}
```

---

## 10. Input Constraints

- max file size (to be defined)
- allowed formats: CSV, JSON
- required fields enforced
- strict rejection policy

---

## 11. Traceability Model

```text
InputSession
    |
    v
IngestionBatch
    |
    v
Run
```

Must support debugging from any level.

---

## 12. Implementation Plan

### Phase 1
- InputSession model
- API skeleton

### Phase 2
- JSON input path

### Phase 3
- File ingestion pipeline

### Phase 4
- Mapping integration

### Phase 5
- Error model + traceability

---

## 13. Test Strategy

### Unit Tests
- file validation
- parsing
- mapping

### Integration Tests
- input -> ingestion -> run

### Contract Tests
- API validation

### Failure Tests
- malformed input
- rejection scenarios

---

## 14. Closure Criteria

EPIC is complete only if:

- external input can be submitted via API
- JSON and CSV are supported
- upload -> ingestion -> run is deterministic
- malformed inputs are rejected safely
- no ingestion bypass exists
- traceability is preserved

---

## 15. Key Principle

The system becomes a product only when external input is controlled, validated, and safely integrated.