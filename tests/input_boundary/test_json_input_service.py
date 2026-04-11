from __future__ import annotations

from invomatch.services.input_boundary.json_input_service import JsonInputService


def test_validate_accepts_valid_payload() -> None:
    service = JsonInputService()

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

    errors = service.validate(payload)

    assert errors == []


def test_validate_rejects_invalid_nested_field() -> None:
    service = JsonInputService()

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

    errors = service.validate(payload)

    assert len(errors) == 1
    assert errors[0].field == "invoices.0.amount"
    assert errors[0].type == "validation_error"


def test_build_ingestion_request_normalizes_using_contract() -> None:
    service = JsonInputService()

    payload = {
        "invoices": [
            {
                "id": "inv-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
                "reference": "  ref-001  ",
            }
        ],
        "payments": [
            {
                "id": "pay-001",
                "date": "2026-04-12",
                "amount": "100.00",
                "currency": "USD",
                "reference": "  ref-001  ",
            }
        ],
    }

    result = service.build_ingestion_request(payload)

    assert result["invoices"][0]["reference"] == "ref-001"
    assert result["payments"][0]["reference"] == "ref-001"