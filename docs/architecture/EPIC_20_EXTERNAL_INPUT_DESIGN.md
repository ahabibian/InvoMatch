# EPIC 20 - External Input Boundary Design

---

## 1. Design Goal

Define the concrete services, interfaces, data models, and execution flow required to expose a safe external input boundary for InvoMatch.

This design turns the EPIC 20 architecture into implementable building blocks.

---

## 2. Design Principles

- API-first
- ingestion remains the canonical intake boundary
- no direct external input -> run creation bypass
- file parsing must be explicit and deterministic
- traceability must exist across input session, ingestion batch, and run
- user-facing errors must be structured and stable
- malformed inputs must fail closed, never fail open

---

## 3. Proposed Modules

```text
src/invomatch/domain/input_boundary/
src/invomatch/services/input_boundary/
src/invomatch/api/routes/input_boundary.py
src/invomatch/api/product_models/input_boundary.py
tests/input_boundary/
tests/contracts/test_product_contract_input_boundary.py
tests/test_input_boundary_api.py
```

---

## 4. Domain Models

### 4.1 InputSession

Represents one external submission.

Fields:

- input_id
- input_type
- status
- source_filename
- source_content_type
- source_size_bytes
- validation_errors
- ingestion_batch_id
- run_id
- created_at
- updated_at

### 4.2 InputType

Allowed values:

- json
- file

### 4.3 InputSessionStatus

Allowed values:

- received
- validated
- rejected
- ingested
- run_created
- failed

### 4.4 InputError

Fields:

- type
- code
- message
- field
- details

---

## 5. Service Design

### 5.1 InputProcessingService

Main orchestrator for external input.

Responsibilities:

- create input session
- validate input
- route by input type
- normalize external data
- invoke ingestion gateway
- invoke run creation service
- update traceability links
- return stable product response

### 5.2 JsonInputService

Responsibilities:

- validate JSON payload against canonical input contract
- produce normalized ingestion request
- reject invalid structured payloads

### 5.3 FileInputService

Responsibilities:

- validate uploaded file
- decode bytes
- parse CSV
- map rows into canonical ingestion input
- reject malformed files safely

### 5.4 FileValidator

Responsibilities:

- enforce format rules
- enforce max size
- enforce file presence
- enforce content-type / extension rules

### 5.5 FileDecoder

Responsibilities:

- decode file bytes using strict UTF-8
- reject invalid encoding

### 5.6 CsvInputParser

Responsibilities:

- parse CSV deterministically
- reject malformed rows
- reject missing required headers
- produce raw structured rows for mapping

### 5.7 CsvInputMapper

Responsibilities:

- map parsed CSV rows into canonical invoice/payment input objects
- enforce explicit column mappings
- reject missing or ambiguous fields

### 5.8 InputSessionRepository

Responsibilities:

- persist InputSession records
- update lifecycle status
- store linked ingestion_batch_id and run_id
- support lookup by input_id

---

## 6. API Surface

### 6.1 POST /api/reconciliation/input/json

Accepts structured JSON input.

Request body:

```text
{
  invoices: [],
  payments: []
}
```

Response shape:

```text
{
  input_id: "...",
  status: "...",
  ingestion_batch_id: "...",
  run_id: "...",
  errors: []
}
```

### 6.2 POST /api/reconciliation/input/file

Accepts multipart file upload.

Supported:

- CSV only

Response shape:

```text
{
  input_id: "...",
  status: "...",
  ingestion_batch_id: "...",
  run_id: "...",
  errors: []
}
```

### 6.3 GET /api/reconciliation/input/{input_id}

Returns input session status and traceability info.

---

## 7. Product Models

### 7.1 ProductInputSubmissionResponse

Fields:

- input_id
- status
- ingestion_batch_id
- run_id
- errors

### 7.2 ProductInputSessionView

Fields:

- input_id
- input_type
- status
- source_filename
- source_size_bytes
- ingestion_batch_id
- run_id
- errors
- created_at
- updated_at

### 7.3 ProductInputError

Fields:

- type
- code
- message
- field

---

## 8. Mapping Rules

### 8.1 JSON Path

JSON must already conform to ingestion contract expectations.

Rules:

- invoices must be a list
- payments must be a list
- item-level required fields must be enforced
- invalid payload shape must be rejected before ingestion

### 8.2 CSV Path

CSV is not treated as domain truth.

CSV must be transformed through explicit mapping rules into canonical ingestion objects.

Example strict headers:

- record_type
- entity_id
- invoice_number
- payment_reference
- amount
- currency
- date

Rules:

- unknown headers do not create inferred fields
- missing required headers cause rejection
- record_type determines invoice vs payment mapping
- each row must map deterministically

---

## 9. Execution Flow

### 9.1 JSON Flow

```text
API request
-> InputSession created
-> JSON validated
-> ingestion request built
-> ingestion service invoked
-> run integration service invoked
-> InputSession updated
-> product response returned
```

### 9.2 File Flow

```text
API request
-> InputSession created
-> file validated
-> file decoded
-> CSV parsed
-> rows mapped
-> ingestion request built
-> ingestion service invoked
-> run integration service invoked
-> InputSession updated
-> product response returned
```

---

## 10. Failure Model

### 10.1 Validation Failure

Returned when request payload or file metadata is invalid.

No ingestion call allowed.

### 10.2 Decode Failure

Returned when file bytes cannot be decoded as UTF-8.

No ingestion call allowed.

### 10.3 Parse Failure

Returned when CSV is malformed or headers are invalid.

No ingestion call allowed.

### 10.4 Mapping Failure

Returned when parsed rows cannot be deterministically mapped.

No ingestion call allowed.

### 10.5 Ingestion Rejection

Returned when canonical input is valid structurally but rejected by ingestion rules.

### 10.6 Run Creation Failure

Returned when ingestion succeeds but run creation fails.

Must preserve traceability.

---

## 11. Traceability Rules

Every successful or failed submission must preserve a trace chain:

```text
InputSession -> IngestionBatch -> Run
```

If flow fails before ingestion:
- InputSession exists
- ingestion_batch_id is null
- run_id is null

If flow fails after ingestion:
- InputSession exists
- ingestion_batch_id is populated
- run_id may be null

---

## 12. Storage Strategy

Initial implementation may use an in-memory repository or SQLite-backed repository, but the interface must be explicit and swappable.

Preferred boundary:

- InputSessionRepository protocol/interface
- InMemoryInputSessionRepository for early implementation
- SqliteInputSessionRepository if needed in same EPIC or next hardening EPIC

---

## 13. Implementation Sequence

### Phase A
- domain models
- product models
- repository interface
- in-memory repository

### Phase B
- JSON service path
- API endpoint for JSON input

### Phase C
- file validator
- decoder
- CSV parser
- CSV mapper

### Phase D
- file endpoint
- integration wiring

### Phase E
- input session query endpoint
- traceability validation
- contract and failure tests

---

## 14. Test Strategy

### Unit
- file validator
- decoder
- parser
- mapper
- JSON validator
- input processing orchestration

### API
- json submission success/failure
- file submission success/failure
- session lookup

### Integration
- input -> ingestion -> run
- ingestion rejection propagation
- run creation failure propagation

### Contract
- response shape is stable
- no internal fields leak
- structured error format is preserved

---

## 15. Closure Standard

EPIC 20 is closed only if:

- external JSON input works
- external CSV input works
- no bypass exists around ingestion contracts
- traceability is preserved
- deterministic failures are enforced
- API responses are contract-backed