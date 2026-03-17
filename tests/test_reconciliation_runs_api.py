from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from invomatch.api.reconciliation_runs import get_reconciliation_run, list_reconciliation_runs
from invomatch.services.reconciliation_runs import save_reconciliation_run
from invomatch.services.run_registry import RunRegistry
from invomatch.domain.models import ReconciliationReport


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
    first = save_reconciliation_run(
        report=_report(matched=2, unmatched=1),
        invoice_csv_path=Path("sample-data/invoices-a.csv"),
        payment_csv_path=Path("sample-data/payments-a.csv"),
        store_path=store_path,
    )
    second = save_reconciliation_run(
        report=_report(matched=4, unmatched=3),
        invoice_csv_path=Path("sample-data/invoices-b.csv"),
        payment_csv_path=Path("sample-data/payments-b.csv"),
        store_path=store_path,
    )
    return [first.run_id, second.run_id]


def _request_for_store(store_path: Path) -> SimpleNamespace:
    app = SimpleNamespace(state=SimpleNamespace(run_registry=RunRegistry(store_path=store_path)))
    return SimpleNamespace(app=app)


def test_get_reconciliation_runs_returns_paginated_list(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    _seed_runs(store_path)

    response = list_reconciliation_runs(request=_request_for_store(store_path))

    assert response.total == 2
    assert response.limit == 50
    assert response.offset == 0
    assert len(response.items) == 2
    assert response.items[0].status == "completed"


def test_get_reconciliation_runs_filters_by_status(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    _seed_runs(store_path)

    response = list_reconciliation_runs(request=_request_for_store(store_path), status="completed")

    assert response.total == 2
    assert all(item.status == "completed" for item in response.items)


def test_get_reconciliation_runs_applies_pagination(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    run_ids = _seed_runs(store_path)

    response = list_reconciliation_runs(
        request=_request_for_store(store_path),
        limit=1,
        offset=1,
        sort_order="asc",
    )

    assert response.total == 2
    assert response.limit == 1
    assert response.offset == 1
    assert len(response.items) == 1
    assert response.items[0].run_id == run_ids[1]


def test_get_reconciliation_run_detail_returns_report_payload(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    run_ids = _seed_runs(store_path)

    response = get_reconciliation_run(run_ids[0], request=_request_for_store(store_path))

    assert response.run_id == run_ids[0]
    assert response.status == "completed"
    assert response.report["matched"] == 2


def test_get_reconciliation_run_detail_returns_404_for_missing_run(tmp_path: Path):
    store_path = tmp_path / "reconciliation_runs.json"
    _seed_runs(store_path)

    with pytest.raises(HTTPException) as exc_info:
        get_reconciliation_run("missing-run", request=_request_for_store(store_path))

    assert exc_info.value.status_code == 404
