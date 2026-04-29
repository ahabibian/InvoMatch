from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from invomatch.domain.models import (
    MatchResult,
    ReconciliationReport,
    ReconciliationResult,
    ReconciliationRun,
    RunError,
)
from invomatch.services.run_store import JsonRunStore
from invomatch.services.sqlite_run_store import SqliteRunStore


def _now() -> datetime:
    return datetime(2026, 4, 19, 14, 0, 0, tzinfo=timezone.utc)


def _build_run(run_id: str) -> ReconciliationRun:
    now = _now()
    return ReconciliationRun(
        run_id=run_id,
            tenant_id="tenant-test",
        status="failed",
        version=3,
        created_at=now - timedelta(minutes=10),
        updated_at=now,
        started_at=now - timedelta(minutes=9),
        finished_at=now - timedelta(minutes=1),
        claimed_by="worker-recovery",
        claimed_at=now - timedelta(minutes=9),
        lease_expires_at=now - timedelta(minutes=8),
        attempt_count=4,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error=RunError(
            code="runtime_failure",
            message="dependency timeout",
            retryable=True,
            terminal=False,
        ),
        error_message="[runtime] dependency timeout",
        report=ReconciliationReport(
            total_invoices=3,
            matched=1,
            duplicate_detected=1,
            partial_match=0,
            unmatched=1,
            results=[
                ReconciliationResult(
                    invoice_id="INV-001",
                    match_result=MatchResult(
                        status="matched",
                        payment_id="PAY-001",
                        duplicate_payment_ids=None,
                        payment_ids=["PAY-001"],
                        confidence_score=0.99,
                        confidence_explanation="exact reference match",
                        mismatch_reasons=["reference_match", "amount_match"],
                    ),
                ),
                ReconciliationResult(
                    invoice_id="INV-002",
                    match_result=MatchResult(
                        status="duplicate_detected",
                        payment_id=None,
                        duplicate_payment_ids=["PAY-002", "PAY-003"],
                        payment_ids=["PAY-002", "PAY-003"],
                        confidence_score=0.72,
                        confidence_explanation="multiple duplicate candidates",
                        mismatch_reasons=["duplicate_candidates"],
                    ),
                ),
                ReconciliationResult(
                    invoice_id="INV-003",
                    match_result=MatchResult(
                        status="unmatched",
                        payment_id=None,
                        duplicate_payment_ids=None,
                        payment_ids=None,
                        confidence_score=0.10,
                        confidence_explanation="no viable candidate",
                        mismatch_reasons=["no_viable_candidate"],
                    ),
                ),
            ],
        ),
    )


@pytest.fixture(params=["json", "sqlite"])
def store_factory(request, tmp_path: Path):
    if request.param == "json":
        path = tmp_path / "runs.json"

        def _factory():
            return JsonRunStore(path)

        return _factory

    path = tmp_path / "runs.sqlite3"

    def _factory():
        return SqliteRunStore(path)

    return _factory


def test_restart_reload_preserves_run_integrity(store_factory):
    first_store = store_factory()
    original = _build_run("run-restart-integrity")

    first_store.create_run(original)

    reloaded_store = store_factory()
    loaded = reloaded_store.get_run("run-restart-integrity")

    assert loaded is not None
    assert loaded.run_id == original.run_id
    assert loaded.status == "failed"
    assert loaded.version == 3

    assert loaded.created_at == original.created_at
    assert loaded.updated_at == original.updated_at
    assert loaded.started_at == original.started_at
    assert loaded.finished_at == original.finished_at

    assert loaded.claimed_by == "worker-recovery"
    assert loaded.claimed_at == original.claimed_at
    assert loaded.lease_expires_at == original.lease_expires_at
    assert loaded.attempt_count == 4

    assert loaded.invoice_csv_path == "input/invoices.csv"
    assert loaded.payment_csv_path == "input/payments.csv"

    assert loaded.error_message == "[runtime] dependency timeout"
    assert loaded.error is not None
    assert loaded.error.code == "runtime_failure"
    assert loaded.error.message == "dependency timeout"
    assert loaded.error.retryable is True
    assert loaded.error.terminal is False

    assert loaded.report is not None
    assert loaded.report.total_invoices == 3
    assert loaded.report.matched == 1
    assert loaded.report.duplicate_detected == 1
    assert loaded.report.partial_match == 0
    assert loaded.report.unmatched == 1
    assert len(loaded.report.results) == 3
    assert loaded.report.results[0].invoice_id == "INV-001"
    assert loaded.report.results[0].match_result.status == "matched"
    assert loaded.report.results[1].match_result.status == "duplicate_detected"
    assert loaded.report.results[2].match_result.status == "unmatched"


def test_restart_reload_preserves_processing_lease_metadata(store_factory):
    first_store = store_factory()
    now = _now()

    original = ReconciliationRun(
        run_id="run-processing-reload",
            tenant_id="tenant-test",
        status="processing",
        version=2,
        created_at=now - timedelta(minutes=20),
        updated_at=now - timedelta(seconds=30),
        started_at=now - timedelta(minutes=19),
        finished_at=None,
        claimed_by="worker-live",
        claimed_at=now - timedelta(minutes=19),
        lease_expires_at=now + timedelta(seconds=45),
        attempt_count=2,
        invoice_csv_path="input/invoices.csv",
        payment_csv_path="input/payments.csv",
        error=None,
        error_message=None,
        report=None,
    )

    first_store.create_run(original)

    reloaded_store = store_factory()
    loaded = reloaded_store.get_run("run-processing-reload")

    assert loaded is not None
    assert loaded.status == "processing"
    assert loaded.version == 2
    assert loaded.claimed_by == "worker-live"
    assert loaded.claimed_at == original.claimed_at
    assert loaded.lease_expires_at == original.lease_expires_at
    assert loaded.attempt_count == 2
    assert loaded.finished_at is None
    assert loaded.error is None
    assert loaded.report is None