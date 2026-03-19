from functools import partial
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from invomatch.api.reconciliation_runs import (
    create_reconciliation_run,
    get_reconciliation_run,
    list_reconciliation_runs,
)
from invomatch.api.reconciliation_schemas import CreateRunRequest
from invomatch.domain.models import ReconciliationReport
from invomatch.services.reconciliation import reconcile_and_save
from invomatch.services.reconciliation_runs import (
    create_reconciliation_run as create_run_record,
    save_reconciliation_run,
    update_reconciliation_run,
)
from invomatch.services.run_registry import RunRegistry


@pytest.fixture
def reconciliation_request(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    app = SimpleNamespace(
        state=SimpleNamespace(
            run_registry=RunRegistry(store_path=store_path),
            reconcile_and_save=partial(reconcile_and_save, store_path=store_path),
        )
    )
    return SimpleNamespace(app=app), store_path


def _report(matched: int, unmatched: int) -> ReconciliationReport:
    return ReconciliationReport(
        total_invoices=matched + unmatched,
        matched=matched,
        duplicate_detected=0,
        partial_match=0,
        unmatched=unmatched,
        results=[],
    )


def _seed_runs(store_path: Path) -> list[str]:
    pending = create_run_record(
        invoice_csv_path=Path("sample-data/invoices-pending.csv"),
        payment_csv_path=Path("sample-data/payments-pending.csv"),
        store_path=store_path,
    )
    failed = create_run_record(
        invoice_csv_path=Path("sample-data/invoices-failed.csv"),
        payment_csv_path=Path("sample-data/payments-failed.csv"),
        store_path=store_path,
    )
    update_reconciliation_run(failed.run_id, status="running", store_path=store_path)
    update_reconciliation_run(
        failed.run_id,
        status="failed",
        error_message="import failed",
        store_path=store_path,
    )
    completed = save_reconciliation_run(
        report=_report(matched=4, unmatched=3),
        invoice_csv_path=Path("sample-data/invoices-completed.csv"),
        payment_csv_path=Path("sample-data/payments-completed.csv"),
        store_path=store_path,
    )
    return [pending.run_id, failed.run_id, completed.run_id]


def _request_for_store(store_path: Path) -> SimpleNamespace:
    app = SimpleNamespace(
        state=SimpleNamespace(
            run_registry=RunRegistry(store_path=store_path),
            reconcile_and_save=partial(reconcile_and_save, store_path=store_path),
        )
    )
    return SimpleNamespace(app=app)


def test_create_reconciliation_run_returns_completed_run(reconciliation_request):
    request, store_path = reconciliation_request

    response = create_reconciliation_run(
        request_body=CreateRunRequest(
            invoice_csv_path="sample-data/invoices.csv",
            payment_csv_path="sample-data/payments.csv",
        ),
        request=request,
    )

    assert response.status == "completed"
    assert response.started_at is not None
    assert response.finished_at is not None
    assert response.error_message is None
    assert response.invoice_csv_path == "sample-data/invoices.csv"
    assert response.payment_csv_path == "sample-data/payments.csv"
    assert response.report is not None
    assert response.report["matched"] == 20

    list_response = list_reconciliation_runs(request=_request_for_store(store_path))
    assert list_response.total == 1
    assert list_response.items[0].run_id == response.run_id


def test_create_reconciliation_run_rejects_invalid_request():
    with pytest.raises(ValidationError):
        CreateRunRequest(
            invoice_csv_path="",
            payment_csv_path="sample-data/payments.csv",
        )


def test_create_then_retrieve_reconciliation_run_returns_persisted_payload(reconciliation_request):
    request, _ = reconciliation_request

    created_run = create_reconciliation_run(
        request_body=CreateRunRequest(
            invoice_csv_path="sample-data/invoices.csv",
            payment_csv_path="sample-data/payments.csv",
        ),
        request=request,
    )

    response = get_reconciliation_run(created_run.run_id, request=request)

    assert response.run_id == created_run.run_id
    assert response.status == "completed"
    assert response.started_at is not None
    assert response.finished_at is not None
    assert response.report is not None
    assert response.report["total_invoices"] == 50
    assert response.report["matched"] == 20
    assert response.report["unmatched"] == 10


def test_get_reconciliation_runs_returns_paginated_list(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    _seed_runs(store_path)

    response = list_reconciliation_runs(request=_request_for_store(store_path))

    assert response.total == 3
    assert response.limit == 50
    assert response.offset == 0
    assert len(response.items) == 3
    assert {item.status for item in response.items} == {"pending", "failed", "completed"}


def test_get_reconciliation_runs_filters_by_status(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    run_ids = _seed_runs(store_path)

    response = list_reconciliation_runs(request=_request_for_store(store_path), status="failed")

    assert response.total == 1
    assert [item.run_id for item in response.items] == [run_ids[1]]
    assert response.items[0].status == "failed"
    assert response.items[0].error_message == "import failed"


def test_get_reconciliation_runs_applies_pagination(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    run_ids = _seed_runs(store_path)

    response = list_reconciliation_runs(
        request=_request_for_store(store_path),
        limit=1,
        offset=1,
        sort_order="asc",
    )

    assert response.total == 3
    assert response.limit == 1
    assert response.offset == 1
    assert len(response.items) == 1
    assert response.items[0].run_id == run_ids[1]


def test_get_reconciliation_run_detail_returns_failed_payload(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    run_ids = _seed_runs(store_path)

    response = get_reconciliation_run(run_ids[1], request=_request_for_store(store_path))

    assert response.run_id == run_ids[1]
    assert response.status == "failed"
    assert response.error_message == "import failed"
    assert response.report is None
    assert response.finished_at is not None


def test_get_reconciliation_run_detail_returns_404_for_missing_run(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    _seed_runs(store_path)

    with pytest.raises(HTTPException) as exc_info:
        get_reconciliation_run("missing-run", request=_request_for_store(store_path))

    assert exc_info.value.status_code == 404
