
Phase E Match Detail Backend Implementation Plan

Mini-EPIC: 33.13.C

Purpose

This document converts the Mini-EPIC 33.13.B git-native backend source discovery into a bounded backend implementation plan for the product-facing Match Detail / Evidence read path.

This is a planning boundary only.

This document does not implement backend behavior.

This document does not authorize Base44 binding.

This document does not authorize live UI wiring.

This document does not claim Scenario 15 completion.

Starting State

Starting commit subject:

docs(epic-33): discover match detail evidence backend source signals

Starting HEAD:

878443a5c6a27f79c57eb9e1dac3f96ad81d448b

Discovery source:

docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_SOURCE_DISCOVERY.md

Discovery Inputs

The implementation plan is based on the following discovery counts:

Route signals: 76
Review Queue signals: 12
match_id signals: 91
Match Detail signals: 0
Evidence signals: 46
Traceability signals: 200
Failure semantics signals: 200
API/test signals: 200
Product-Facing Backend Contract Goal

The backend must expose a product-facing Match Detail / Evidence read path before any Base44 binding is allowed.

The target path remains:

Review Queue -> stable match_id -> product-facing Match Detail retrieval -> backend-owned evidence payload -> backend-owned traceability payload -> explicit failure semantics -> UI-displayable response without frontend truth synthesis.

Implementation Boundary

33.13.C does not build the implementation.

33.13.C defines the implementation plan that the next execution step must follow.

Implementation must be backend-side only.

Implementation must not create or modify Base44 prompts.

Implementation must not perform live UI wiring.

Implementation must not add Human Correction binding.

Implementation must not add Finalized Truth binding.

Implementation must not add Export Readiness binding.

Implementation must not add Intake Workspace binding.

Planned Backend Route Boundary

A product-facing route must be added or confirmed for Match Detail / Evidence retrieval.

Expected route shape:

GET /api/review/matches/{match_id}/detail

The exact path may be adjusted only if existing API conventions require it, but the route must remain product-facing and match_id-based.

The route must not require the frontend to fallback to invoice_id or payment_id.

The route must not require the frontend to reconstruct match truth from Review Queue row data.

Planned Request Contract

The request contract must use stable match_id as the primary identifier.

Required request constraint:

match_id is required
match_id must come from backend-owned Review Queue output
no frontend-generated match identity is allowed
invoice_id/payment_id fallback is forbidden unless explicitly backend-defined
Planned Response DTO / Read Model

A backend-owned Match Detail response DTO/read model must be defined.

Minimum planned response shape:

match_id
match_status or match posture
invoice summary
payment summary
backend-owned evidence payload
backend-owned traceability payload
backend-owned explanation if available
backend-owned confidence/score if available
source references using audit-safe identifiers
response metadata if needed for versioning

The response must be UI-displayable without frontend truth synthesis.

Planned Evidence Payload

Evidence must be mapped by backend code only.

The evidence payload must be:

linked to match_id
structured
display-safe
backend-owned
free from frontend-generated calculations
stable enough for contract tests

The frontend may display evidence but must not generate, merge, infer, calculate, or reinterpret evidence.

Planned Traceability Payload

Traceability must be mapped by backend code only.

The traceability payload must expose audit-safe backend-owned references, including any available:

invoice linkage
payment linkage
source record references
source file or source batch references if available
projection/run linkage if available
audit-safe identifiers

The frontend must not generate traceability from local UI state.

Planned Failure Semantics

The backend route/adapter must distinguish at least these product-facing failure states:

match not found
missing evidence
unavailable evidence
malformed or incomplete payload
backend error

Failure semantics must be backend-owned.

The UI may display failure states but must not synthesize them.

Planned Adapter / Service Responsibility

A backend adapter or service layer must translate existing internal match, evidence, traceability, projection, or review data into the product-facing Match Detail response.

The adapter/service must own:

