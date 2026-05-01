from datetime import datetime, timezone

import pytest

from invomatch.domain.models import MatchResult, ReconciliationReport, ReconciliationResult, ReconciliationRun
from invomatch.services.completed_run_projection_service import (
    CompletedRunProjectionIntegrityError,
)
from invomatch.services.orchestration.run_orchestration_service import (
    RunOrchestrationService,
)
from invomatch.services.review_store import InMemoryReviewStore
from invomatch.services.run_store import InMemoryRunStore


class _ReadableExistingProjectionStore:
    def exists(self, *, tenant_id: str, run_id: str) -> bool:
        return True

    def get_results(self, *, tenant_id: str, run_id: str):
        return [object()]

    def save_results(self, **kwargs) -> None:
        raise AssertionError("save_results should not be called when projection already exists")

class _FailingProjectionSaveStore:
    def exists(self, *, tenant_id: str, run_id: str) -> bool:
        return False

    def get_results(self, *, tenant_id: str, run_id: str):
        raise AssertionError("get_results should not be called after save failure")

    def save_results(self, **kwargs) -> None:
        raise RuntimeError("projection persistence unavailable")


class _UnreadableAfterSaveProjectionStore:
    def exists(self, *, tenant_id: str, run_id: str) -> bool:
        return False

    def get_results(self, *, tenant_id: str, run_id: str):
        return None

    def save_results(self, **kwargs) -> None:
        return None


def _with_matched_projection_sources(run: ReconciliationRun, tmp_path) -> ReconciliationRun:
    invoice = tmp_path / f"{run.run_id}_invoices.csv"
    payment = tmp_path / f"{run.run_id}_payments.csv"

    invoice.write_text(
        "id,date,amount,currency,reference\n"
        "inv-1,2024-01-10,100.00,USD,INV-1\n",
        encoding="utf-8",
    )

    payment.write_text(
        "id,date,amount,currency,reference,invoice_id\n"
        "pay-1,2024-01-12,100.00,USD,INV-1,inv-1\n",
        encoding="utf-8",
    )

    report = ReconciliationReport(
        total_invoices=1,
        matched=1,
        duplicate_detected=0,
        partial_match=0,
        unmatched=0,
        results=[
            ReconciliationResult(
                invoice_id="inv-1",
                match_result=MatchResult(
                    status="matched",
                    payment_id="pay-1",
                    payment_ids=[],
                    duplicate_payment_ids=None,
                    confidence_score=1.0,
                    confidence_explanation="matched for projection integrity test",
                    mismatch_reasons=[],
                ),
            )
        ],
    )

    return run.model_copy(
        update={
            "invoice_csv_path": str(invoice),
            "payment_csv_path": str(payment),
            "report": report,
        }
    )


def _processing_run(run_id: str) -> ReconciliationRun:
    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        run_id=run_id,
            tenant_id="tenant-test",
        status="processing",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=None,
        claimed_by="worker-1",
        claimed_at=now,
        lease_expires_at=now,
        attempt_count=1,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error_message=None,
        report=None,
    )


def _review_required_run(run_id: str) -> ReconciliationRun:
    now = datetime.now(timezone.utc)
    return ReconciliationRun(
        run_id=run_id,
            tenant_id="tenant-test",
        status="review_required",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=now,
        finished_at=None,
        claimed_by="worker-1",
        claimed_at=now,
        lease_expires_at=now,
        attempt_count=1,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error_message=None,
        report=None,
    )


def test_orchestrate_and_persist_post_matching_moves_run_to_review_required():
    run = _processing_run("run_review_required")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    outcomes = [
        {"invoice_id": "INV-001", "status": "unmatched", "reason": "no_match"},
    ]

    result, persisted_run = service.orchestrate_and_persist_post_matching(
        run_id=run.run_id,
        reconciliation_outcomes=outcomes,
        run_store=run_store,
    )

    assert result.run_status == "review_required"
    assert persisted_run.status == "review_required"
    assert len(result.review_cases) == 1


def test_orchestrate_and_persist_post_matching_moves_run_to_completed():
    run = _processing_run("run_completed")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(
        review_store=review_store,
        projection_store=_ReadableExistingProjectionStore(),
    )

    outcomes = [
        {"invoice_id": "INV-010", "status": "finalizable"},
    ]

    result, persisted_run = service.orchestrate_and_persist_post_matching(
        run_id=run.run_id,
        reconciliation_outcomes=outcomes,
        run_store=run_store,
    )

    assert result.run_status == "completed"
    assert persisted_run.status == "completed"
    assert result.review_cases == []


def test_orchestrate_and_persist_post_matching_fails_for_invalid_run_transition():
    now = datetime.now(timezone.utc)
    run = ReconciliationRun(
        run_id="run_invalid_transition",
            tenant_id="tenant-test",
        status="queued",
        version=0,
        created_at=now,
        updated_at=now,
        started_at=None,
        finished_at=None,
        claimed_by=None,
        claimed_at=None,
        lease_expires_at=None,
        attempt_count=0,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error_message=None,
        report=None,
    )

    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    outcomes = [
        {"invoice_id": "INV-020", "status": "finalizable"},
    ]

    with pytest.raises(ValueError):
        service.orchestrate_and_persist_post_matching(
            run_id=run.run_id,
            reconciliation_outcomes=outcomes,
            run_store=run_store,
        )


def test_orchestrate_and_persist_post_review_resolution_moves_run_to_completed():
    run = _review_required_run("run_resolved_completed")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(
        review_store=review_store,
        projection_store=_ReadableExistingProjectionStore(),
    )

    result, persisted_run = service.orchestrate_and_persist_post_review_resolution(
        run_id=run.run_id,
        matching_completed=True,
        run_store=run_store,
    )

    assert result.run_status == "completed"
    assert persisted_run.status == "completed"
    assert result.review_cases == []


