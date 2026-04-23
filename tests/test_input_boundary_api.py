from __future__ import annotations

from fastapi.testclient import TestClient

from invomatch.main import create_app


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_submit_json_returns_401_without_auth() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "invoices": [{"id": "inv-001", "date": "2026-04-12", "amount": "100.00", "currency": "USD", "reference": "ref-001"}],
        "payments": [{"id": "pay-001", "date": "2026-04-12", "amount": "100.00", "currency": "USD", "reference": "ref-001"}],
    }

    response = client.post("/api/reconciliation/input/json", json=payload)
    assert response.status_code == 401


def test_submit_json_returns_403_for_viewer() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "invoices": [{"id": "inv-001", "date": "2026-04-12", "amount": "100.00", "currency": "USD", "reference": "ref-001"}],
        "payments": [{"id": "pay-001", "date": "2026-04-12", "amount": "100.00", "currency": "USD", "reference": "ref-001"}],
    }

    response = client.post(
        "/api/reconciliation/input/json",
        json=payload,
        headers=_auth_headers("viewer-token"),
    )
    assert response.status_code == 403


def test_submit_json_returns_run_created_for_valid_payload() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "invoices": [{"id": "inv-001", "date": "2026-04-12", "amount": "100.00", "currency": "USD", "reference": "ref-001"}],
        "payments": [{"id": "pay-001", "date": "2026-04-12", "amount": "100.00", "currency": "USD", "reference": "ref-001"}],
    }

    response = client.post(
        "/api/reconciliation/input/json",
        json=payload,
        headers=_auth_headers("operator-token"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "run_created"
    assert body["run_id"]


def test_submit_json_returns_rejected_for_invalid_payload() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "invoices": [{"id": "inv-001", "date": "2026-04-12", "amount": "", "currency": "USD"}],
        "payments": [{"id": "pay-001", "date": "2026-04-12", "amount": "100.00", "currency": "USD"}],
    }

    response = client.post(
        "/api/reconciliation/input/json",
        json=payload,
        headers=_auth_headers("operator-token"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["errors"][0]["field"] == "invoices.0.amount"


def test_submit_file_returns_run_created_for_valid_csv() -> None:
    app = create_app()
    client = TestClient(app)

    csv_content = (
        "record_type,id,date,amount,currency,reference\n"
        "invoice,inv-001,2026-04-12,100.00,USD,ref-001\n"
        "payment,pay-001,2026-04-12,100.00,USD,ref-001\n"
    )

    response = client.post(
        "/api/reconciliation/input/file",
        files={"file": ("input.csv", csv_content, "text/csv")},
        headers=_auth_headers("operator-token"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "run_created"
    assert body["ingestion_batch_id"] == body["input_id"]
    assert body["run_id"]


def test_submit_file_returns_rejected_for_missing_required_header() -> None:
    app = create_app()
    client = TestClient(app)

    csv_content = (
        "record_type,id,date,amount,currency\n"
        "invoice,inv-001,2026-04-12,100.00,USD\n"
        "payment,pay-001,2026-04-12,100.00,USD\n"
    )

    response = client.post(
        "/api/reconciliation/input/file",
        files={"file": ("input.csv", csv_content, "text/csv")},
        headers=_auth_headers("operator-token"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ["rejected", "failed"]
    assert body["run_id"] is None
    assert body["errors"]


def test_get_input_session_returns_created_session() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "invoices": [{"id": "inv-001", "date": "2026-04-12", "amount": "100.00", "currency": "USD", "reference": "ref-001"}],
        "payments": [{"id": "pay-001", "date": "2026-04-12", "amount": "100.00", "currency": "USD", "reference": "ref-001"}],
    }

    post_response = client.post(
        "/api/reconciliation/input/json",
        json=payload,
        headers=_auth_headers("operator-token"),
    )
    input_id = post_response.json()["input_id"]

    get_response = client.get(
        f"/api/reconciliation/input/{input_id}",
        headers=_auth_headers("viewer-token"),
    )
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["input_id"] == input_id
    assert body["status"] == "run_created"


def test_get_input_session_returns_404_for_unknown_id() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get(
        "/api/reconciliation/input/missing-input-id",
        headers=_auth_headers("viewer-token"),
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Input session not found"