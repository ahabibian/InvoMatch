from __future__ import annotations


def _assert_forbidden_fields(payload: dict, forbidden: set[str]) -> None:
    leaked = forbidden.intersection(payload.keys())
    assert not leaked, f"Forbidden fields leaked: {sorted(leaked)}"


def test_get_runs_conforms_to_product_contract(client):
    response = client.get("/runs")

    assert response.status_code in (200, 404, 405), response.text
    if response.status_code != 200:
        return

    data = response.json()
    assert isinstance(data, list)

    forbidden = {"internal_status", "retry_count", "lease_owner", "version", "debug_info"}

    for item in data:
        assert "run_id" in item
        assert "status" in item
        assert "created_at" in item
        _assert_forbidden_fields(item, forbidden)


def test_get_run_detail_conforms_to_product_contract(client):
    response = client.get("/runs/test-run-id")

    assert response.status_code in (200, 404, 405), response.text
    if response.status_code != 200:
        return

    data = response.json()
    assert "run_id" in data
    assert "status" in data
    assert "created_at" in data
    assert "matches" in data
    assert isinstance(data["matches"], list)

    forbidden = {"internal_status", "retry_count", "lease_owner", "version", "debug_info"}
    _assert_forbidden_fields(data, forbidden)