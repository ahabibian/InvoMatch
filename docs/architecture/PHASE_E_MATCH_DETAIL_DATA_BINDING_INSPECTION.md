
Phase E Match Detail Data Binding Inspection

Mini-EPIC: 33.13.H

Purpose

This document inspects the backend data-binding path required after Mini-EPIC 33.13.G.

The backend Match Detail / Evidence contract exists, but the route is not yet real-data-bound.

This inspection does not change endpoint behavior.

This inspection does not implement data binding.

This inspection does not authorize Base44 binding.

This inspection does not authorize live UI wiring.

This inspection does not claim Scenario 15 completion.

Starting State

Starting commit subject:

docs(epic-33): audit match detail backend contract readiness

Starting HEAD:

9e12356c65c8d6ecb898ae786f2e3ef100c97fc0

Prior Readiness Decision

Mini-EPIC 33.13.G concluded:

Decision: Backend contract exists, but real-data binding is not yet ready.

The current route delegates using:

read_match_detail_by_id(match_id=match_id, matches=[])

Therefore the next step must inspect backend review/match/projection data sources before implementation.

Inspected Files
src/invomatch/api/review_cases.py
src/invomatch/services/match_detail_read_service.py
src/invomatch/api/product_models/review_case.py
src/invomatch/api/mappers/product_contract.py
src/invomatch/services/review_queries.py
tests/contracts/test_match_detail_evidence_api.py
docs/architecture/PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md
Route Signals

- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:3 — from fastapi import APIRouter, HTTPException, Request
- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:6 — read_match_detail_by_id,
- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:15 — from invomatch.services.review_queries import ReviewQueryService
- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:22 — def get_reconciliation_run_review(run_id: str, request: Request) -> ProductReviewCase:
- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:23 — require_permission(request, permission=Permission.RUNS_READ_REVIEW)
- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:25 — review_store = getattr(request.app.state, "review_store", None)
- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:26 — if review_store is None:
- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:29 — query_service = ReviewQueryService(review_store=review_store)
- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:39 — "/api/review/matches/{match_id}/detail",
- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:42 — def get_match_detail_evidence(match_id: str) -> ProductMatchDetailResponse:
- C:\dev\InvoMatch\src\invomatch\api\review_cases.py:46 — return read_match_detail_by_id(match_id=match_id, matches=[])


Service Signals

- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:1 — """Backend-owned Match Detail / Evidence read service."""
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:9 — ProductMatchDetailEvidenceItem,
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:10 — ProductMatchDetailFailure,
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:11 — ProductMatchDetailResponse,
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:12 — ProductMatchDetailTraceability,
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:17 — MATCH_NOT_FOUND = "match_not_found"
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:18 — MISSING_EVIDENCE = "missing_evidence"
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:19 — UNAVAILABLE_EVIDENCE = "unavailable_evidence"
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:20 — MALFORMED_PAYLOAD = "malformed_or_incomplete_payload"
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:34 — def to_failure(self) -> ProductMatchDetailFailure:
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:35 — return ProductMatchDetailFailure(
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:53 — def build_match_detail_response(match: Any) -> ProductMatchDetailResponse:
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:56 — match_id = _as_string(_get_attr(match, "match_id", None))
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:57 — if not match_id:
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:58 — match_id = _as_string(_get_attr(match, "id", None))
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:60 — if not match_id:
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:62 — MatchDetailFailureCode.MALFORMED_PAYLOAD,
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:63 — "Match detail payload is missing match_id.",
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:70 — return ProductMatchDetailResponse(
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:71 — match_id=match_id,
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:75 — evidence=[
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:76 — ProductMatchDetailEvidenceItem(
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:77 — evidence_id=match_id + ":status",
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:78 — evidence_type="match_status",
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:84 — traceability=ProductMatchDetailTraceability(
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:96 — def read_match_detail_by_id(
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:98 — match_id: str,
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:99 — matches: Iterable[Any] | None = None,
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:100 — ) -> ProductMatchDetailResponse:
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:101 — """Retrieve product-facing Match Detail by stable backend-owned match_id."""
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:103 — if not match_id:
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:105 — MatchDetailFailureCode.MALFORMED_PAYLOAD,
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:106 — "match_id is required.",
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:109 — for match in matches or []:
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:110 — candidate = _as_string(_get_attr(match, "match_id", None))
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:114 — if candidate == match_id:
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:115 — return build_match_detail_response(match)
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:118 — MatchDetailFailureCode.MATCH_NOT_FOUND,
- C:\dev\InvoMatch\src\invomatch\services\match_detail_read_service.py:119 — "Match detail was not found for the provided match_id.",


DTO / Product Model Signals

- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:10 — class ProductReviewQueueItem(BaseModel):
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:26 — class ProductReviewCase(BaseModel):
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:36 — match_id: Optional[str] = Field(
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:49 — class ProductMatchDetailEvidenceItem(BaseModel):
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:50 — """Backend-owned display-safe evidence item for Match Detail."""
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:52 — evidence_id: str = Field(
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:54 — description="Backend-owned evidence identifier.",
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:56 — evidence_type: str = Field(
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:58 — description="Backend-owned evidence type.",
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:62 — description="Human-readable backend-owned evidence label.",
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:66 — description="Display-safe backend-owned evidence value.",
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:70 — description="Backend-owned evidence source reference if available.",
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:74 — class ProductMatchDetailTraceability(BaseModel):
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:75 — """Backend-owned audit-safe traceability payload for Match Detail."""
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:95 — class ProductMatchDetailFailure(BaseModel):
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:96 — """Product-facing backend-owned failure semantics for Match Detail."""
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:100 — description="Stable backend-owned failure code.",
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:104 — description="Display-safe backend-owned failure message.",
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:108 — class ProductMatchDetailResponse(BaseModel):
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:109 — """Product-facing Match Detail / Evidence response owned by the backend."""
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:111 — match_id: str = Field(
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:127 — evidence: list[ProductMatchDetailEvidenceItem] = Field(
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:129 — description="Backend-owned evidence payload.",
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:131 — traceability: ProductMatchDetailTraceability = Field(
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:132 — default_factory=ProductMatchDetailTraceability,
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:133 — description="Backend-owned traceability payload.",
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:143 — failure: ProductMatchDetailFailure | None = Field(
- C:\dev\InvoMatch\src\invomatch\api\product_models\review_case.py:145 — description="Backend-owned failure semantics when detail is not available.",


Product Mapper Signals

- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:18 — from invomatch.api.product_models.match_result import ProductMatchResult
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:19 — from invomatch.api.product_models.review_case import ProductReviewCase
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:142 — def to_product_match_result(match: Any) -> ProductMatchResult:
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:143 — return ProductMatchResult(
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:144 — match_id=str(getattr(match, "match_id", getattr(match, "id", ""))),
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:153 — def to_product_review_case(projection: Any) -> ProductReviewCase:
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:154 — return ProductReviewCase(
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:155 — case_id=str(projection.case_id),
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:156 — run_id=str(projection.run_id),
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:157 — status=str(projection.status),
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:158 — reason_code=str(projection.reason_code),
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:159 — match_id=getattr(projection, "match_id", None),
- C:\dev\InvoMatch\src\invomatch\api\mappers\product_contract.py:161 — recommended_action=getattr(projection, "recommended_action", None),


Review Query Service Signals

- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:8 — class ReviewCaseProjection:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:10 — run_id: str
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:13 — match_id: Optional[str] = None
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:17 — def _normalize_review_status(item_status: str) -> str:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:20 — if normalized in {"PENDING", "IN_REVIEW", "DEFERRED"}:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:32 — def _extract_reason_code(feedback: Any) -> str:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:35 — for key in ("reason_code", "primary_mismatch_code", "review_reason"):
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:39 — return "manual_review"
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:42 — def _extract_match_id(feedback: Any) -> Optional[str]:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:45 — for key in ("match_id", "candidate_match_id"):
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:52 — def _extract_recommended_action(review_item: Any) -> Optional[str]:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:53 — decision = getattr(review_item, "current_decision", None)
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:59 — class ReviewQueryService:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:61 — Query-side boundary for assembling product-facing review cases.
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:63 — Current implementation depends on a review store that exposes:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:64 — - list_review_items()
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:68 — review store. SQLite-backed review query coverage can be added later.
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:71 — def __init__(self, review_store: Any) -> None:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:72 — self._review_store = review_store
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:74 — def get_review_case_for_run(self, run_id: str) -> Optional[ReviewCaseProjection]:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:75 — list_review_items = getattr(self._review_store, "list_review_items", None)
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:76 — get_feedback = getattr(self._review_store, "get_feedback", None)
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:78 — if list_review_items is None or get_feedback is None:
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:81 — for review_item in list_review_items():
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:82 — feedback = get_feedback(review_item.feedback_id)
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:86 — if str(getattr(feedback, "run_id", "")) != str(run_id):
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:89 — return ReviewCaseProjection(
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:90 — case_id=str(review_item.review_item_id),
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:91 — run_id=str(run_id),
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:92 — status=_normalize_review_status(str(review_item.item_status)),
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:94 — match_id=_extract_match_id(feedback),
- C:\dev\InvoMatch\src\invomatch\services\review_queries.py:95 — recommended_action=_extract_recommended_action(review_item),


Contract Test Signals

- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:2 — from fastapi.testclient import TestClient
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:16 — def _client() -> TestClient:
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:18 — app.include_router(review_cases.router)
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:19 — return TestClient(app)
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:22 — def test_match_detail_retrieval_by_match_id_exposes_backend_owned_payload(monkeypatch):
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:23 — def fake_read_match_detail_by_id(*, match_id, matches=None):
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:24 — assert match_id == "match-123"
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:26 — match_id="match-123",
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:49 — monkeypatch.setattr(
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:51 — "read_match_detail_by_id",
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:52 — fake_read_match_detail_by_id,
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:55 — response = _client().get("/api/review/matches/match-123/detail")
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:59 — assert payload["match_id"] == "match-123"
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:67 — def test_match_detail_not_found_uses_backend_owned_failure_semantics(monkeypatch):
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:68 — def fake_read_match_detail_by_id(*, match_id, matches=None):
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:71 — "Match detail was not found for the provided match_id.",
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:74 — monkeypatch.setattr(
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:76 — "read_match_detail_by_id",
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:77 — fake_read_match_detail_by_id,
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:80 — response = _client().get("/api/review/matches/missing-match/detail")
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:88 — def test_match_detail_malformed_payload_is_distinguishable(monkeypatch):
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:89 — def fake_read_match_detail_by_id(*, match_id, matches=None):
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:92 — "Match detail payload is missing match_id.",
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:95 — monkeypatch.setattr(
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:97 — "read_match_detail_by_id",
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:98 — fake_read_match_detail_by_id,
- C:\dev\InvoMatch\tests\contracts\test_match_detail_evidence_api.py:101 — response = _client().get("/api/review/matches/malformed/detail")


Readiness Audit Signals

- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:67 — read_match_detail_by_id(match_id=match_id, matches=[])
- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:88 — review queue match_id to match detail data binding
- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:94 — Base44 binding remains blocked.
- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:96 — Scenario 15 completion remains blocked.
- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:98 — The backend contract implementation is not yet real-data-bound.
- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:102 — No UI layer may treat this endpoint as pilot-ready until backend data binding is implemented and tested.
- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:106 — The next Mini-EPIC must be backend data binding, not UI work.
- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:110 — Mini-EPIC 33.13.H — Match Detail / Evidence Backend Data Binding
- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:112 — The next step must bind the route/service to real backend match/review/projection data and prove that a match_id exposed by Review Queue can retrieve the corresponding backend-owned Match Detail / Evidence response.
- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:118 — Review Queue exposes stable match_id.
- C:\dev\InvoMatch\docs\architecture\PHASE_E_MATCH_DETAIL_BACKEND_CONTRACT_READINESS_AUDIT.md:127 — at least one integration-style test proves review queue -> match detail continuity.


Related Backend Files Reviewed For Binding Candidates

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
- src/invomatch/bootstrap/__init__.py
- src/invomatch/bootstrap/app_factory.py
- src/invomatch/bootstrap/persistence_factory.py
- src/invomatch/bootstrap/runtime_factory.py
- src/invomatch/bootstrap/storage_factory.py
- src/invomatch/bootstrap/validation_factory.py
- src/invomatch/config/__init__.py
- src/invomatch/config/defaults.py
- src/invomatch/config/environment.py
- src/invomatch/config/loaders.py
- src/invomatch/config/models.py
- src/invomatch/config/settings.py
- src/invomatch/config/validation.py
- src/invomatch/domain/audit/__init__.py
- src/invomatch/domain/audit/models.py
- src/invomatch/domain/audit/repository.py
- src/invomatch/domain/export/__init__.py
- src/invomatch/domain/export/models.py
- src/invomatch/domain/export_delivery/__init__.py
- src/invomatch/domain/export_delivery/models.py
- src/invomatch/domain/export_delivery/repository.py
- src/invomatch/domain/feedback/__init__.py
- src/invomatch/domain/feedback/enums.py
- src/invomatch/domain/feedback/models.py
- src/invomatch/domain/feedback/repositories.py
- src/invomatch/domain/input_boundary/__init__.py
- src/invomatch/domain/input_boundary/models.py
- src/invomatch/domain/match_record.py
- src/invomatch/domain/matching/__init__.py
- src/invomatch/domain/matching/decisioning.py
- src/invomatch/domain/matching/features.py
- src/invomatch/domain/matching/models.py
- src/invomatch/domain/matching/rules.py
- src/invomatch/domain/matching/taxonomy.py
- src/invomatch/domain/models.py
- src/invomatch/domain/operational/__init__.py
- src/invomatch/domain/operational/models.py
- src/invomatch/domain/release_identity.py
- src/invomatch/domain/review/models.py
- src/invomatch/domain/run_lifecycle.py
- src/invomatch/domain/security/__init__.py
- src/invomatch/domain/security/permission.py
- src/invomatch/domain/security/principal.py
- src/invomatch/domain/security/role.py
- src/invomatch/domain/security/user_status.py
- src/invomatch/domain/strategy.py
- src/invomatch/domain/tenant/__init__.py
- src/invomatch/domain/tenant/models.py
- src/invomatch/ingestion/__init__.py
- src/invomatch/ingestion/models/__init__.py
- src/invomatch/ingestion/models/duplicate_models.py
- src/invomatch/ingestion/models/ingestion_record.py
- src/invomatch/ingestion/models/ingestion_result.py
- src/invomatch/ingestion/models/normalized_models.py
- src/invomatch/ingestion/models/persisted_ingestion_outcome.py
- src/invomatch/ingestion/models/raw_models.py
- src/invomatch/ingestion/models/traceability_models.py
- src/invomatch/ingestion/models/validation_models.py
- src/invomatch/ingestion/normalizers/__init__.py
- src/invomatch/ingestion/normalizers/amount_normalizer.py
- src/invomatch/ingestion/normalizers/currency_normalizer.py
- src/invomatch/ingestion/normalizers/date_normalizer.py
- src/invomatch/ingestion/normalizers/identifier_normalizer.py
- src/invomatch/ingestion/normalizers/string_normalizer.py
- src/invomatch/ingestion/repositories/__init__.py
- src/invomatch/ingestion/repositories/in_memory_ingestion_repository.py
- src/invomatch/ingestion/repositories/ingestion_repository.py
- src/invomatch/ingestion/services/__init__.py
- src/invomatch/ingestion/services/decision_builder.py
- src/invomatch/ingestion/services/duplicate_classifier.py
- src/invomatch/ingestion/services/invoice_ingestion_gateway.py
- src/invomatch/ingestion/services/invoice_ingestion_service.py
- src/invomatch/ingestion/services/payment_ingestion_gateway.py
- src/invomatch/ingestion/services/payment_ingestion_service.py
- src/invomatch/ingestion/utils/__init__.py
- src/invomatch/ingestion/utils/fingerprint.py
- src/invomatch/ingestion/utils/identity_keys.py
- src/invomatch/ingestion/utils/semantic_keys.py
- src/invomatch/ingestion/validators/__init__.py
- src/invomatch/ingestion/validators/invoice_validator.py
- src/invomatch/ingestion/validators/payment_validator.py
- src/invomatch/main.py
- src/invomatch/persistence/base.py
- src/invomatch/persistence/postgres/run_store.py
- src/invomatch/persistence/postgres/schema.py
- src/invomatch/persistence/sqlite/run_store.py
- src/invomatch/persistence/sqlite/schema.py
- src/invomatch/repositories/audit_event_repository_sqlite.py
- src/invomatch/repositories/export_artifact_repository_sqlite.py
- src/invomatch/runtime/__init__.py
- src/invomatch/runtime/runtime_executor.py
- src/invomatch/runtime/runtime_failure.py
- src/invomatch/runtime/runtime_policy.py


Inspection Questions To Resolve In Next Step

The next implementation step must answer these questions through code, not assumption:

Which backend object owns the canonical match_id used by Review Queue?
Which backend object can be looked up by that match_id?
Does review_store expose enough data for Match Detail, or is another read model required?
Does ReviewQueryService already expose match-level data, or only run-level review case data?
Where should evidence be sourced from?
Where should traceability be sourced from?
Should the route pass request/app state into a query service instead of passing matches=[]?
What integration-style test can prove Review Queue -> match_id -> Match Detail continuity?
Data-Binding Decision Boundary

33.13.H is inspection only.

The next implementation Mini-EPIC must be a bounded backend data-binding patch.

It must replace matches=[] with a backend-owned real or test-backed data source.

It must not move truth assembly into the frontend.

It must not use Base44 to compensate for missing backend data.

It must not claim Scenario 15 readiness.

Recommended Next Mini-EPIC

Mini-EPIC 33.13.I — Match Detail / Evidence Backend Data Binding Patch

Required Acceptance Criteria For 33.13.I

The next implementation step must prove:

Review Queue exposes stable match_id.
The same match_id is accepted by GET /api/review/matches/{match_id}/detail.
The endpoint returns a backend-owned Match Detail response for real or test-backed backend data.
The endpoint returns backend-owned evidence.
The endpoint returns backend-owned traceability.
match_not_found remains distinguishable.
malformed_or_incomplete_payload remains distinguishable.
frontend truth synthesis is not required.
focused contract tests pass.
at least one integration-style test proves Review Queue -> match_id -> Match Detail continuity.
Explicit Non-Actions

No endpoint behavior was changed.

No data binding implementation was performed.

No Base44 prompt was created.

No live UI wiring was performed.

No Scenario 15 completion claim was made.

No frontend truth synthesis was authorized.
