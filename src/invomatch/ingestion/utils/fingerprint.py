from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel


def _to_canonical_data(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", exclude_none=False)

    if isinstance(value, dict):
        return {key: _to_canonical_data(val) for key, val in sorted(value.items())}

    if isinstance(value, list):
        return [_to_canonical_data(item) for item in value]

    return value


def canonical_json(value: Any) -> str:
    canonical = _to_canonical_data(value)
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint_payload(value: Any) -> str:
    payload = canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_idempotency_key(payload_kind: str, payload_fingerprint: str) -> str:
    return f"{payload_kind}:{payload_fingerprint}"