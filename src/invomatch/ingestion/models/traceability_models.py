from __future__ import annotations

from pydantic import BaseModel


class RawTraceReference(BaseModel):
    payload_fingerprint: str
    payload_kind: str
    schema_version: str
    rule_version: str