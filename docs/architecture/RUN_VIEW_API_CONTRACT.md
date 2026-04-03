# RUN VIEW API CONTRACT

Status: Proposed
EPIC: 11
Title: Product Run View API Contract

## 1. Purpose

This document defines the product API contract for the unified run-centric read model introduced in EPIC 11.

Endpoint:

GET /api/reconciliation/runs/{run_id}/view

This endpoint returns the canonical product-facing read projection for a single reconciliation run.

This contract exists to ensure:
- stable field naming
- explicit section semantics
- no domain leakage
- deterministic ordering
- predictable nullability
- UI-safe and integration-safe response behavior

---

## 2. Contract Principles

### 2.1 Product Contract Only
The response must expose only product-safe fields.
It must not mirror internal domain or persistence structures.

### 2.2 Explicitness
Sections such as review_summary and export_summary must be present even when their underlying subsystem state is absent or not ready.

### 2.3 Determinism
For the same persisted state, the response shape, field presence, and ordering must remain stable.

### 2.4 No Storage Leakage
No filesystem path, storage backend detail, driver name, bucket/container name, or local implementation-specific information may appear in the contract.

### 2.5 Stable Evolution
New fields may be added in future versions only in a backward-compatible way.
Existing field meaning must not drift.

---

## 3. Endpoint Definition

### 3.1 Route

GET /api/reconciliation/runs/{run_id}/view

### 3.2 Success Response

HTTP 200 OK

Content-Type:
application/json

Returns:
ProductRunView

### 3.3 Not Found Response

If the run does not exist, the endpoint returns:

HTTP 404 Not Found

The precise error envelope should remain consistent with existing API error behavior used elsewhere in the product surface.

---

## 4. ProductRunView Schema

### 4.1 Top-Level Shape

{
  "run_id": "string",
  "status": "queued|processing|review_required|completed|failed|cancelled",
  "created_at": "ISO-8601 timestamp",
  "updated_at": "ISO-8601 timestamp",
  "match_summary": {
    "total_items": 0,
    "matched_items": 0,
    "unmatched_items": 0,
    "ambiguous_items": 0
  },
  "review_summary": {
    "status": "not_started|pending|in_review|completed|not_required",
    "total_items": 0,
    "open_items": 0,
    "resolved_items": 0
  },
  "export_summary": {
    "status": "not_ready|ready|exported",
    "artifact_count": 0
  },
  "artifacts": [
    {
      "artifact_id": "string",
      "kind": "string",
      "file_name": "string",
      "media_type": "string",
      "size_bytes": 0,
      "created_at": "ISO-8601 timestamp",
      "download_url": "string"
    }
  ]
}

---

## 5. Field Definitions

### 5.1 Top-Level Fields

#### run_id
Type:
string

Required:
yes

Meaning:
Stable product identifier of the run.

#### status
Type:
string enum

Required:
yes

Allowed values:
- queued
- processing
- review_required
- completed
- failed
- cancelled

Meaning:
Canonical product lifecycle state for the run.

#### created_at
Type:
string (timestamp)

Required:
yes

Meaning:
Run creation timestamp.

#### updated_at
Type:
string (timestamp)

Required:
yes

Meaning:
Most recent product-visible update timestamp for the run.

---

### 5.2 match_summary

Type:
object

Required:
yes

Fields:
- total_items
- matched_items
- unmatched_items
- ambiguous_items

### 5.3 review_summary

Type:
object

Required:
yes

Rules:
- review_summary must always be present
- if no review exists, explicit product-safe defaults must still be returned

### 5.4 export_summary

Type:
object

Required:
yes

Rules:
- export_summary must always be present
- artifact existence alone must not imply readiness

### 5.5 artifacts

Type:
array

Required:
yes

Rules:
- must always be an array
- must never be null

---

## 6. Ordering Rules

Artifacts must be returned in deterministic order:
1. created_at ascending
2. artifact_id ascending

---

## 7. State Consistency Rules

### 7.1 Export Readiness Rule
If run.status is not compatible with completed export readiness, export_summary.status must be not_ready.

### 7.2 Review Explicitness Rule
If no review exists for the run, review_summary must still be present.

### 7.3 Artifact Non-Inference Rule
Artifact presence must not imply export readiness by itself.

### 7.4 Storage Isolation Rule
No artifact or export field may expose internal filesystem or storage details.

---

## 8. Summary

The Run View API contract defines a single, stable, run-centric response surface for product consumers.
It is explicit, deterministic, stable, and product-safe.
