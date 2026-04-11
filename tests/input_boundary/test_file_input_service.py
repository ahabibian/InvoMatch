from __future__ import annotations

from invomatch.services.input_boundary.file_input_service import FileInputService


def test_validate_file_accepts_valid_csv() -> None:
    service = FileInputService()

    csv_content = (
        "record_type,id,date,amount,currency,reference\n"
        "invoice,inv-001,2026-04-12,100.00,USD,ref-001\n"
        "payment,pay-001,2026-04-12,100.00,USD,ref-001\n"
    ).encode("utf-8")

    errors = service.validate_file(
        filename="input.csv",
        content_type="text/csv",
        content_bytes=csv_content,
    )

    assert errors == []


def test_validate_file_rejects_missing_header() -> None:
    service = FileInputService()

    csv_content = (
        "record_type,id,date,amount,currency\n"
        "invoice,inv-001,2026-04-12,100.00,USD\n"
    ).encode("utf-8")

    errors = service.validate_file(
        filename="input.csv",
        content_type="text/csv",
        content_bytes=csv_content,
    )

    assert len(errors) == 1
    assert errors[0].code == "invalid_csv"


def test_build_ingestion_request_maps_invoice_and_payment() -> None:
    service = FileInputService()

    csv_content = (
        "record_type,id,date,amount,currency,reference\n"
        "invoice,inv-001,2026-04-12,100.00,USD,ref-001\n"
        "payment,pay-001,2026-04-12,100.00,USD,ref-001\n"
    ).encode("utf-8")

    result = service.build_ingestion_request(
        filename="input.csv",
        content_type="text/csv",
        content_bytes=csv_content,
    )

    assert len(result["invoices"]) == 1
    assert len(result["payments"]) == 1
    assert result["invoices"][0]["id"] == "inv-001"
    assert result["payments"][0]["id"] == "pay-001"