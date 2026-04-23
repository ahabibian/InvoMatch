# Endpoint Protection Map

## Purpose

Map the current repository API surface to explicit authentication and authorization requirements.

This document translates the authorization capability model into route-level protection rules without creating a second policy source.

The authorization rule matrix remains the source of truth for permission definitions.
This map defines how those permissions apply to the current API endpoints.

## Protection Design Rules

- Public endpoints must be explicitly listed
- All other product endpoints are protected by default
- Route protection does not replace service-level authorization
- UI visibility does not affect backend protection
- Generic action endpoints must perform action-specific permission evaluation
- New endpoints must be added explicitly before being considered protected correctly

## Public Endpoints

The following endpoints remain public in the initial EPIC 25 boundary:

- GET /health
- GET /readiness

Reasoning:

- these endpoints support deployment and operational probing
- they do not expose product data or mutating capability
- keeping them public avoids unnecessary friction for current runtime monitoring

## Protected Endpoint Map

### Input Boundary

#### POST /api/reconciliation/input/json

Authentication:
- required

Allowed roles:
- operator
- admin

Required capability:
- input.submit

Notes:
- state-changing entry into the product boundary
- viewer is denied

#### POST /api/reconciliation/input/file

Authentication:
- required

Allowed roles:
- operator
- admin

Required capability:
- input.submit

Notes:
- state-changing entry into the product boundary
- viewer is denied

#### GET /api/reconciliation/input/{input_id}

Authentication:
- required

Allowed roles:
- viewer
- operator
- admin

Required capability:
- input.view

## Reconciliation Runs

### POST /api/reconciliation/runs

Authentication:
- required

Allowed roles:
- operator
- admin

Required capability:
- runs.create

Notes:
- creates reconciliation run from path-based request body
- not allowed for viewer

### POST /api/reconciliation/runs/ingest

Authentication:
- required

Allowed roles:
- operator
- admin

Required capability:
- runs.create_from_ingestion

Notes:
- creates reconciliation run from ingestion payloads
- not allowed for viewer

### GET /api/reconciliation/runs

Authentication:
- required

Allowed roles:
- viewer
- operator
- admin

Required capability:
- runs.list

### GET /api/reconciliation/runs/{run_id}

Authentication:
- required

Allowed roles:
- viewer
- operator
- admin

Required capability:
- runs.read

### GET /api/reconciliation/runs/{run_id}/view

Authentication:
- required

Allowed roles:
- viewer
- operator
- admin

Required capability:
- runs.read_view

### GET /api/reconciliation/runs/{run_id}/review

Authentication:
- required

Allowed roles:
- viewer
- operator
- admin

Required capability:
- runs.read_review

## Action Endpoint

### POST /api/reconciliation/runs/{run_id}/actions

Authentication:
- required

Allowed roles:
- operator
- admin

Base endpoint rule:
- user must be authenticated
- user must have access to action execution surface
- requested action type must be authorized separately

Action-type capability mapping:

- resolve_review -> actions.resolve_review
- export_run -> actions.export_run

Notes:
- viewer is denied for the endpoint
- action permission must be evaluated from request payload action type
- authorization does not bypass action_guard or lifecycle rules
- unsupported or newly added action types must default to denied unless explicitly mapped

## Direct Export Endpoint

### GET /api/reconciliation/runs/{run_id}/export

Authentication:
- required

Allowed roles:
- operator
- admin

Required capability:
- exports.download_direct

Notes:
- this endpoint is not read-only metadata access
- it creates an export artifact and returns content immediately
- viewer is denied
- authorization does not bypass export eligibility rules

## Export Artifact Endpoints

### GET /api/reconciliation/runs/{run_id}/exports

Authentication:
- required

Allowed roles:
- viewer
- operator
- admin

Required capability:
- artifacts.list

### GET /api/reconciliation/exports/{artifact_id}

Authentication:
- required

Allowed roles:
- viewer
- operator
- admin

Required capability:
- artifacts.read_metadata

### GET /api/reconciliation/exports/{artifact_id}/download

Authentication:
- required

Allowed roles:
- operator
- admin

Required capability:
- artifacts.download

Notes:
- viewer is denied in the initial policy
- artifact download is treated as protected business data extraction, not simple read visibility

## Reserved Admin-Only Operational Surface

The current repository contains privileged operational and repair services, even though they are not yet fully exposed as public API routes.

If or when routes are introduced for these capabilities, they must be admin-only by default.

Reserved admin-only capability areas:

- startup repair execution
- restart consistency repair execution
- runtime recovery execution
- operational metrics access
- operational control / repair endpoints
- future security configuration endpoints

Associated admin-only capabilities:

- operations.view_metrics
- operations.execute_recovery
- operations.execute_startup_repair
- operations.manage_admin_surface

## Inactive User Rule

A known but inactive authenticated user must not access any protected endpoint.

Behavior:

- authentication succeeds at identity resolution level
- endpoint access is denied with 403 Forbidden
- denial remains auditable

## Failure Semantics

### 401 Unauthorized

Return when:

- Authorization header is missing for protected endpoint
- token is invalid
- token does not resolve to known user identity

### 403 Forbidden

Return when:

- user is authenticated but inactive
- user lacks required route capability
- user lacks required action-specific capability
- user attempts reserved admin-only capability without admin privilege

### Other application errors

Business and application-level errors remain separate from auth failures.

Examples:

- 404 run not found
- 409 action conflict
- 422 export data incomplete

Authorization must run before business mutation, but it must not rewrite business-state semantics once permission is granted.

## Service-Level Alignment Rule

Every protected route in this map must align with backend enforcement.

At minimum, backend permission enforcement is required for:

- action execution
- direct export generation
- artifact download
- future operational repair / recovery surfaces

## UI Alignment Rule

The UI may use this map to hide screens or disable actions, but backend enforcement remains authoritative.

UI mismatch must never lead to unauthorized backend success.

## Validation Expectations

This map must be validated by tests that confirm:

- public endpoints remain accessible without auth
- protected endpoints reject unauthenticated access
- viewer / operator / admin route protection is correct
- action endpoint permission depends on action type
- direct export and artifact download boundaries are enforced
- inactive users are rejected consistently
- backend enforcement matches route protection