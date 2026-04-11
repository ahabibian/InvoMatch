from __future__ import annotations


class CsvInputMapper:
    def map(self, rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
        invoices: list[dict[str, str]] = []
        payments: list[dict[str, str]] = []

        for index, row in enumerate(rows):
            record_type = row.get("record_type", "").strip().lower()
            if record_type not in {"invoice", "payment"}:
                raise ValueError(f"Invalid record_type at row {index + 1}: {record_type}")

            entity = {
                "id": row.get("id", "").strip(),
                "date": row.get("date", "").strip(),
                "amount": row.get("amount", "").strip(),
                "currency": row.get("currency", "").strip(),
                "reference": row.get("reference", "").strip() or None,
            }

            missing_fields = [
                field_name for field_name in ("id", "date", "amount", "currency")
                if not entity[field_name]
            ]
            if missing_fields:
                raise ValueError(
                    f"Missing required values at row {index + 1}: {', '.join(missing_fields)}"
                )

            if record_type == "invoice":
                invoices.append(entity)
            else:
                payments.append(entity)

        return {
            "invoices": invoices,
            "payments": payments,
        }