from __future__ import annotations


def test_get_run_review_conforms_to_product_contract(client):
    response = client.get("/api/reconciliation/runs/test-run-id/review")

    assert response.status_code in (200, 404), response.text
    if response.status_code != 200:
        return

    data = response.json()
    assert "case_id" in data
    assert "run_id" in data
    assert "status" in data
    assert "reason_code" in data

    forbidden = {
        "internal_status",
        "retry_count",
        "lease_owner",
        "version",
        "debug_info",
        "learning_signal",
        "feedback_event",
        "reviewed_payload",
        "reviewed_by",
        "decision_payload",
    }
    leaked = forbidden.intersection(data.keys())
    assert not leaked, f"Forbidden review fields leaked: {sorted(leaked)}"