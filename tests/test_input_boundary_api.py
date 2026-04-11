from __future__ import annotations

from fastapi.testclient import TestClient

from invomatch.main import create_app


def test_submit_json_returns_run_created_for_valid_payload() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "invoices": [
            {
                "id": "inv-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
                "reference": "ref-001",
            }
        ],
        "payments": [
            {
                "id": "pay-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
                "reference": "ref-001",
            }
        ],
    }

    response = client.post("/api/reconciliation/input/json", json=payload)

    assert response.status_code == 200

    body = response.json()
    assert body["input_id"]
    assert body["status"] == "run_created"
    assert body["ingestion_batch_id"] == body["input_id"]
    assert body["run_id"]
    assert body["errors"] == []


def test_submit_json_returns_rejected_for_invalid_payload() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "invoices": [
            {
                "id": "inv-001",
                "date": "2026-04-12",
                "amount": "",
                "currency": "USD",
            }
        ],
        "payments": [
            {
                "id": "pay-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
            }
        ],
    }

    response = client.post("/api/reconciliation/input/json", json=payload)

    assert response.status_code == 200

    body = response.json()
    assert body["input_id"]
    assert body["status"] == "rejected"
    assert body["ingestion_batch_id"] is None
    assert body["run_id"] is None
    assert len(body["errors"]) == 1
    assert body["errors"][0]["type"] == "validation_error"
    assert body["errors"][0]["field"] == "invoices.0.amount"


def test_get_input_session_returns_created_session() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "invoices": [
            {
                "id": "inv-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
                "reference": "ref-001",
            }
        ],
        "payments": [
            {
                "id": "pay-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
                "reference": "ref-001",
            }
        ],
    }

    post_response = client.post("/api/reconciliation/input/json", json=payload)
    input_id = post_response.json()["input_id"]

    get_response = client.get(f"/api/reconciliation/input/{input_id}")

    assert get_response.status_code == 200

    body = get_response.json()
    assert body["input_id"] == input_id
    assert body["input_type"] == "json"
    assert body["status"] == "run_created"
    assert body["ingestion_batch_id"] == input_id
    assert body["run_id"]
    assert body["errors"] == []


def test_get_input_session_returns_rejected_session() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "invoices": [
            {
                "id": "inv-001",
                "date": "2026-04-12",
                "amount": "",
                "currency": "USD",
            }
        ],
        "payments": [
            {
                "id": "pay-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
            }
        ],
    }

    post_response = client.post("/api/reconciliation/input/json", json=payload)
    input_id = post_response.json()["input_id"]

    get_response = client.get(f"/api/reconciliation/input/{input_id}")

    assert get_response.status_code == 200

    body = get_response.json()
    assert body["input_id"] == input_id
    assert body["input_type"] == "json"
    assert body["status"] == "rejected"
    assert body["ingestion_batch_id"] is None
    assert body["run_id"] is None
    assert len(body["errors"]) == 1
    assert body["errors"][0]["field"] == "invoices.0.amount"


def test_get_input_session_returns_404_for_unknown_id() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/reconciliation/input/missing-input-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Input session not found"