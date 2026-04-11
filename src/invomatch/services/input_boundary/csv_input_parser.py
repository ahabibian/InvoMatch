from __future__ import annotations

import csv
from io import StringIO


class CsvInputParser:
    REQUIRED_HEADERS = [
        "record_type",
        "id",
        "date",
        "amount",
        "currency",
        "reference",
    ]

    def parse(self, content: str) -> list[dict[str, str]]:
        reader = csv.DictReader(StringIO(content))

        if reader.fieldnames is None:
            raise ValueError("CSV file must include a header row")

        normalized_headers = [header.strip() for header in reader.fieldnames]

        missing_headers = [
            header for header in self.REQUIRED_HEADERS
            if header not in normalized_headers
        ]
        if missing_headers:
            raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")

        rows: list[dict[str, str]] = []
        for row in reader:
            normalized_row: dict[str, str] = {}
            for key, value in row.items():
                if key is None:
                    continue
                normalized_row[key.strip()] = "" if value is None else str(value).strip()
            rows.append(normalized_row)

        return rows