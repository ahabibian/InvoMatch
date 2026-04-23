# Security Audit Visibility

## Purpose

Define the audit and visibility requirements for authentication and authorization decisions in InvoMatch.

EPIC 25 does not only introduce protected access.
It also introduces the requirement that security-relevant decisions remain observable, explainable, and testable.

## Core Principle

A protected system is not sufficiently safe if it only allows or denies access.

It must also make security-relevant decisions visible in a controlled and auditable way.

This includes:

- authentication success
- authentication failure
- inactive-user rejection
- permission denial
- privileged action execution
- admin-only capability usage

## Scope

This document covers security visibility for:

- protected API access
- action execution authorization
- direct export authorization
- artifact access authorization
- reserved admin-only operational capability usage
- UI-visible security outcomes where relevant

It does not define external SIEM integration or enterprise audit export.

## Audit Event Categories

The initial security audit categories are:

- authentication_success
- authentication_failure
- inactive_user_blocked
- authorization_denied
- privileged_action_executed
- admin_surface_accessed

## Authentication Visibility

### authentication_success

Must be recordable when a protected request is successfully authenticated.

Useful audit fields:

- event_type
- timestamp
- user_id
- username
- role
- auth_source
- request_path
- request_method
- correlation_id when available

### authentication_failure

Must be recordable when protected access is attempted without valid identity.

Examples:

- missing bearer token
- invalid token
- unknown token
- malformed authorization header

Useful audit fields:

- event_type
- timestamp
- request_path
- request_method
- failure_reason
- correlation_id when available

Note:
Authentication failure may not always have a resolved user identity.

## User Status Visibility

### inactive_user_blocked

Must be recordable when a known but inactive user attempts protected access.

Useful audit fields:

- event_type
- timestamp
- user_id
- username
- role
- user_status
- request_path
- request_method
- correlation_id when available

## Authorization Visibility

### authorization_denied

Must be recordable when an authenticated active user lacks permission for a requested capability.

Examples:

- viewer attempts input submission
- viewer attempts review resolution
- operator attempts admin-only operation
- authenticated user attempts artifact download without permission

Useful audit fields:

- event_type
- timestamp
- user_id
- username
- role
- requested_capability
- target_resource_type
- target_resource_id when available
- request_path
- request_method
- denial_reason
- correlation_id when available

## Privileged Execution Visibility

### privileged_action_executed

Must be recordable when a privileged or state-changing action is successfully executed under authenticated identity.

Examples:

- resolve_review success
- export_run success
- future privileged operational execution

Useful audit fields:

- event_type
- timestamp
- user_id
- username
- role
- executed_capability
- target_resource_type
- target_resource_id
- request_path
- request_method
- outcome
- correlation_id when available

## Admin Surface Visibility

### admin_surface_accessed

Must be recordable when an admin-only route or capability is successfully used.

Examples:

- future recovery trigger endpoint
- future startup repair execution endpoint
- future admin configuration boundary

Useful audit fields:

- event_type
- timestamp
- user_id
- username
- role
- admin_capability
- target_resource_type
- target_resource_id when available
- outcome
- correlation_id when available

## Minimum Security Audit Fields

At minimum, security audit records should support:

- event_type
- timestamp
- user_id when known
- username when known
- role when known
- auth_source when known
- user_status when relevant
- requested_capability or executed_capability when relevant
- request_path
- request_method
- target_resource_type when relevant
- target_resource_id when relevant
- outcome
- denial_reason or failure_reason when relevant
- correlation_id when available

## Correlation Rule

Security-relevant audit events should be correlatable with request and action flows whenever possible.

This is especially important for:

- denied action attempts
- direct export attempts
- artifact downloads
- future operational repair / recovery execution

A correlation identifier should be included when the request context provides one or when one can be generated safely.

## Separation of Concerns Rule

Security audit visibility must not overwrite existing business audit behavior.

Examples:

- review-domain audit events remain review-domain events
- operational audit events remain operational events

Security events may complement those systems, but should not blur business-state and access-control semantics.

## Service-Level Visibility Rule

Security audit visibility must not depend only on route decorators.

Important protected operations should remain auditable even when permission checks occur in backend services.

This is especially important for:

- action execution
- direct export generation
- artifact download
- future operational admin capabilities

## UI Visibility Rule

The UI is not the primary audit store, but it must not hide security-relevant outcomes.

Important UI-facing outcomes must remain understandable:

- authentication required
- permission denied
- privileged action blocked
- session no longer valid

UI wording may be simplified, but the backend must preserve the real security reason.

## Error Mapping Rule

Security audit visibility must remain compatible with HTTP behavior:

- 401 Unauthorized -> authentication failure
- 403 Forbidden -> inactive user or authorization denied

The audit event should preserve which of these actually occurred.

The UI must not collapse all security denials into generic failure.

## Noise Control Rule

Not every read access success needs heavy audit verbosity.

The initial emphasis should be on:

- failures
- denials
- privileged successes
- admin-only usage

This keeps security visibility useful instead of noisy.

## Repository-Aligned Initial Focus

Based on the current repository surface, the most important initial security visibility events are:

- protected route access without valid auth
- viewer denied on input submission
- viewer denied on review resolution
- viewer denied on direct export
- viewer denied on artifact download
- operator denied on future admin-only operational capability
- operator/admin successful resolve_review
- operator/admin successful export_run

## Validation Expectations

Security visibility must be validated by tests that confirm:

- authentication failures are auditable
- inactive-user blocks are auditable
- authorization denials are auditable
- privileged successful actions are auditable
- 401 and 403 remain distinguishable in audit output
- backend authorization denials are not silently swallowed