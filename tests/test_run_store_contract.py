from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from invomatch.persistence.base import RunStore


UTC = timezone.utc


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


@pytest.fixture
def run_store() -> RunStore:
    """
    Contract fixture.

    Each concrete backend test suite must provide this fixture.
    Example:
    - SQLite contract suite
    - PostgreSQL contract suite
    """
    raise NotImplementedError("Backend-specific fixture must provide a RunStore implementation.")


@pytest.fixture
def sample_run() -> dict[str, Any]:
    now = utc_now()
    return {
        "run_id": "run-001",
        "tenant_id": "tenant-001",
        "status": "pending",
        "current_stage": None,
        "claimed_by": None,
        "claim_expires_at": None,
        "retry_count": 0,
        "max_retries": 3,
        "created_at": now,
        "updated_at": now,
        "started_at": None,
        "completed_at": None,
        "error_code": None,
        "error_message": None,
        "invoice_csv_path": "input/invoices.csv",
        "payment_csv_path": "input/payments.csv",
        "result_artifact_uri": None,
        "schema_version": "1",
        "storage_version": "1",
        "engine_version": "1",
        "metadata_json": {},
    }


def test_create_then_get_returns_authoritative_run(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_id = run_store.create_run(sample_run)
    loaded = run_store.get_run(run_id)

    assert run_id == sample_run["run_id"]
    assert loaded is not None


def test_duplicate_create_is_rejected(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_store.create_run(sample_run)

    with pytest.raises(Exception):
        run_store.create_run(sample_run)


def test_list_runs_is_deterministic(run_store: RunStore) -> None:
    now = utc_now()

    runs = [
        {
            "run_id": "run-a",
            "tenant_id": "tenant-001",
            "status": "pending",
            "current_stage": None,
            "claimed_by": None,
            "claim_expires_at": None,
            "retry_count": 0,
            "max_retries": 3,
            "created_at": now,
            "updated_at": now,
            "started_at": None,
            "completed_at": None,
            "error_code": None,
            "error_message": None,
            "invoice_csv_path": "a.csv",
            "payment_csv_path": "a-pay.csv",
            "result_artifact_uri": None,
            "schema_version": "1",
            "storage_version": "1",
            "engine_version": "1",
            "metadata_json": {},
        },
        {
            "run_id": "run-b",
            "tenant_id": "tenant-001",
            "status": "pending",
            "current_stage": None,
            "claimed_by": None,
            "claim_expires_at": None,
            "retry_count": 0,
            "max_retries": 3,
            "created_at": now,
            "updated_at": now,
            "started_at": None,
            "completed_at": None,
            "error_code": None,
            "error_message": None,
            "invoice_csv_path": "b.csv",
            "payment_csv_path": "b-pay.csv",
            "result_artifact_uri": None,
            "schema_version": "1",
            "storage_version": "1",
            "engine_version": "1",
            "metadata_json": {},
        },
    ]

    for run in runs:
        run_store.create_run(run)

    first = run_store.list_runs(limit=100)
    second = run_store.list_runs(limit=100)

    assert first == second


def test_claim_next_eligible_run_returns_only_one_claim(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_store.create_run(sample_run)

    claimed = run_store.claim_next_eligible_run(
        worker_id="worker-1",
        now=utc_now(),
        lease_seconds=60,
    )
    not_claimed = run_store.claim_next_eligible_run(
        worker_id="worker-2",
        now=utc_now(),
        lease_seconds=60,
    )

    assert claimed is not None
    assert not_claimed is None


def test_renew_claim_succeeds_for_owner_only(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_store.create_run(sample_run)

    claimed = run_store.claim_next_eligible_run(
        worker_id="worker-1",
        now=utc_now(),
        lease_seconds=60,
    )
    assert claimed is not None

    renewed = run_store.renew_claim(
        run_id=sample_run["run_id"],
        worker_id="worker-1",
        now=utc_now(),
        lease_seconds=60,
    )
    assert renewed is True

    renewed_by_other = run_store.renew_claim(
        run_id=sample_run["run_id"],
        worker_id="worker-2",
        now=utc_now(),
        lease_seconds=60,
    )
    assert renewed_by_other is False


def test_release_claim_succeeds_for_owner_only(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_store.create_run(sample_run)

    claimed = run_store.claim_next_eligible_run(
        worker_id="worker-1",
        now=utc_now(),
        lease_seconds=60,
    )
    assert claimed is not None

    assert run_store.release_claim(sample_run["run_id"], "worker-1") is True
    assert run_store.release_claim(sample_run["run_id"], "worker-2") is False


def test_mark_awaiting_review_makes_run_non_claimable(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_store.create_run(sample_run)

    claimed = run_store.claim_next_eligible_run(
        worker_id="worker-1",
        now=utc_now(),
        lease_seconds=60,
    )
    assert claimed is not None

    assert run_store.mark_awaiting_review(sample_run["run_id"]) is True

    next_claim = run_store.claim_next_eligible_run(
        worker_id="worker-2",
        now=utc_now(),
        lease_seconds=60,
    )
    assert next_claim is None


def test_mark_completed_creates_terminal_non_claimable_state(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_store.create_run(sample_run)

    claimed = run_store.claim_next_eligible_run(
        worker_id="worker-1",
        now=utc_now(),
        lease_seconds=60,
    )
    assert claimed is not None

    assert run_store.mark_completed(
        run_id=sample_run["run_id"],
        result_uri="artifacts/result.json",
    ) is True

    next_claim = run_store.claim_next_eligible_run(
        worker_id="worker-2",
        now=utc_now(),
        lease_seconds=60,
    )
    assert next_claim is None


def test_mark_failed_creates_terminal_non_claimable_state(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_store.create_run(sample_run)

    claimed = run_store.claim_next_eligible_run(
        worker_id="worker-1",
        now=utc_now(),
        lease_seconds=60,
    )
    assert claimed is not None

    assert run_store.mark_failed(
        run_id=sample_run["run_id"],
        error_code="MATCHING_ERROR",
        error_message="simulated failure",
    ) is True

    next_claim = run_store.claim_next_eligible_run(
        worker_id="worker-2",
        now=utc_now(),
        lease_seconds=60,
    )
    assert next_claim is None


def test_terminal_run_cannot_be_reopened_via_progress_update(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_store.create_run(sample_run)
    assert run_store.mark_completed(sample_run["run_id"], "artifacts/result.json") is True

    updated = run_store.update_progress(
        run_id=sample_run["run_id"],
        status="running",
        stage="matching",
    )
    assert updated is False


def test_retry_visibility_is_persisted(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_store.create_run(sample_run)

    assert run_store.is_retry_allowed(sample_run["run_id"]) is True
    assert run_store.increment_retry(sample_run["run_id"]) is True


def test_not_found_read_returns_none(run_store: RunStore) -> None:
    loaded = run_store.get_run("missing-run")
    assert loaded is None


def test_claim_returns_no_result_when_store_is_empty(run_store: RunStore) -> None:
    claimed = run_store.claim_next_eligible_run(
        worker_id="worker-1",
        now=utc_now(),
        lease_seconds=60,
    )
    assert claimed is None


def test_reclaim_after_lease_expiry_is_possible(
    run_store: RunStore,
    sample_run: dict[str, Any],
) -> None:
    run_store.create_run(sample_run)

    first_claim = run_store.claim_next_eligible_run(
        worker_id="worker-1",
        now=utc_now(),
        lease_seconds=1,
    )
    assert first_claim is not None

    second_claim = run_store.claim_next_eligible_run(
        worker_id="worker-2",
        now=utc_now() + timedelta(seconds=2),
        lease_seconds=60,
    )
    assert second_claim is not None