lookup by match_id
response assembly
evidence mapping
traceability mapping
failure-state mapping
response DTO stability
no frontend truth synthesis guarantee
Candidate API / Route Files

The next implementation step should inspect and select from these tracked candidate API/route files:

- src/invomatch/api/actions.py
- src/invomatch/api/audit_events.py
- src/invomatch/api/auth_session.py
- src/invomatch/api/export.py
- src/invomatch/api/export_artifacts.py
- src/invomatch/api/health.py
- src/invomatch/api/mappers/product_contract.py
- src/invomatch/api/operations.py
- src/invomatch/api/operations_models.py
- src/invomatch/api/product_models/__init__.py
- src/invomatch/api/product_models/action.py
- src/invomatch/api/product_models/audit_event.py
- src/invomatch/api/product_models/auth_session.py
- src/invomatch/api/product_models/export.py
- src/invomatch/api/product_models/export_artifact.py
- src/invomatch/api/product_models/input_boundary.py
- src/invomatch/api/product_models/match_result.py
- src/invomatch/api/product_models/review_case.py
- src/invomatch/api/product_models/run.py
- src/invomatch/api/product_models/run_view.py
- src/invomatch/api/reconciliation_runs.py
- src/invomatch/api/reconciliation_schemas.py
- src/invomatch/api/review_cases.py
- src/invomatch/api/routes/input_boundary.py
- src/invomatch/api/security/__init__.py
- src/invomatch/api/security/dependencies.py
- src/invomatch/api/security/errors.py
- tests/audit/test_audit_api.py
- tests/operational/test_operations_metrics_api.py
- tests/test_actions_api.py


Candidate Service / Adapter Files

The next implementation step should inspect and select from these tracked candidate service/adapter files:

- src/invomatch/api/product_models/review_case.py
- src/invomatch/api/review_cases.py
- src/invomatch/domain/matching/__init__.py
- src/invomatch/domain/matching/decisioning.py
- src/invomatch/domain/matching/features.py
- src/invomatch/domain/matching/models.py
- src/invomatch/domain/matching/rules.py
- src/invomatch/domain/matching/taxonomy.py
- src/invomatch/domain/review/models.py
- src/invomatch/ingestion/services/__init__.py
- src/invomatch/ingestion/services/decision_builder.py
- src/invomatch/ingestion/services/duplicate_classifier.py
- src/invomatch/ingestion/services/invoice_ingestion_gateway.py
- src/invomatch/ingestion/services/invoice_ingestion_service.py
- src/invomatch/ingestion/services/payment_ingestion_gateway.py
- src/invomatch/ingestion/services/payment_ingestion_service.py
- src/invomatch/services/action_service.py
- src/invomatch/services/actions/action_guard.py
- src/invomatch/services/actions/command.py
- src/invomatch/services/actions/dispatcher.py
- src/invomatch/services/actions/execution_service.py
- src/invomatch/services/actions/handlers/__init__.py
- src/invomatch/services/actions/handlers/base.py
- src/invomatch/services/actions/handlers/export_run.py
- src/invomatch/services/actions/handlers/resolve_review.py
- src/invomatch/services/actions/result.py
- src/invomatch/services/artifact_query_service.py
- src/invomatch/services/audit/__init__.py
- src/invomatch/services/audit/audit_query_service.py
- src/invomatch/services/completed_run_projection_service.py


Candidate Model / DTO Files

The next implementation step should inspect and select from these tracked candidate model/schema/DTO files:

