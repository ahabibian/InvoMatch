from __future__ import annotations

import json
from dataclasses import dataclass

from invomatch.domain.security import AuthenticatedPrincipal, Role, UserStatus


@dataclass(frozen=True)
class TokenRecord:
    token: str
    principal: AuthenticatedPrincipal


class StaticTokenProvider:
    def __init__(self, seed_tokens_json: str) -> None:
        self._records = self._load(seed_tokens_json)

    def _load(self, seed_tokens_json: str) -> dict[str, AuthenticatedPrincipal]:
        raw_items = json.loads(seed_tokens_json)
        records: dict[str, AuthenticatedPrincipal] = {}

        for item in raw_items:
            token = str(item["token"]).strip()
            principal = AuthenticatedPrincipal(
                user_id=str(item["user_id"]).strip(),
                username=str(item["username"]).strip(),
                role=Role(str(item["role"]).strip()),
                status=UserStatus(str(item["status"]).strip()),
                auth_source="internal_token",
            )
            records[token] = principal

        return records

    def get_principal_for_token(self, token: str) -> AuthenticatedPrincipal | None:
        return self._records.get(token)