# Authentication Model

## Purpose

Define the canonical authentication boundary for InvoMatch so the current API surface and existing backend capabilities can be protected by authenticated identity.

## Current Repository Reality

The current system exposes product-facing API routes for:

- input submission and input session lookup
- reconciliation run creation and run visibility
- review case visibility
- run actions
- direct export generation
- export artifact listing, metadata, and download
- health and readiness checks

The current implementation does not yet include:

- authenticated principal resolution
- route-level authentication dependencies
- role-based endpoint protection
- service-level authorization checks

EPIC 25 introduces that boundary without changing core product flow behavior.

## Initial Authentication Approach

The initial authentication model uses internal bearer-token authentication.

Protected requests must provide:

Authorization: Bearer <token>

The token resolves to a known user identity in the application security layer.

This approach is selected because it is:

- explicit
- deterministic
- testable
- environment-safe
- compatible with future replacement by stronger identity providers

## Authentication Boundary Rule

Authentication must be enforced for protected API routes before product or operational logic executes.

Authentication must also produce an explicit auth context that can be passed into backend services.

UI presence must never be treated as proof of identity.

## Public vs Protected Endpoints

### Public

- GET /health
- GET /readiness

### Protected

Protected endpoints include the current product API surface:

- POST /api/reconciliation/input/json
- POST /api/reconciliation/input/file
- GET /api/reconciliation/input/{input_id}
- POST /api/reconciliation/runs
- POST /api/reconciliation/runs/ingest
- GET /api/reconciliation/runs
- GET /api/reconciliation/runs/{run_id}
- GET /api/reconciliation/runs/{run_id}/view
- GET /api/reconciliation/runs/{run_id}/review
- POST /api/reconciliation/runs/{run_id}/actions
- GET /api/reconciliation/runs/{run_id}/export
- GET /api/reconciliation/runs/{run_id}/exports
- GET /api/reconciliation/exports/{artifact_id}
- GET /api/reconciliation/exports/{artifact_id}/download

## Authenticated Principal

Successful authentication yields an authenticated principal with at least:

- user_id
- username
- role
- status
- auth_source
- audit metadata

## User Status

Supported initial user statuses:

- active
- inactive

Rules:

- invalid or unknown token -> 401 Unauthorized
- inactive known user -> 403 Forbidden

Inactive users remain known identities for audit purposes but cannot use protected product capabilities.

## Environment Safety

Authentication configuration must be environment-safe:

- no production secrets hardcoded in source
- local and test credentials must come from explicit configuration
- security seed data must be replaceable by environment
- missing or invalid auth configuration must fail predictably

## Compatibility with Future Expansion

This model is intentionally compatible with future support for:

- external identity providers
- session-backed UI login
- API key support for machine access
- richer user repositories
- organization-aware authorization models

Authorization must depend on resolved identity and permissions, not on the bearer token mechanism itself.

## Backend Enforcement Rule

Authentication must not stop at route protection.

The resolved auth context must be available to backend services so product and operational actions can enforce permission decisions consistently even if another invocation surface is introduced later.

## Audit Visibility

Authentication events must be auditable:

- authentication success
- authentication failure
- inactive-user rejection
- protected endpoint access attempt
- privileged access attempt

## Failure Semantics

- 401 Unauthorized = request has no valid authenticated identity
- 403 Forbidden = request is authenticated but blocked by user status or authorization policy

## Implementation Direction

Implementation should introduce:

- security domain models
- principal / auth context model
- token-to-user authentication service
- FastAPI authentication dependency
- environment-backed user/token provider
- audit hook integration for auth decisions

## Required Validation

Authentication must be covered by:

- unit tests
- API protection tests
- permission boundary scenario coverage
- regression checks on existing product flows