from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime

from invomatch.domain.security import AuthenticatedPrincipal, Role, UserStatus


@dataclass(frozen=True)
class TokenRecord:
    token: str
    principal: AuthenticatedPrincipal
    expires_at: datetime | None = None
    revoked: bool = False

    def is_expired(self, *, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False

        effective_now = now or datetime.now(UTC)
        expires_at = self.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)

        return effective_now >= expires_at


class StaticTokenProvider:
    def __init__(self, seed_tokens_json: str) -> None:
        self._records = self._load(seed_tokens_json)

    def _load(self, seed_tokens_json: str) -> dict[str, TokenRecord]:
        raw_items = json.loads(seed_tokens_json)
        records: dict[str, TokenRecord] = {}

        for item in raw_items:
            token = str(item["token"]).strip()
            principal = AuthenticatedPrincipal(
                user_id=str(item["user_id"]).strip(),
                username=str(item["username"]).strip(),
                role=Role(str(item["role"]).strip()),
                status=UserStatus(str(item["status"]).strip()),
                auth_source="internal_token",
                tenant_id=str(item.get("tenant_id", "tenant-test")).strip(),
            )

            expires_at_raw = item.get("expires_at")
            expires_at = None
            if expires_at_raw is not None and str(expires_at_raw).strip():
                expires_at = datetime.fromisoformat(
                    str(expires_at_raw).strip().replace("Z", "+00:00")
                )

            records[token] = TokenRecord(
                token=token,
                principal=principal,
                expires_at=expires_at,
                revoked=bool(item.get("revoked", False)),
            )

        return records

    def get_token_record(self, token: str) -> TokenRecord | None:
        return self._records.get(token)

    def get_principal_for_token(self, token: str) -> AuthenticatedPrincipal | None:
        record = self.get_token_record(token)
        if record is None:
            return None
        return record.principal