from __future__ import annotations


def test_get_run_export_conforms_to_product_contract(client):
    response = client.get("/api/reconciliation/runs/test-run-id/export")

    assert response.status_code in (200, 404), response.text
    if response.status_code != 200:
        return

    data = response.json()
    assert "run_id" in data
    assert "export_status" in data
    assert "export_format" in data

    forbidden = {
        "internal_status",
        "retry_count",
        "lease_owner",
        "version",
        "debug_info",
        "storage_backend",
        "storage_path",
        "job_id",
    }
    leaked = forbidden.intersection(data.keys())
    assert not leaked, f"Forbidden export fields leaked: {sorted(leaked)}"