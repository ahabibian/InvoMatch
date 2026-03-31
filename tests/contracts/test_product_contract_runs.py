from __future__ import annotations


def _assert_forbidden_fields(payload: dict, forbidden: set[str]) -> None:
    leaked = forbidden.intersection(payload.keys())
    assert not leaked, f"Forbidden fields leaked: {sorted(leaked)}"


def test_get_runs_conforms_to_product_contract(client):
    response = client.get("/api/reconciliation/runs")

    assert response.status_code in (200, 404), response.text
    if response.status_code != 200:
        return

    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["items"], list)

    forbidden = {
        "internal_status",
        "retry_count",
        "lease_owner",
        "version",
        "debug_info",
        "invoice_csv_path",
        "payment_csv_path",
        "error_message",
        "report",
        "started_at",
        "finished_at",
    }

    for item in data["items"]:
        assert "run_id" in item
        assert "status" in item
        assert "created_at" in item
        _assert_forbidden_fields(item, forbidden)


def test_get_run_detail_conforms_to_product_contract(client):
    response = client.get("/api/reconciliation/runs/test-run-id")

    assert response.status_code in (200, 404), response.text
    if response.status_code != 200:
        return

    data = response.json()
    assert "run_id" in data
    assert "status" in data
    assert "created_at" in data
    assert "matches" in data
    assert isinstance(data["matches"], list)

    forbidden = {
        "internal_status",
        "retry_count",
        "lease_owner",
        "version",
        "debug_info",
        "invoice_csv_path",
        "payment_csv_path",
        "error_message",
        "report",
        "started_at",
        "finished_at",
    }
    _assert_forbidden_fields(data, forbidden)