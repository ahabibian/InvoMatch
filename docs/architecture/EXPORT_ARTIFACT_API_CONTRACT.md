# EXPORT ARTIFACT API CONTRACT

Status: Draft

## 1. Purpose

This document defines the product-facing API contract for export artifacts.

EPIC 10 treats export artifacts as first-class product resources.
This contract MUST be defined before artifact service logic or API route expansion proceeds.

## 2. Design Principles

The artifact API contract MUST:

- expose artifacts as explicit product resources
- avoid leaking storage implementation details
- provide deterministic lifecycle visibility
- define artifact-specific download behavior
- remain stable even if storage backend changes

The contract MUST NOT expose:
- local file paths
- storage keys
- repository-internal implementation fields

## 3. Artifact Resource Shape

Each artifact resource MUST expose the following product fields:

- artifact_id
- run_id
- artifact_type
- format
- file_name
- content_type
- size_bytes
- state
- created_at
- expires_at
- download_available

Optional future-safe fields:
- checksum
- last_downloaded_at
- deleted_at

## 4. Lifecycle State Contract

Artifact state is a product-level field.

Allowed values:

- available
- expired
- deleted
- failed

Definitions:

### available
Artifact metadata exists and artifact is eligible for download.

### expired
Artifact metadata exists but artifact is no longer eligible for download according to product policy.

### deleted
Artifact metadata exists but underlying artifact has been removed or marked deleted.

### failed
Artifact generation or delivery completed unsuccessfully and no downloadable artifact is available.

State MUST be normalized in product/service layer.
State MUST NOT be inferred directly by API routes from raw storage conditions.

## 5. Endpoint Contract

### 5.1 GET /api/reconciliation/runs/{run_id}/exports

Purpose:
List export artifacts belonging to a run.

Behavior:
- returns all product-visible artifacts for the run
- ordering MUST be deterministic
- response MUST include lifecycle visibility fields
- expired and deleted artifacts MAY still appear in list response if product policy allows historical visibility

Success response shape:
- run_id
- artifacts: [artifact resource]

Error behavior:
- run not found -> 404
- internal failure -> 500

### 5.2 GET /api/reconciliation/exports/{artifact_id}

Purpose:
Return artifact metadata by artifact_id.

Behavior:
- returns product metadata for the artifact
- MUST include lifecycle state and download_available
- MUST NOT expose storage internals

Error behavior:
- artifact not found -> 404
- internal failure -> 500

### 5.3 GET /api/reconciliation/exports/{artifact_id}/download

Purpose:
Download artifact content by artifact_id.

Behavior:
- available -> returns downloadable content
- expired -> deterministic product error
- deleted -> deterministic product error
- failed -> deterministic product error
- missing artifact metadata -> 404
- storage retrieval failure -> controlled failure

This endpoint MUST use artifact_id as the public access handle.
Download behavior MUST be artifact-centric, not run-centric.

## 6. Response Semantics

### 6.1 Artifact List Response

Shape:
- run_id: string
- artifacts: array of artifact resources

### 6.2 Artifact Metadata Response

Shape:
- artifact: artifact resource

### 6.3 Download Response

For successful download:
- file content returned
- content type set correctly
- file name behavior deterministic

For unsuccessful download:
- structured product error response
- no storage details leaked

## 7. download_available Semantics

download_available MUST reflect product truth, not raw implementation convenience.

Examples:
- available + stored correctly -> true
- expired -> false
- deleted -> false
- failed -> false

If product policy says artifact is not downloadable, download_available MUST be false even if a file still physically exists.

## 8. Deterministic Ordering

List response ordering MUST be defined explicitly.

Recommended default:
- created_at descending
- artifact_id as deterministic tie-breaker

No implicit database ordering is allowed.

## 9. Error Model

Artifact-facing endpoints SHOULD use a stable product error shape.

Minimum fields:
- code
- message

Recommended product error codes:
- artifact_not_found
- artifact_expired
- artifact_deleted
- artifact_failed
- artifact_unavailable
- run_not_found

Error responses MUST be product-safe and MUST NOT leak internal storage or repository implementation details.

## 10. Contract Boundary

This contract defines:
- public artifact fields
- lifecycle values
- endpoint semantics
- download behavior
- error expectations

This contract does NOT define:
- internal repository schema
- storage backend design
- cleanup scheduler implementation
- authorization model expansion

## 11. Delivery Rule

No EPIC 10 implementation may introduce:
- artifact routes
- service methods
- response models
- error behavior

unless they conform to this contract.
