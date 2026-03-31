from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from invomatch.api.export import get_reconciliation_run_export
from invomatch.services.reconciliation_runs import save_reconciliation_run
from invomatch.services.run_registry import RunRegistry
from invomatch.services.run_store import JsonRunStore


def _request_for_store(run_store: JsonRunStore) -> SimpleNamespace:
    app = SimpleNamespace(state=SimpleNamespace(run_registry=RunRegistry(run_store=run_store)))
    return SimpleNamespace(app=app)


def test_get_reconciliation_run_export_returns_404_for_missing_run(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    request = _request_for_store(run_store)

    with pytest.raises(HTTPException) as exc_info:
        get_reconciliation_run_export("missing-run", request=request)

    assert exc_info.value.status_code == 404


def test_get_reconciliation_run_export_returns_product_export_model(tmp_path: Path):
    run_store = JsonRunStore(tmp_path / "reconciliation_runs.json")
    run = save_reconciliation_run(
        report=None,
        invoice_csv_path=Path("sample-data/invoices.csv"),
        payment_csv_path=Path("sample-data/payments.csv"),
        run_store=run_store,
    )

    response = get_reconciliation_run_export(run.run_id, request=_request_for_store(run_store))

    assert response.run_id == run.run_id
    assert response.export_status == "not_ready"
    assert response.export_format == "json"
    assert response.download_url is None
    assert response.generated_at is None
    assert not hasattr(response, "storage_backend")
    assert not hasattr(response, "storage_path")
    assert not hasattr(response, "job_id")