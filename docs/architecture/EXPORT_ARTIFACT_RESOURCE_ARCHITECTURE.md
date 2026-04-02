# EXPORT ARTIFACT RESOURCE ARCHITECTURE

Status: Draft

## 1. Problem

In EPIC 9, export artifacts were introduced as outputs of export operations.
However, artifacts are not yet modeled as first-class product resources.

Current limitations:
- No artifact-centric API
- No explicit lifecycle model
- No stable artifact identity in product layer
- Download behavior is implicit and not contract-defined

## 2. Goal

Promote export artifacts to first-class product resources with:

- explicit identity (artifact_id)
- artifact-centric retrieval
- lifecycle visibility
- deterministic download behavior
- clean separation from storage internals

## 3. Resource Model

Artifact is a standalone product resource.

Key properties:
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

## 4. Lifecycle States

Artifacts MUST have explicit lifecycle states:

- available
- expired
- deleted
- failed

State MUST NOT be inferred directly from storage layer.

## 5. Access Patterns

Supported operations:

- list artifacts for a run
- get artifact metadata by artifact_id
- download artifact by artifact_id

## 6. Download Semantics

Download behavior MUST be deterministic:

- available → file returned
- expired → explicit error
- deleted → explicit error
- missing → not found
- storage failure → controlled failure

## 7. Storage Isolation

Product layer MUST NOT expose:
- file system paths
- storage keys
- backend-specific identifiers

## 8. Cleanup Boundary

This EPIC defines:
- visibility of expiry
- lifecycle state exposure

This EPIC does NOT require:
- full background cleanup scheduler

## 9. Non-Goals

- redesign export generation
- cloud delivery (signed URLs)
- multi-tenant access control expansion

## 10. Delivery Rule

EPIC 10 MUST be driven by Product Contract first.

Implementation order:
1. product contract
2. service behavior
3. API routes
4. tests
5. closure

No endpoint or handler should be introduced before its product contract and lifecycle semantics are defined.
