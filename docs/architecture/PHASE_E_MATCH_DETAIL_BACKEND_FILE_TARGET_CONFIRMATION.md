Phase E Match Detail Backend File Target Confirmation

Mini-EPIC: 33.13.D

Purpose

This document confirms the final corrected backend implementation file targets for the product-facing Match Detail / Evidence read path.

This is a target-confirmation boundary only.

This document does not implement backend behavior.

This document does not add an endpoint.

This document does not add a DTO/read model.

This document does not add an adapter/service implementation.

This document does not add contract tests.

This document does not authorize Base44 binding.

This document does not authorize live UI wiring.

This document does not claim Scenario 15 completion.

Final Correction Note

The earlier local 33.13.D target confirmations selected or retained unsafe target boundaries.

The first version incorrectly selected src/invomatch/api/actions.py as the route target.

The second version corrected the route target but still allowed src/invomatch/api/review_cases.py to act as both route and service/adapter target.

That is not acceptable because route/API boundary and service/adapter boundary must remain separate.

This final correction separates the route, service/adapter, DTO/product model, mapper, and contract-test responsibilities.

Starting State

Starting commit subject:

docs(epic-33): confirm match detail backend implementation targets

Local commit being amended:

fdfa05d

Prior discovery report:

docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_SOURCE_DISCOVERY.md

Prior implementation plan:

docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_IMPLEMENTATION_PLAN.md

Target Selection Principle

The implementation must modify exact backend files only after target confirmation.

The selected files must preserve the backend-owned truth boundary.

The selected files must support the path:

Review Queue -> stable match_id -> product-facing Match Detail retrieval -> backend-owned evidence payload -> backend-owned traceability payload -> explicit failure semantics -> UI-displayable response without frontend truth synthesis.

Final Confirmed Route / API Target

Selected API/route file:

src/invomatch/api/review_cases.py

Selection rationale:

Match Detail / Evidence retrieval is a review read-path concern, not an action execution concern.

The route target must be review-case aligned.

Required route intent:

GET /api/review/matches/{match_id}/detail

The exact route may be adapted only if existing backend API conventions require it.

The route must remain match_id-based.

The route must not require invoice_id/payment_id fallback.

The route must not require frontend truth reconstruction.

Explicitly rejected route target:

src/invomatch/api/actions.py

Rejection rationale:

actions.py is not the correct home for a product-facing Match Detail / Evidence read path. It risks mixing read-model retrieval with action execution boundaries.

Final Confirmed Service / Adapter Target

Selected service/adapter target:

src/invomatch/services/match_detail_read_service.py

Target mode:

new-companion-file-required

Selection rationale:

A separate backend service/adapter is required because route/API code must not become the owner of Match Detail truth assembly.

The service/adapter must own:

lookup by match_id
evidence mapping
traceability mapping
failure semantics mapping
response assembly
no frontend truth synthesis guarantee

Explicitly rejected service targets:

src/invomatch/api/review_cases.py
src/invomatch/api/product_models/review_case.py

Rejection rationale:

review_cases.py is the API route boundary, not the service/adapter boundary.

product_models/review_case.py is a DTO/product model file, not a backend service/adapter implementation file.

Final Confirmed DTO / Product Model Target

Selected DTO/product model file:

src/invomatch/api/product_models/review_case.py

Selection rationale:

This file is selected as the DTO/product model target for defining the product-facing Match Detail response shape because it is already review-case aligned.

The DTO/read model must support:

match_id
match status or posture
invoice summary
payment summary
backend-owned evidence payload
backend-owned traceability payload
backend-owned explanation if available
backend-owned confidence/score if available
audit-safe source references
Final Confirmed Mapper Companion Target

Selected mapper companion file:

src/invomatch/api/mappers/product_contract.py

Selection rationale:

This file may be used as a companion mapping target only if existing API conventions require product-contract mapping there.

The mapper may translate backend-owned data into the product-facing DTO.

The mapper must not create financial truth.

The mapper must not synthesize evidence.

The mapper must not synthesize traceability.

Final Confirmed Contract / API Test Target

Selected contract/API test target:

tests/contracts/test_match_detail_evidence_api.py

Target mode:

new-contract-test-file-required

Selection rationale:

A dedicated Match Detail / Evidence contract test is required because existing action-focused contract tests do not directly prove this read path.

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

Explicitly rejected primary test target:

tests/contracts/test_product_contract_actions.py

Rejection rationale:

test_product_contract_actions.py is action-focused and must not become the primary test home for a product-facing Match Detail / Evidence read path.

API / Route Candidate Review

Selected target:

src/invomatch/api/review_cases.py

Candidate set reviewed:

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


Service / Adapter Candidate Review

Selected target:

src/invomatch/services/match_detail_read_service.py

Target mode:

new-companion-file-required

