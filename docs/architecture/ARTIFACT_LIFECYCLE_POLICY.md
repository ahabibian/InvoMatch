# ARTIFACT LIFECYCLE POLICY

Status: Draft

## 1. Purpose

This document defines the lifecycle policy for export artifacts in EPIC 10.

The goal is to ensure that artifact visibility, access, expiry, and cleanup behavior are product-defined rather than implicitly derived from storage implementation details.

## 2. Core Rule

Artifact lifecycle is determined by product policy.

Storage layer may provide facts such as:
- artifact record exists
- file exists
- file missing
- retrieval failed

But storage facts alone MUST NOT define the final product state exposed by the API.

## 3. Lifecycle States

Allowed artifact lifecycle states:

- available
- expired
- deleted
- failed

These are product states, not raw infrastructure states.

## 4. State Definitions

### 4.1 available

Meaning:
- artifact metadata exists
- artifact is considered valid by product policy
- artifact is eligible for download

Expected API behavior:
- visible in artifact listing
- metadata retrievable
- download_available = true
- download endpoint may return file content

### 4.2 expired

Meaning:
- artifact metadata exists
- retention or access policy says artifact is no longer downloadable
- historical visibility may still be preserved

Expected API behavior:
- may remain visible in artifact listing
- metadata retrievable
- download_available = false
- download endpoint returns product error
- physical file presence does not override expired state

### 4.3 deleted

Meaning:
- artifact metadata exists or artifact identity remains historically known
- artifact has been explicitly removed or marked deleted
- artifact is not downloadable

Expected API behavior:
- may remain visible in artifact listing if product policy preserves history
- metadata retrievable if historical visibility is supported
- download_available = false
- download endpoint returns product error

### 4.4 failed

Meaning:
- export artifact generation or delivery did not complete successfully
- no valid downloadable artifact is available

Expected API behavior:
- artifact may be visible if product wants failure visibility
- metadata retrievable if record exists
- download_available = false
- download endpoint returns product error

## 5. State Derivation Rules

Product/service layer SHOULD normalize final artifact state using policy and known facts.

Recommended priority model:

1. failed
2. deleted
3. expired
4. available

Interpretation:
- if artifact is marked failed, it remains failed
- if artifact is marked deleted, it remains deleted
- if artifact is not failed or deleted but expiry policy has passed, it becomes expired
- only non-failed, non-deleted, non-expired artifacts may be available

## 6. Expiry Policy

Artifacts MAY have an expires_at value.

Rules:
- if expires_at is null, artifact does not expire automatically by current policy
- if expires_at is in the past, artifact transitions to expired unless it is already failed or deleted
- expiry affects download eligibility even if file still physically exists

Expiry is a product rule, not a storage condition.

## 7. Download Eligibility Rule

download_available MUST reflect product policy.

download_available = true only when:
- state = available
- artifact metadata exists
- product policy allows download

download_available MUST be false when:
- state = expired
- state = deleted
- state = failed

If a file physically exists but product policy says download is disallowed, the API MUST return download_available = false.

## 8. Historical Visibility Rule

Historical visibility is allowed.

This means:
- expired artifacts MAY remain listable
- deleted artifacts MAY remain listable
- failed artifacts MAY remain listable

This EPIC does not require hiding all non-downloadable artifacts from list endpoints.

Reason:
historical visibility is useful for product transparency, auditability, and future UI behavior.

## 9. Cleanup Boundary

EPIC 10 defines:
- lifecycle visibility
- expiry semantics
- download eligibility semantics
- product behavior for expired/deleted/failed artifacts

EPIC 10 does NOT require:
- background scheduler
- automated deletion worker
- physical cleanup orchestration
- storage compaction

Cleanup automation may be added in a later EPIC.

## 10. Missing File Scenarios

If artifact metadata exists but storage file is missing:

- product layer MUST NOT leak storage details
- final outcome depends on policy and implementation decision

Recommended current policy:
- if artifact was expected to be downloadable but file is missing, treat it as artifact_unavailable at access time
- do not silently reclassify it as deleted unless deletion was explicitly recorded

This distinction preserves product truth and avoids incorrect state mutation from incidental storage loss.

## 11. Product Error Expectations

Recommended download-time product errors:

- artifact_not_found
- artifact_expired
- artifact_deleted
- artifact_failed
- artifact_unavailable

These errors describe product-visible behavior and must not expose storage internals.

## 12. EPIC 10 Delivery Rule

Any EPIC 10 service or API implementation MUST conform to this lifecycle policy.

Specifically:
- state exposure must follow this policy
- download_available must follow this policy
- download route behavior must follow this policy
- cleanup implementation beyond this boundary is out of scope unless a concrete defect requires it
