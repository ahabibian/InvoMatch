from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from invomatch.domain.export import ExportFormat
from invomatch.domain.models import (
    MatchResult,
    ReconciliationReport,
    ReconciliationResult,
    ReconciliationRun,
)
from invomatch.domain.review.models import DecisionType
from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)
from invomatch.services.artifact_query_service import ArtifactQueryService
from invomatch.services.export import ExportService
from invomatch.services.export.finalized_projection import FinalizedResultProjection
from invomatch.services.export.finalized_projection_store import SqliteFinalizedProjectionStore
from invomatch.services.export.source_loader import ExportSourceLoader
from invomatch.services.export_delivery_service import ExportDeliveryService
from invomatch.services.orchestration.export_readiness_evaluator import (
    ExportReadinessEvaluator,
)
from invomatch.services.orchestration.review_resolution_coordinator import (
    ReviewResolutionCoordinator,
)
from invomatch.services.orchestration.run_orchestration_service import (
    RunOrchestrationService,
)
from invomatch.services.review_service import ReviewService
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import SqliteRunStore
from invomatch.services.run_view_query_service import RunViewQueryService
from invomatch.services.storage.local_storage import LocalArtifactStorage


"""
System Scenario 2 - Review Required -> Resolve -> Finalize

This scenario validates the review loop as a real system flow:
- run enters review_required
- review item is created
- export is blocked before review resolution
- reviewer resolves the review item
- run transitions to completed
- export becomes ready
- artifact generation succeeds
- run view reflects the final state
"""


@dataclass
class ReviewFlowSystemContext:
    run_store: SqliteRunStore
    review_store: InMemoryReviewStore
    review_service: ReviewService
    orchestration_service: RunOrchestrationService
    resolution_coordinator: ReviewResolutionCoordinator
    export_readiness_evaluator: ExportReadinessEvaluator
    export_delivery_service: ExportDeliveryService
    projection_store: SqliteFinalizedProjectionStore
    artifact_query_service: ArtifactQueryService
    run_view_query_service: RunViewQueryService
    tmp_path: Path


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _seed_processing_run(run_store: SqliteRunStore, tmp_path: Path) -> ReconciliationRun:
    now = _now()

    invoice_path = tmp_path / "review_flow_invoices.csv"
    payment_path = tmp_path / "review_flow_payments.csv"

    invoice_path.write_text(
        "\n".join(
            [
                "id,date,amount,currency,reference",
                "inv-1,2024-01-10,100.00,USD,INV-1",
            ]
        ) + "\n",
        encoding="utf-8",
    )

    payment_path.write_text(
        "\n".join(
            [
                "id,date,amount,currency,reference",
                "pay-1,2024-01-12,100.00,USD,Payment for INV-1",
            ]
        ) + "\n",
        encoding="utf-8",
    )

    run = ReconciliationRun(
        tenant_id="tenant-test",

        run_id="run-review-flow-001",
        status="processing",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=None,
        claimed_by="worker-system-test",
        claimed_at=now,
        lease_expires_at=now,
        attempt_count=1,
        invoice_csv_path=str(invoice_path),
        payment_csv_path=str(payment_path),
        error_message=None,
        report=ReconciliationReport(
            total_invoices=1,
            matched=0,
            unmatched=1,
            duplicate_detected=0,
            partial_match=0,
            results=[
                ReconciliationResult(
                    invoice_id="inv-1",
                    match_result=MatchResult(
                        status="unmatched",
                        payment_id=None,
                        payment_ids=None,
                        duplicate_payment_ids=None,
                        confidence_score=0.0,
                        confidence_explanation="no viable candidate",
                        mismatch_reasons=["no_viable_candidate"],
                    ),
                )
            ],
        ),
    )

    return run_store.create_run(run)