Candidate set reviewed:

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
- src/invomatch/services/export/__init__.py
- src/invomatch/services/export/errors.py
- src/invomatch/services/export/export_service.py
- src/invomatch/services/export/finalized_projection.py
- src/invomatch/services/export/finalized_projection_store.py
- src/invomatch/services/export/finalized_projection_writer.py
- src/invomatch/services/export/finalized_result_reader.py
- src/invomatch/services/export/mapper.py
- src/invomatch/services/export/run_finalized_result_reader.py
- src/invomatch/services/export/serializers/__init__.py
- src/invomatch/services/export/serializers/csv_exporter.py
- src/invomatch/services/export/serializers/json_exporter.py
- src/invomatch/services/export/source_loader.py
- src/invomatch/services/export_delivery_service.py
- src/invomatch/services/feedback/__init__.py
- src/invomatch/services/feedback/feedback_capture.py
- src/invomatch/services/feedback/records.py
- src/invomatch/services/feedback/rule_recommendation.py
- src/invomatch/services/feedback/signal_extraction.py
- src/invomatch/services/feedback/sqlite_feedback_repository.py
- src/invomatch/services/feedback_store.py
- src/invomatch/services/ingestion.py
- src/invomatch/services/ingestion_run_integration/idempotency_policy.py
- src/invomatch/services/ingestion_run_integration/mapper.py
- src/invomatch/services/ingestion_run_integration/models.py
- src/invomatch/services/ingestion_run_integration/run_creation_policy.py
- src/invomatch/services/ingestion_run_integration/runtime_adapter.py
- src/invomatch/services/ingestion_run_integration/service.py
- src/invomatch/services/input_boundary/__init__.py
- src/invomatch/services/input_boundary/csv_input_mapper.py
- src/invomatch/services/input_boundary/csv_input_parser.py
- src/invomatch/services/input_boundary/file_decoder.py
- src/invomatch/services/input_boundary/file_input_service.py
- src/invomatch/services/input_boundary/file_validator.py
- src/invomatch/services/input_boundary/input_processing_service.py
- src/invomatch/services/input_boundary/json_input_service.py
- src/invomatch/services/input_boundary/repository.py
- src/invomatch/services/input_boundary/sqlite_repository.py
- src/invomatch/services/lifecycle/__init__.py
- src/invomatch/services/lifecycle/errors.py
- src/invomatch/services/lifecycle/guards.py
- src/invomatch/services/lifecycle/service.py
- src/invomatch/services/lifecycle/state_machine.py
- src/invomatch/services/match_record_store.py
- src/invomatch/services/matching/__init__.py
- src/invomatch/services/matching/decision_builder.py
- src/invomatch/services/matching/explanations.py
- src/invomatch/services/matching/features.py
- src/invomatch/services/matching/rules.py
- src/invomatch/services/matching_engine.py
- src/invomatch/services/operational/__init__.py
- src/invomatch/services/operational/alert_policy.py
- src/invomatch/services/operational/condition_detector.py
- src/invomatch/services/operational/operational_audit.py
- src/invomatch/services/operational/operational_metrics.py
- src/invomatch/services/operational/operational_scan_service.py
- src/invomatch/services/operational/operational_scheduler_service.py
- src/invomatch/services/operational/recovery_eligibility_policy.py
- src/invomatch/services/operational/recovery_loop_service.py
- src/invomatch/services/operational/retry_budget_policy.py
- src/invomatch/services/operational/stuck_run_policy.py
- src/invomatch/services/orchestration/export_readiness_evaluator.py
- src/invomatch/services/orchestration/review_case_factory.py
- src/invomatch/services/orchestration/review_case_generation_service.py
- src/invomatch/services/orchestration/review_integration_service.py
- src/invomatch/services/orchestration/review_requirement_evaluator.py


DTO / Product Model / Mapper Candidate Review

Selected DTO/product model target:

src/invomatch/api/product_models/review_case.py

Selected mapper companion target:

src/invomatch/api/mappers/product_contract.py
Contract / API Test Candidate Review

Selected target:

tests/contracts/test_match_detail_evidence_api.py

Target mode:

new-contract-test-file-required

Candidate set reviewed:

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
- tests/test_actions/test_dispatcher.py
- tests/test_actions/test_export_run.py
- tests/test_actions/test_resolve_review.py
- tests/test_actions/test_resolve_review_conflicts.py
- tests/test_actions_api.py
- tests/test_artifact_storage_contract.py
- tests/test_auth_session_api.py
- tests/test_export_api.py
- tests/test_export_artifact_api.py
- tests/test_export_artifact_repository_contract.py
- tests/test_finalized_projection_no_review.py
- tests/test_ingestion_run_api.py
- tests/test_input_boundary_api.py
- tests/test_match_decision_models.py
- tests/test_match_features.py
- tests/test_match_rules.py
- tests/test_match_taxonomy_and_explanations.py
- tests/test_matching_engine.py
- tests/test_product_flow_end_to_end.py
- tests/test_reconciliation_runs_api.py
- tests/test_restart_app_review_run_view_integrity.py
- tests/test_restart_review_persistence_integrity.py
- tests/test_review_api.py
- tests/test_review_case_factory.py
- tests/test_review_case_generation_service.py
- tests/test_review_integration_service.py
- tests/test_review_requirement_evaluator.py
- tests/test_review_resolution_coordinator.py
- tests/test_review_service.py
- tests/test_review_service_store_integration.py
- tests/test_run_store_contract.py
- tests/test_run_store_core_contract.py
- tests/test_run_view_api.py
- tests/test_run_view_contract.py
- tests/test_sqlite_review_store.py


Next Implementation Boundary

The next Mini-EPIC step may implement backend behavior only in the final confirmed target files or in narrowly justified companion files.

If implementation requires a different file, that deviation must be documented before commit.

The next implementation step must remain backend-side only.

The next implementation step must not create or modify Base44 prompts.

The next implementation step must not perform live UI wiring.

The next implementation step must not claim Scenario 15 completion.

Explicit Non-Actions

No endpoint was implemented.

No DTO/read model was implemented.

No adapter/service implementation was added.

No contract tests were added.

No Base44 prompt was created.

No live UI wiring was performed.

No Scenario 15 completion claim was made.

No frontend truth synthesis was authorized.
