from __future__ import annotations

import json
import sqlite3
from dataclasses import fields, is_dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

from invomatch.domain.export import (
    FinalDecisionType,
    FinalizedInvoiceRef,
    FinalizedMatchMeta,
    FinalizedPaymentRef,
    FinalizedResult,
    FinalizedReviewMeta,
    FinalizedReviewStatus,
)

_SQLITE_TIMEOUT_SECONDS = 30.0
_SQLITE_BUSY_TIMEOUT_MS = int(_SQLITE_TIMEOUT_SECONDS * 1000)
_SQLITE_JOURNAL_MODE = "WAL"
_SQLITE_SYNCHRONOUS = "NORMAL"
_PROJECTION_VERSION = 1


class DuplicateFinalizedProjectionError(RuntimeError):
    pass


class FinalizedProjectionStore(Protocol):
    def save_results(
        self,
        *,
        tenant_id: str,
        run_id: str,
        results: list[FinalizedResult],
        created_from_run_version: int | None = None,
        source_fingerprint: str | None = None,
        created_by_system: str = "unknown",
    ) -> None:
        ...

    def get_results(
        self,
        *,
        tenant_id: str,
        run_id: str,
    ) -> list[FinalizedResult] | None:
        ...

    def exists(
        self,
        *,
        tenant_id: str,
        run_id: str,
    ) -> bool:
        ...


class SqliteFinalizedProjectionStore:
    def __init__(self, path: Path):
        self.path = path
        self._bootstrap_schema()

    def save_results(
        self,
        *,
        tenant_id: str,
        run_id: str,
        results: list[FinalizedResult],
        created_from_run_version: int | None = None,
        source_fingerprint: str | None = None,
        created_by_system: str = "unknown",
    ) -> None:
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not run_id:
            raise ValueError("run_id is required")
        if not results:
            raise ValueError("finalized projection results are required")
        if created_from_run_version is None:
            raise ValueError("created_from_run_version is required")
        if not source_fingerprint:
            raise ValueError("source_fingerprint is required")
        if not created_by_system:
            raise ValueError("created_by_system is required")

        created_at = datetime.now(UTC).isoformat()
        payload = json.dumps(
            {
                "projection_version": _PROJECTION_VERSION,
                "lineage": {
                    "created_from_run_version": created_from_run_version,
                    "source_fingerprint": source_fingerprint,
                    "created_at": created_at,
                    "created_by_system": created_by_system,
                },
                "results": [_to_primitive(result) for result in results],
            },
            sort_keys=True,
            ensure_ascii=False,
        )

        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO finalized_projections (
                        tenant_id,
                        run_id,
                        payload_json,
                        created_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        tenant_id,
                        run_id,
                        payload,
                        created_at,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise DuplicateFinalizedProjectionError(
                f"finalized projection already exists: tenant_id={tenant_id}, run_id={run_id}"
            ) from exc

    def get_results(
        self,
        *,
        tenant_id: str,
        run_id: str,
    ) -> list[FinalizedResult] | None:
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not run_id:
            raise ValueError("run_id is required")

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json
                FROM finalized_projections
                WHERE tenant_id = ?
                  AND run_id = ?
                """,
                (tenant_id, run_id),
            ).fetchone()

        if row is None:
            return None

        payload = json.loads(row["payload_json"])
        if payload.get("projection_version") != _PROJECTION_VERSION:
            raise ValueError("unsupported finalized projection payload version")

        lineage_payload = payload.get("lineage")
        if not isinstance(lineage_payload, dict):
            raise ValueError("finalized projection lineage payload must be an object")
        if lineage_payload.get("created_from_run_version") is None:
            raise ValueError("finalized projection lineage.created_from_run_version is required")
        if not lineage_payload.get("source_fingerprint"):
            raise ValueError("finalized projection lineage.source_fingerprint is required")
        if not lineage_payload.get("created_at"):
            raise ValueError("finalized projection lineage.created_at is required")
        if not lineage_payload.get("created_by_system"):
            raise ValueError("finalized projection lineage.created_by_system is required")

        results_payload = payload.get("results")
        if not isinstance(results_payload, list):
            raise ValueError("finalized projection results payload must be a list")

        return [_finalized_result_from_payload(item) for item in results_payload]

    def exists(
        self,
        *,
        tenant_id: str,
        run_id: str,
    ) -> bool:
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not run_id:
            raise ValueError("run_id is required")

        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM finalized_projections
                WHERE tenant_id = ?
                  AND run_id = ?
                LIMIT 1
                """,
                (tenant_id, run_id),
            ).fetchone()

        return row is not None

    def _bootstrap_schema(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS finalized_projections (
                    tenant_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, run_id)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_finalized_projections_tenant_run
                ON finalized_projections (tenant_id, run_id)
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=_SQLITE_TIMEOUT_SECONDS,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute(f"PRAGMA busy_timeout={_SQLITE_BUSY_TIMEOUT_MS}")
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute(f"PRAGMA journal_mode={_SQLITE_JOURNAL_MODE}")
        connection.execute(f"PRAGMA synchronous={_SQLITE_SYNCHRONOUS}")
        return connection


def _to_primitive(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)

    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, (list, tuple)):
        return [_to_primitive(item) for item in obj]

    if isinstance(obj, dict):
        return {key: _to_primitive(value) for key, value in obj.items()}

    if is_dataclass(obj):
        return {
            field.name: _to_primitive(getattr(obj, field.name))
            for field in fields(obj)
        }

    return obj


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(value)


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _finalized_result_from_payload(payload: dict[str, Any]) -> FinalizedResult:
    invoice_payload = payload["invoice"]
    match_payload = payload["match"]
    review_payload = payload["review"]

    payments = tuple(
        FinalizedPaymentRef(
            payment_id=payment_payload["payment_id"],
            payment_date=_parse_date(payment_payload.get("payment_date")),
            amount=Decimal(str(payment_payload["amount"])),
            currency=payment_payload["currency"],
        )
        for payment_payload in payload.get("payments", [])
    )

    return FinalizedResult(
        result_id=payload["result_id"],
        run_id=payload["run_id"],
        decision_type=FinalDecisionType(payload["decision_type"]),
        invoice=FinalizedInvoiceRef(
            invoice_id=invoice_payload["invoice_id"],
            invoice_number=invoice_payload["invoice_number"],
            invoice_date=_parse_date(invoice_payload.get("invoice_date")),
            amount=Decimal(str(invoice_payload["amount"])),
            currency=invoice_payload["currency"],
            vendor_name=invoice_payload.get("vendor_name"),
        ),
        payments=payments,
        match=FinalizedMatchMeta(
            confidence=(
                None
                if match_payload.get("confidence") is None
                else Decimal(str(match_payload["confidence"]))
            ),
            method=match_payload["method"],
            matched_amount=Decimal(str(match_payload["matched_amount"])),
            difference_amount=Decimal(str(match_payload["difference_amount"])),
        ),
        review=FinalizedReviewMeta(
            status=FinalizedReviewStatus(review_payload["status"]),
            reviewed_by=review_payload.get("reviewed_by"),
            reviewed_at=_parse_datetime(review_payload.get("reviewed_at")),
        ),
    )