@pytest.fixture
def review_flow_system_context(tmp_path: Path) -> ReviewFlowSystemContext:
    run_store = SqliteRunStore(tmp_path / "runs.sqlite3")
    review_store = InMemoryReviewStore()
    review_service = ReviewService()

    seeded_run = _seed_processing_run(run_store, tmp_path)

    projection_store = SqliteFinalizedProjectionStore(tmp_path / "finalized_projections.sqlite3")

    orchestration_service = RunOrchestrationService(
        review_store=review_store,
        review_service=review_service,
        projection_store=projection_store,
    )

    resolution_coordinator = ReviewResolutionCoordinator(
        review_store=review_store,
        review_service=review_service,
        run_orchestration_service=orchestration_service,
    )

    export_service = ExportService(
        run_store=run_store,
        projection_store=projection_store,
    )

    export_root = tmp_path / "exports"
    export_root.mkdir(parents=True, exist_ok=True)

    export_repository = SqliteExportArtifactRepository(
        str(export_root / "export_artifacts.sqlite3")
    )
    export_storage = LocalArtifactStorage(export_root)

    def _export_generator(run_id: str, format: str, *, tenant_id: str | None = None) -> bytes:
        return export_service.export(
            tenant_id="tenant-test",

            run_id=run_id,
            export_format=ExportFormat(format),
        ).content

    export_delivery_service = ExportDeliveryService(
        repository=export_repository,
        storage=export_storage,
        export_generator=_export_generator,
    )

    artifact_query_service = ArtifactQueryService(
        repository=export_repository,
        storage=export_storage,
    )

    export_readiness_evaluator = ExportReadinessEvaluator(
        run_store=run_store,
        review_store=review_store,
        review_service=review_service,
        projection_store=projection_store,
    )

    run_view_query_service = RunViewQueryService(
        run_store=run_store,
        review_store=review_store,
        artifact_query_service=artifact_query_service,
        export_readiness_evaluator=export_readiness_evaluator,
    )

    return ReviewFlowSystemContext(
        run_store=run_store,
        review_store=review_store,
        review_service=review_service,
        orchestration_service=orchestration_service,
        resolution_coordinator=resolution_coordinator,
        export_readiness_evaluator=export_readiness_evaluator,
        export_delivery_service=export_delivery_service,
        projection_store=projection_store,
        artifact_query_service=artifact_query_service,
        run_view_query_service=run_view_query_service,
        tmp_path=tmp_path,
    )


def test_review_resolution_flow(review_flow_system_context: ReviewFlowSystemContext) -> None:
    run_id = "run-review-flow-001"

    post_match_result, persisted_after_match = (
        review_flow_system_context.orchestration_service.orchestrate_and_persist_post_matching(
            tenant_id="tenant-test",

            run_id=run_id,
            reconciliation_outcomes=[
                {"invoice_id": "inv-1", "status": "unmatched", "reason": "no_match"},
            ],
            run_store=review_flow_system_context.run_store,
        )
    )

    assert post_match_result.run_status == "review_required"
    assert persisted_after_match.status == "review_required"
    assert len(post_match_result.review_cases) == 1
    assert post_match_result.review_cases[0]["invoice_id"] == "inv-1"

    review_items = review_flow_system_context.review_store.list_review_items()
    assert len(review_items) == 1, f"expected one review item, got {len(review_items)}"

    review_item = review_items[0]
    feedback = review_flow_system_context.review_store.get_feedback(review_item.feedback_id)
    assert feedback is not None, "expected feedback record for review item"
    assert feedback.run_id == run_id

    export_before_resolution = review_flow_system_context.export_readiness_evaluator.evaluate(run_id)
    assert export_before_resolution.is_export_ready is False
    assert export_before_resolution.reason == "run_status_not_completed:review_required"

    resolution_result, persisted_after_resolution = (
        review_flow_system_context.resolution_coordinator.resolve_and_reconcile(
            tenant_id="tenant-test",

            run_id=run_id,
            review_item_id=review_item.review_item_id,
            feedback_id=feedback.feedback_id,
            reviewer_id="reviewer-system-test",
            decision=DecisionType.APPROVE,
            reason="approved in Scenario 2 system test",
            run_store=review_flow_system_context.run_store,
        )
    )

    assert resolution_result.review_item.item_status.value == "APPROVED"

    export_after_resolution = review_flow_system_context.export_readiness_evaluator.evaluate(run_id)
    assert export_after_resolution.is_export_ready is True
    assert export_after_resolution.reason == "export_allowed"

    preexisting_artifacts = review_flow_system_context.artifact_query_service.list_artifacts_for_run(
        run_id
    )
    assert preexisting_artifacts == [], "expected no artifacts before explicit export generation"

    artifact = review_flow_system_context.export_delivery_service.create_export_artifact(
        run_id,
        "json",
    )

    assert artifact.run_id == run_id
    assert artifact.format == "json"
    assert artifact.byte_size is not None and artifact.byte_size > 0

    artifacts = review_flow_system_context.artifact_query_service.list_artifacts_for_run(run_id)
    assert len(artifacts) == 1
    assert artifacts[0].id == artifact.id

    run_view = review_flow_system_context.run_view_query_service.get_run_view(run_id)
    assert run_view is not None
    assert run_view.run_id == run_id
    assert run_view.status == "completed"
    assert run_view.review_summary.total_items == 1
    assert run_view.review_summary.open_items == 0
    assert run_view.review_summary.resolved_items == 1
    assert run_view.export_summary.status == "exported"
    assert len(run_view.artifacts) == 1




