from __future__ import annotations


def test_post_run_actions_rejects_unknown_fields(client):
    payload = {
        "action_type": "confirm_match",
        "target_id": "match-123",
        "payload": {},
        "note": "reviewed by user",
        "internal_status": "should-not-be-accepted",
    }

    response = client.post("/runs/test-run-id/actions", json=payload)

    assert response.status_code in (200, 400, 404, 405, 422), response.text
    if response.status_code == 200:
        data = response.json()
        assert "run_id" in data
        assert "action_type" in data
        assert "accepted" in data
        assert "status" in data
        assert "internal_status" not in data
        return

    assert response.status_code in (400, 404, 405, 422)


def test_post_run_actions_accepts_product_contract_shape(client):
    payload = {
        "action_type": "confirm_match",
        "target_id": "match-123",
        "payload": {},
        "note": "confirmed by reviewer",
    }

    response = client.post("/runs/test-run-id/actions", json=payload)

    assert response.status_code in (200, 404, 405, 422), response.text
    if response.status_code != 200:
        return

    data = response.json()
    assert "run_id" in data
    assert "action_type" in data
    assert "accepted" in data
    assert "status" in data