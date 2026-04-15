from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from invomatch.services.artifact_query_service import ArtifactQueryService
from invomatch.services.export_delivery_service import ExportDeliveryService
from invomatch.services.orchestration.export_readiness_evaluator import (
    ExportReadinessEvaluator,
)
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.reconciliation_errors import ReconciliationExecutionError
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import SqliteRunStore
from invomatch.services.run_view_query_service import RunViewQueryService
from invomatch.services.storage.local_storage import LocalArtifactStorage
from invomatch.repositories.export_artifact_repository_sqlite import (
    SqliteExportArtifactRepository,
)
from invomatch.runtime.runtime_executor import RuntimeExecutor
from invomatch.runtime.runtime_policy import RuntimeRetryPolicy


"""
System Scenario 4 - Runtime Failure -> Safe Failed State

This scenario validates that a runtime failure terminalizes safely:
- execution fails after retry exhaustion
- run becomes failed
- structured error is persisted
- report is not persisted falsely
- export readiness remains blocked
- run view exposes failure correctly
- no artifact is generated
"""


class _AlwaysFailingMatchRecordStore:
    def save_many(self, records):
        raise RuntimeError("match record persistence unavailable")


@dataclass
class RuntimeFailureSystemContext:
    run_store: SqliteRunStore
    review_store: InMemoryReviewStore
    export_readiness_evaluator: ExportReadinessEvaluator
    artifact_query_service: ArtifactQueryService
    run_view_query_service: RunViewQueryService
    runtime_executor: RuntimeExecutor
    tmp_path: Path


@pytest.fixture
def runtime_failure_system_context(tmp_path: Path) -> RuntimeFailureSystemContext:
    run_store = SqliteRunStore(tmp_path / "runs.sqlite3")
    review_store = InMemoryReviewStore()

    export_root = tmp_path / "exports"
    export_root.mkdir(parents=True, exist_ok=True)

    export_repository = SqliteExportArtifactRepository(
        str(export_root / "export_artifacts.sqlite3")
    )
    export_storage = LocalArtifactStorage(export_root)

    artifact_query_service = ArtifactQueryService(
        repository=export_repository,
        storage=export_storage,
    )

    export_readiness_evaluator = ExportReadinessEvaluator(
        run_store=run_store,
        review_store=review_store,
    )

    run_view_query_service = RunViewQueryService(
        run_store=run_store,
        review_store=review_store,
        artifact_query_service=artifact_query_service,
        export_readiness_evaluator=export_readiness_evaluator,
    )

    runtime_executor = RuntimeExecutor(
        retry_policy=RuntimeRetryPolicy(max_attempts=2)
    )

    return RuntimeFailureSystemContext(
        run_store=run_store,
        review_store=review_store,
        export_readiness_evaluator=export_readiness_evaluator,
        artifact_query_service=artifact_query_service,
        run_view_query_service=run_view_query_service,
        runtime_executor=runtime_executor,
        tmp_path=tmp_path,
    )


def test_runtime_failure_terminalizes_safely(
    runtime_failure_system_context: RuntimeFailureSystemContext,
) -> None:
    invoice_path = runtime_failure_system_context.tmp_path / "invoices.csv"
    payment_path = runtime_failure_system_context.tmp_path / "payments.csv"

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
                "invoice_id,id,date,amount,currency,reference",
                "inv-1,pay-1,2024-01-12,100.00,USD,Payment for INV-1",
            ]
        ) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ReconciliationExecutionError, match="Reconciliation execution failed"):
        reconcile_and_save(
            invoice_path,
            payment_path,
            run_store=runtime_failure_system_context.run_store,
            match_record_store=_AlwaysFailingMatchRecordStore(),
            runtime_executor=runtime_failure_system_context.runtime_executor,
        )

    runs, total = runtime_failure_system_context.run_store.list_runs()
    assert total == 1, f"expected one failed run, got total={total}"

    failed_run = runs[0]
    assert failed_run.status == "failed"
    assert failed_run.started_at is not None
    assert failed_run.finished_at is not None
    assert failed_run.report is None, "failed run must not persist a false report"

    assert failed_run.error is not None, "expected structured error on failed run"
    assert failed_run.error.code == "retry_exhausted"
    assert failed_run.error.message == "retry limit reached for operation: reconcile_and_save"
    assert failed_run.error.retryable is False
    assert failed_run.error.terminal is True

    assert failed_run.error_message is not None
    assert "retry_exhausted" in failed_run.error_message

    export_readiness = runtime_failure_system_context.export_readiness_evaluator.evaluate(
        failed_run.run_id
    )
    assert export_readiness.is_export_ready is False
    assert export_readiness.reason == "run_status_not_completed:failed"

    artifacts = runtime_failure_system_context.artifact_query_service.list_artifacts_for_run(
        failed_run.run_id
    )
    assert artifacts == [], f"expected no artifacts for failed run, got {artifacts}"

    run_view = runtime_failure_system_context.run_view_query_service.get_run_view(
        failed_run.run_id
    )
    assert run_view is not None
    assert run_view.run_id == failed_run.run_id
    assert run_view.status == "failed"
    assert run_view.error is not None
    assert run_view.error.code == "retry_exhausted"
    assert run_view.error.terminal is True
    assert run_view.export_summary.status == "not_ready"
    assert run_view.artifacts == []