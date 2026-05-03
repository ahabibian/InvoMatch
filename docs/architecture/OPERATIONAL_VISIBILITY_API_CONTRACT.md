# Operational Visibility API Contract

## Purpose

This document freezes the response contracts for the operational visibility API before UI integration.

The operational visibility endpoints are read-only, admin-only API surfaces intended for operator-facing monitoring and diagnostics.

## Authorization

All endpoints in this contract require:

- authenticated request
- operations.view_metrics permission
- admin-level access

Viewer-level users must not access these endpoints.

## Endpoints

### GET /api/operations/metrics

Returns normalized operational metrics and raw metric groupings.

Response model:

OperationalMetricsResponse

Fields:

| Field | Type | Description |
|---|---|---|
| status | string | Overall operational condition. Allowed values: healthy, degraded, attention_required. |
| generated_at | string | ISO-8601 timestamp indicating when the condition was generated. |
| signals | object<string, integer> | Normalized operational signal counters consumed by UI and alert policy. |
| counters | object<string, integer> | Raw operational counters captured by the metrics service. |
| decision_counts | object<string, integer> | Counts grouped by operational recovery decision. |
| reason_counts | object<string, integer> | Counts grouped by operational recovery reason code. |

Stable top-level fields:

- status
- generated_at
- signals
- counters
- decision_counts
- reason_counts

### GET /api/operations/health-summary

Returns a UI-safe operational health summary derived from normalized operational signals.

Response model:

OperationalHealthSummaryResponse

Fields:

| Field | Type | Description |
|---|---|---|
| status | string | Overall operational condition. Allowed values: healthy, degraded, attention_required. |
| generated_at | string | ISO-8601 timestamp indicating when the condition was generated. |
| summary | object<string, string> | Human-readable operational summary grouped by operational area. |
| signals | object<string, integer> | Normalized operational signal counters used to build the health summary. |
| recommended_action | string | Machine-readable recommended operator action. Allowed values: none, inspect_startup_repair, inspect_terminal_failures, inspect_recovery_activity. |

Stable top-level fields:

- status
- generated_at
- summary
- signals
- recommended_action

### GET /api/operations/alerts

Returns machine-readable operational alerts derived from normalized operational signals.

Response model:

OperationalAlertsResponse

Fields:

| Field | Type | Description |
|---|---|---|
| status | string | Whether active operational alerts exist. Allowed values: clear, active. |
| generated_at | string | ISO-8601 timestamp indicating when alerts were evaluated. |
| alerts | array<OperationalAlertResponse> | Stable ordered list of machine-readable operational alerts. |

Stable top-level fields:

- status
- generated_at
- alerts

#### OperationalAlertResponse

| Field | Type | Description |
|---|---|---|
| code | string | Stable machine-readable alert code. |
| severity | string | Alert severity. Allowed values: info, warning, critical. |
| message | string | Human-readable alert message. |
| recommended_action | string | Machine-readable recommended operator action. Allowed values: none, inspect_startup_repair, inspect_terminal_failures, inspect_recovery_activity. |
| signal | string | Operational signal that triggered the alert. |
| value | integer | Signal value observed when the alert was generated. |

Stable alert fields:

- code
- severity
- message
- recommended_action
- signal
- value

## Contract Stability Rules

These endpoints are UI-facing contracts.

The following changes are breaking changes and must not be made casually:

- removing a response field
- renaming a response field
- changing a field type
- changing allowed literal values
- removing response_model from the route declaration
- replacing typed response models with anonymous dictionaries
- changing admin-only access rules

Adding new fields should be treated as a contract change and must be documented with tests.

## Test Coverage

Contract stability is protected by:

- response body shape tests
- OpenAPI response model tests
- authentication tests
- authorization tests

The OpenAPI tests verify that each route exposes a typed response_model and that required fields remain stable.

## Implementation Files

- src/invomatch/api/operations.py
- src/invomatch/api/operations_models.py
- tests/operational/test_operations_metrics_api.py

## Status

Mini-EPIC 31.1 freezes operational visibility response contracts for future UI consumption.