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
    router,
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
from invomatch.services.run_store import InMemoryRunStore, JsonRunStore, RunStore


def _request_for_store(run_store: RunStore) -> SimpleNamespace:
    app = SimpleNamespace(
        state=SimpleNamespace(
            run_registry=RunRegistry(run_store=run_store),
            reconcile_and_save=partial(reconcile_and_save, run_store=run_store),
        )
    )
    return SimpleNamespace(app=app)


@pytest.fixture
def reconciliation_request(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    return _request_for_store(run_store), run_store


def _report(matched: int, unmatched: int) -> ReconciliationReport:
    return ReconciliationReport(
        total_invoices=matched + unmatched,
        matched=matched,
        duplicate_detected=0,
        partial_match=0,
        unmatched=unmatched,
        results=[],
    )


def _seed_runs(run_store: RunStore) -> list[str]:
    pending = create_run_record(
        invoice_csv_path=Path("sample-data/invoices-pending.csv"),
        payment_csv_path=Path("sample-data/payments-pending.csv"),
        run_store=run_store,
    )
    failed = create_run_record(
        invoice_csv_path=Path("sample-data/invoices-failed.csv"),
        payment_csv_path=Path("sample-data/payments-failed.csv"),
        run_store=run_store,
    )
    update_reconciliation_run(failed.run_id, status="running", run_store=run_store)
    update_reconciliation_run(
        failed.run_id,
        status="failed",
        error_message="import failed",
        run_store=run_store,
    )
    completed = save_reconciliation_run(
        report=_report(matched=4, unmatched=3),
        invoice_csv_path=Path("sample-data/invoices-completed.csv"),
        payment_csv_path=Path("sample-data/payments-completed.csv"),
        run_store=run_store,
    )
    return [pending.run_id, failed.run_id, completed.run_id]


def test_create_reconciliation_run_returns_completed_run(reconciliation_request):
    request, run_store = reconciliation_request

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

    list_response = list_reconciliation_runs(request=_request_for_store(run_store))
    assert list_response.total == 1
    assert list_response.items[0].run_id == response.run_id


def test_create_reconciliation_run_supports_injected_in_memory_store():
    run_store = InMemoryRunStore()
    request = _request_for_store(run_store)

    response = create_reconciliation_run(
        request_body=CreateRunRequest(
            invoice_csv_path="sample-data/invoices.csv",
            payment_csv_path="sample-data/payments.csv",
        ),
        request=request,
    )

    assert response.status == "completed"
    runs, total = run_store.list_runs()
    assert total == 1
    assert runs[0].run_id == response.run_id


def test_create_reconciliation_run_rejects_invalid_request():
    with pytest.raises(ValidationError):
        CreateRunRequest(
            invoice_csv_path="   ",
            payment_csv_path="sample-data/payments.csv",
        )


def test_post_reconciliation_route_declares_201_status_code():
    post_route = next(route for route in router.routes if route.path == "/api/reconciliation/runs" and "POST" in route.methods)

    assert post_route.status_code == 201


def test_create_reconciliation_run_returns_400_for_missing_invoice_file(reconciliation_request):
    request, _ = reconciliation_request

    with pytest.raises(HTTPException) as exc_info:
        create_reconciliation_run(
            request_body=CreateRunRequest(
                invoice_csv_path="sample-data/missing.csv",
                payment_csv_path="sample-data/payments.csv",
            ),
            request=request,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {
        "error_code": "input_validation_failed",
        "message": "invoice_csv_path does not exist: sample-data/missing.csv",
    }


def test_create_reconciliation_run_returns_400_for_missing_payment_file(reconciliation_request):
    request, _ = reconciliation_request

    with pytest.raises(HTTPException) as exc_info:
        create_reconciliation_run(
            request_body=CreateRunRequest(
                invoice_csv_path="sample-data/invoices.csv",
                payment_csv_path="sample-data/missing.csv",
            ),
            request=request,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {
        "error_code": "input_validation_failed",
        "message": "payment_csv_path does not exist: sample-data/missing.csv",
    }


def test_create_reconciliation_run_returns_400_for_wrong_extension(reconciliation_request, tmp_path: Path):
    request, _ = reconciliation_request
    invoice_path = tmp_path / "invoices.txt"
    invoice_path.write_text("id,date,amount`nINV-1,2024-01-01,10.00`n", encoding="utf-8")

    with pytest.raises(HTTPException) as exc_info:
        create_reconciliation_run(
            request_body=CreateRunRequest(
                invoice_csv_path=str(invoice_path),
                payment_csv_path="sample-data/payments.csv",
            ),
            request=request,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {
        "error_code": "input_validation_failed",
        "message": "invoice_csv_path must point to a .csv file",
    }


def test_create_reconciliation_run_returns_structured_execution_failure_and_persists_failed_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    request = _request_for_store(run_store)

    def boom(invoice_csv_path: Path, payment_csv_path: Path):
        raise RuntimeError("reconciliation exploded")

    monkeypatch.setattr("invomatch.services.reconciliation.reconcile", boom)

    with pytest.raises(HTTPException) as exc_info:
        create_reconciliation_run(
            request_body=CreateRunRequest(
                invoice_csv_path="sample-data/invoices.csv",
                payment_csv_path="sample-data/payments.csv",
            ),
            request=request,
        )

    assert exc_info.value.status_code == 500
    detail = exc_info.value.detail
    assert detail["error_code"] == "execution_failed"
    assert detail["message"] == "Reconciliation execution failed: reconciliation exploded"
    assert detail["run_id"]

    persisted_runs, total = run_store.list_runs()
    assert total == 1
    failed_run = persisted_runs[0]
    assert failed_run.run_id == detail["run_id"]
    assert failed_run.status == "failed"
    assert failed_run.error_message == "reconciliation exploded"
    assert failed_run.report is None
    assert failed_run.finished_at is not None


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
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    _seed_runs(run_store)

    response = list_reconciliation_runs(request=_request_for_store(run_store))

    assert response.total == 3
    assert response.limit == 50
    assert response.offset == 0
    assert len(response.items) == 3
    assert {item.status for item in response.items} == {"pending", "failed", "completed"}


def test_get_reconciliation_runs_filters_by_status(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    run_ids = _seed_runs(run_store)

    response = list_reconciliation_runs(request=_request_for_store(run_store), status="failed")

    assert response.total == 1
    assert [item.run_id for item in response.items] == [run_ids[1]]
    assert response.items[0].status == "failed"
    assert response.items[0].error_message == "import failed"


def test_get_reconciliation_runs_applies_pagination(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    run_ids = _seed_runs(run_store)

    response = list_reconciliation_runs(
        request=_request_for_store(run_store),
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
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    run_ids = _seed_runs(run_store)

    response = get_reconciliation_run(run_ids[1], request=_request_for_store(run_store))

    assert response.run_id == run_ids[1]
    assert response.status == "failed"
    assert response.error_message == "import failed"
    assert response.report is None
    assert response.finished_at is not None


def test_get_reconciliation_run_detail_returns_404_for_missing_run(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    _seed_runs(run_store)

    with pytest.raises(HTTPException) as exc_info:
        get_reconciliation_run("missing-run", request=_request_for_store(run_store))

    assert exc_info.value.status_code == 404
