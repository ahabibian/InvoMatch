# EPIC 20 — Test Strategy

---

## 1. Testing Goal

Prove that the external input boundary is safe, deterministic, and fully integrated with ingestion and run creation.

---

## 2. Unit Test Coverage

### Input Session
- create input session
- update status
- attach error details
- attach ingestion batch id
- attach run id

### JSON Validation
- valid request accepted
- missing field rejected
- invalid field type rejected

### File Validation
- unsupported extension rejected
- oversized file rejected
- invalid encoding rejected

### CSV Parsing
- valid CSV parsed deterministically
- malformed CSV rejected
- invalid header layout rejected

### CSV Mapping
- valid row mapping
- missing required column rejection
- invalid row value rejection

### Error Mapping
- validation error normalization
- parsing error normalization
- ingestion rejection normalization

---

## 3. Integration Test Coverage

### JSON Entry Flow
request → input boundary → ingestion → run creation

### CSV Entry Flow
file upload → validation → parse → mapping → ingestion → run creation

### Traceability Flow
input session → ingestion batch → run linkage preserved

### Failure Flow
boundary rejection preserves input session trace

---

## 4. API Contract Coverage

- POST /api/reconciliation/input/json request contract
- POST /api/reconciliation/input/json response contract
- POST /api/reconciliation/input/file request contract
- POST /api/reconciliation/input/file response contract
- structured error contract

---

## 5. Failure Path Coverage

- invalid JSON schema
- unsupported file type
- malformed CSV
- missing CSV headers
- ingestion duplicate rejection
- ingestion validation rejection
- run creation integration failure

---

## 6. Closure Proof

EPIC 20 can close only when tests prove:

- no ingestion bypass exists
- deterministic mapping behavior exists
- malformed external input is rejected safely
- valid external input reaches run creation correctly
- traceability is preserved end-to-end