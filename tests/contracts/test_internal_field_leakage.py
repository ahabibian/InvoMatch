from __future__ import annotations


FORBIDDEN_FIELDS = {
    "internal_status",
    "retry_count",
    "lease_owner",
    "version",
    "debug_info",
    "worker_id",
    "attempt_count",
    "invoice_csv_path",
    "payment_csv_path",
    "error_message",
    "report",
    "started_at",
    "finished_at",
}


def _assert_no_forbidden_fields(payload):
    if isinstance(payload, dict):
        leaked = FORBIDDEN_FIELDS.intersection(payload.keys())
        assert not leaked, f"Forbidden fields leaked: {sorted(leaked)}"
        for value in payload.values():
            _assert_no_forbidden_fields(value)
    elif isinstance(payload, list):
        for item in payload:
            _assert_no_forbidden_fields(item)


def test_runs_endpoint_does_not_leak_internal_fields(client):
    response = client.get("/api/reconciliation/runs")
    assert response.status_code in (200, 404), response.text
    if response.status_code == 200:
        _assert_no_forbidden_fields(response.json())


def test_run_detail_endpoint_does_not_leak_internal_fields(client):
    response = client.get("/api/reconciliation/runs/test-run-id")
    assert response.status_code in (200, 404), response.text
    if response.status_code == 200:
        _assert_no_forbidden_fields(response.json())