def test_orchestrate_and_persist_post_review_resolution_keeps_run_in_review_required_when_blockers_exist():
    run = _review_required_run("run_still_blocked")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    service.orchestrate_post_matching(
        run_id=run.run_id,
        reconciliation_outcomes=[
            {"invoice_id": "INV-030", "status": "unmatched", "reason": "no_match"},
        ],
    )

    result, persisted_run = service.orchestrate_and_persist_post_review_resolution(
        run_id=run.run_id,
        matching_completed=True,
        run_store=run_store,
    )

    assert result.run_status == "review_required"
    assert persisted_run.status == "review_required"
    assert len(result.review_cases) == 1


def test_orchestrate_and_persist_post_review_resolution_fails_for_invalid_run_transition():
    run = _processing_run("run_invalid_review_resolution")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    with pytest.raises(ValueError):
        service.orchestrate_and_persist_post_review_resolution(
            run_id=run.run_id,
            matching_completed=True,
            run_store=run_store,
        )

def test_orchestrate_and_persist_post_matching_blocks_completed_without_projection_store():
    run = _processing_run("run_completed_without_projection_store")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    with pytest.raises(
        CompletedRunProjectionIntegrityError,
        match="requires finalized projection store before completion",
    ):
        service.orchestrate_and_persist_post_matching(
            run_id=run.run_id,
            reconciliation_outcomes=[
                {"invoice_id": "INV-040", "status": "finalizable"},
            ],
            run_store=run_store,
        )

    persisted_run = run_store.get_run(run.run_id, tenant_id="tenant-test")
    assert persisted_run is not None
    assert persisted_run.status == "processing"


def test_orchestrate_and_persist_post_review_resolution_blocks_completed_without_projection_store():
    run = _review_required_run("run_review_completed_without_projection_store")
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(review_store=review_store)

    with pytest.raises(
        CompletedRunProjectionIntegrityError,
        match="requires finalized projection store before completion",
    ):
        service.orchestrate_and_persist_post_review_resolution(
            run_id=run.run_id,
            matching_completed=True,
            run_store=run_store,
        )

    persisted_run = run_store.get_run(run.run_id, tenant_id="tenant-test")
    assert persisted_run is not None
    assert persisted_run.status == "review_required"

def test_orchestrate_and_persist_post_matching_does_not_complete_when_projection_save_fails(tmp_path):
    run = _with_matched_projection_sources(
        _processing_run("run_projection_save_fails"),
        tmp_path,
    )
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(
        review_store=review_store,
        projection_store=_FailingProjectionSaveStore(),
    )

    with pytest.raises(RuntimeError, match="projection persistence unavailable"):
        service.orchestrate_and_persist_post_matching(
            run_id=run.run_id,
            reconciliation_outcomes=[
                {"invoice_id": "INV-050", "status": "finalizable"},
            ],
            run_store=run_store,
        )

    persisted_run = run_store.get_run(run.run_id, tenant_id="tenant-test")
    assert persisted_run is not None
    assert persisted_run.status == "processing"


def test_orchestrate_and_persist_post_matching_does_not_complete_when_projection_readback_fails(tmp_path):
    run = _with_matched_projection_sources(
        _processing_run("run_projection_readback_fails"),
        tmp_path,
    )
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(
        review_store=review_store,
        projection_store=_UnreadableAfterSaveProjectionStore(),
    )

    with pytest.raises(
        CompletedRunProjectionIntegrityError,
        match="not readable after persistence",
    ):
        service.orchestrate_and_persist_post_matching(
            run_id=run.run_id,
            reconciliation_outcomes=[
                {"invoice_id": "INV-060", "status": "finalizable"},
            ],
            run_store=run_store,
        )

    persisted_run = run_store.get_run(run.run_id, tenant_id="tenant-test")
    assert persisted_run is not None
    assert persisted_run.status == "processing"


def test_orchestrate_and_persist_post_review_resolution_does_not_complete_when_projection_save_fails(tmp_path):
    run = _with_matched_projection_sources(
        _review_required_run("run_review_projection_save_fails"),
        tmp_path,
    )
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(
        review_store=review_store,
        projection_store=_FailingProjectionSaveStore(),
    )

    with pytest.raises(RuntimeError, match="projection persistence unavailable"):
        service.orchestrate_and_persist_post_review_resolution(
            run_id=run.run_id,
            matching_completed=True,
            run_store=run_store,
        )

    persisted_run = run_store.get_run(run.run_id, tenant_id="tenant-test")
    assert persisted_run is not None
    assert persisted_run.status == "review_required"


def test_orchestrate_and_persist_post_review_resolution_does_not_complete_when_projection_readback_fails(tmp_path):
    run = _with_matched_projection_sources(
        _review_required_run("run_review_projection_readback_fails"),
        tmp_path,
    )
    run_store = InMemoryRunStore([run])
    review_store = InMemoryReviewStore()
    service = RunOrchestrationService(
        review_store=review_store,
        projection_store=_UnreadableAfterSaveProjectionStore(),
    )

    with pytest.raises(
        CompletedRunProjectionIntegrityError,
        match="not readable after persistence",
    ):
        service.orchestrate_and_persist_post_review_resolution(
            run_id=run.run_id,
            matching_completed=True,
            run_store=run_store,
        )

    persisted_run = run_store.get_run(run.run_id, tenant_id="tenant-test")
    assert persisted_run is not None
    assert persisted_run.status == "review_required"