- src/invomatch/api/mappers/product_contract.py
- src/invomatch/api/operations_models.py
- src/invomatch/api/product_models/__init__.py
- src/invomatch/api/product_models/action.py
- src/invomatch/api/product_models/audit_event.py
- src/invomatch/api/product_models/auth_session.py
- src/invomatch/api/product_models/export.py
- src/invomatch/api/product_models/export_artifact.py
- src/invomatch/api/product_models/input_boundary.py
- src/invomatch/api/product_models/match_result.py
- src/invomatch/api/product_models/review_case.py
- src/invomatch/api/product_models/run.py
- src/invomatch/api/product_models/run_view.py
- src/invomatch/api/reconciliation_schemas.py
- src/invomatch/api/review_cases.py
- src/invomatch/config/models.py
- src/invomatch/domain/audit/models.py
- src/invomatch/domain/export/models.py
- src/invomatch/domain/export_delivery/models.py
- src/invomatch/domain/feedback/models.py
- src/invomatch/domain/input_boundary/models.py
- src/invomatch/domain/matching/models.py
- src/invomatch/domain/models.py
- src/invomatch/domain/operational/models.py
- src/invomatch/domain/review/models.py
- src/invomatch/domain/tenant/models.py
- src/invomatch/ingestion/models/__init__.py
- src/invomatch/ingestion/models/duplicate_models.py
- src/invomatch/ingestion/models/ingestion_record.py
- src/invomatch/ingestion/models/ingestion_result.py


Candidate Contract / API Test Files

The next implementation step should inspect and select from these tracked candidate test files:

- tests/audit/test_audit_api.py
- tests/contracts/conftest.py
- tests/contracts/test_internal_field_leakage.py
- tests/contracts/test_product_contract_actions.py
- tests/contracts/test_product_contract_ingest_run.py
- tests/contracts/test_product_contract_input_boundary.py
- tests/contracts/test_product_contract_review.py
- tests/contracts/test_product_contract_runs.py
- tests/domain/test_feedback_time_contract.py
- tests/operational/test_operations_metrics_api.py
- tests/services/test_reconciliation_match_persistence.py
- tests/services/test_sqlite_match_record_store.py
- tests/sqlite_contract/conftest.py
- tests/sqlite_contract/test_run_store_contract_sqlite.py
- tests/system/test_review_required_taxonomy_alignment.py
- tests/system/test_review_resolution_flow.py
- tests/test_actions/test_resolve_review.py
- tests/test_actions/test_resolve_review_conflicts.py
- tests/test_actions_api.py
- tests/test_artifact_storage_contract.py
- tests/test_auth_session_api.py
- tests/test_export_api.py
- tests/test_export_artifact_api.py
- tests/test_export_artifact_repository_contract.py
- tests/test_finalized_projection_lifecycle.py
- tests/test_finalized_projection_no_review.py
- tests/test_finalized_projection_store.py
- tests/test_ingestion_run_api.py
- tests/test_input_boundary_api.py
- tests/test_match_decision_models.py


Planned Contract Tests

Contract tests must prove:

Match Detail retrieval by match_id works
response includes backend-owned evidence payload
response includes backend-owned traceability payload
match not found is distinguishable
missing evidence is distinguishable
unavailable evidence is distinguishable
malformed or incomplete payload is distinguishable
backend error is distinguishable
response shape is stable
frontend truth synthesis is not required
Planned Implementation Sequence

The next implementation Mini-EPIC should follow this order:

Inspect selected API/route file and confirm route convention.
Inspect selected model/DTO file and add Match Detail response DTO/read model.
Inspect selected service/adapter file and add Match Detail backend adapter.
Wire route to adapter without adding frontend assumptions.
Add contract tests for success path and failure semantics.
Run focused tests.
Update Mini-EPIC 33.13 closure only after implementation evidence exists.
Explicit Non-Actions

No Base44 prompt is created.

No live UI wiring is performed.

No Scenario 15 completion claim is made.

No Human Correction binding is implemented.

No Finalized Truth binding is implemented.

No Export Readiness binding is implemented.

No Intake Workspace binding is implemented.

No frontend truth synthesis is authorized.

Exit Criteria for the Next Implementation Step

The next implementation step may proceed only if it names exact files to modify and preserves the backend-owned truth boundary.

The implementation is acceptable only if the backend exposes Match Detail / Evidence as product-facing truth and tests prove frontend truth synthesis is not required.
