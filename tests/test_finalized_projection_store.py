from __future__ import annotations

import sqlite3
from datetime import date, datetime
from decimal import Decimal

import pytest

from invomatch.domain.export import (
    FinalDecisionType,
    FinalizedInvoiceRef,
    FinalizedMatchMeta,
    FinalizedPaymentRef,
    FinalizedResult,
    FinalizedReviewMeta,
    FinalizedReviewStatus,
)
from invomatch.services.export.finalized_projection_store import (
    SqliteFinalizedProjectionStore,
)


def _result(run_id: str) -> FinalizedResult:
    return FinalizedResult(
        result_id="inv-1",
        run_id=run_id,
        decision_type=FinalDecisionType.MATCH,
        invoice=FinalizedInvoiceRef(
            invoice_id="inv-1",
            invoice_number="INV-1",
            invoice_date=date(2026, 1, 1),
            amount=Decimal("100.00"),
            currency="SEK",
            vendor_name=None,
        ),
        payments=(
            FinalizedPaymentRef(
                payment_id="pay-1",
                payment_date=date(2026, 1, 2),
                amount=Decimal("100.00"),
                currency="SEK",
            ),
        ),
        match=FinalizedMatchMeta(
            confidence=Decimal("1.0"),
            method="rule_based",
            matched_amount=Decimal("100.00"),
            difference_amount=Decimal("0.00"),
        ),
        review=FinalizedReviewMeta(
            status=FinalizedReviewStatus.NOT_REQUIRED,
            reviewed_by=None,
            reviewed_at=None,
        ),
    )


def test_sqlite_finalized_projection_store_round_trips_results_per_tenant_and_run(tmp_path):
    store = SqliteFinalizedProjectionStore(tmp_path / "projection.sqlite3")

    store.save_results(
        tenant_id="tenant-a",
        run_id="run-1",
        results=[_result("run-1")],
        created_from_run_version=1,
        source_fingerprint="source-fp-1",
        created_by_system="test",
    )

    assert store.exists(tenant_id="tenant-a", run_id="run-1") is True
    assert store.exists(tenant_id="tenant-b", run_id="run-1") is False

    loaded = store.get_results(tenant_id="tenant-a", run_id="run-1")

    assert loaded == [_result("run-1")]


def test_sqlite_finalized_projection_store_is_immutable_per_tenant_run(tmp_path):
    store = SqliteFinalizedProjectionStore(tmp_path / "projection.sqlite3")

    store.save_results(
        tenant_id="tenant-a",
        run_id="run-1",
        results=[_result("run-1")],
        created_from_run_version=1,
        source_fingerprint="source-fp-1",
        created_by_system="test",
    )

    from invomatch.services.export.finalized_projection_store import DuplicateFinalizedProjectionError

    with pytest.raises(DuplicateFinalizedProjectionError):
        store.save_results(
            tenant_id="tenant-a",
            run_id="run-1",
            results=[_result("run-1")],
            created_from_run_version=1,
            source_fingerprint="source-fp-1",
            created_by_system="test",
        )


def test_sqlite_finalized_projection_store_requires_tenant_boundary(tmp_path):
    store = SqliteFinalizedProjectionStore(tmp_path / "projection.sqlite3")

    with pytest.raises(ValueError):
        store.save_results(
            tenant_id="",
            run_id="run-1",
            results=[_result("run-1")],
        )

    with pytest.raises(ValueError):
        store.get_results(
            tenant_id="",
            run_id="run-1",
        )

    with pytest.raises(ValueError):
        store.exists(
            tenant_id="",
            run_id="run-1",
        )


def test_sqlite_finalized_projection_payload_includes_lineage_metadata(tmp_path):
    store = SqliteFinalizedProjectionStore(tmp_path / "projection.sqlite3")

    store.save_results(
        tenant_id="tenant-a",
        run_id="run-1",
        results=[_result("run-1")],
        created_from_run_version=7,
        source_fingerprint="source-fp-123",
        created_by_system="projection-writer",
    )

    with sqlite3.connect(tmp_path / "projection.sqlite3") as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT payload_json
            FROM finalized_projections
            WHERE tenant_id = ?
              AND run_id = ?
            """,
            ("tenant-a", "run-1"),
        ).fetchone()

    assert row is not None

    import json

    payload = json.loads(row["payload_json"])

    assert payload["projection_version"] == 1
    assert payload["lineage"]["created_from_run_version"] == 7
    assert payload["lineage"]["source_fingerprint"] == "source-fp-123"
    assert payload["lineage"]["created_by_system"] == "projection-writer"
    assert isinstance(payload["lineage"]["created_at"], str)


def test_sqlite_finalized_projection_store_rejects_legacy_payload_without_projection_version(tmp_path):
    db_path = tmp_path / "projection.sqlite3"
    store = SqliteFinalizedProjectionStore(db_path)

    legacy_payload = {
        "version": 1,
        "results": [],
    }

    import json

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO finalized_projections (
                tenant_id,
                run_id,
                payload_json,
                created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (
                "tenant-a",
                "run-legacy",
                json.dumps(legacy_payload),
                datetime.now().isoformat(),
            ),
        )

    with pytest.raises(ValueError, match="unsupported finalized projection payload version"):
        store.get_results(tenant_id="tenant-a", run_id="run-legacy")


def test_sqlite_finalized_projection_duplicate_save_raises_domain_error(tmp_path):
    store = SqliteFinalizedProjectionStore(tmp_path / "projection.sqlite3")

    store.save_results(
        tenant_id="tenant-a",
        run_id="run-1",
        results=[_result("run-1")],
        created_from_run_version=1,
        source_fingerprint="source-fp-1",
        created_by_system="projection-writer",
    )

    from invomatch.services.export.finalized_projection_store import DuplicateFinalizedProjectionError

    with pytest.raises(DuplicateFinalizedProjectionError, match="finalized projection already exists"):
        store.save_results(
            tenant_id="tenant-a",
            run_id="run-1",
            results=[_result("run-1")],
            created_from_run_version=1,
            source_fingerprint="source-fp-1",
            created_by_system="projection-writer",
        )
