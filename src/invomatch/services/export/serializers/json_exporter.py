from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from decimal import Decimal
from typing import Any

from invomatch.domain.export import ExportBundle


def _to_primitive(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)

    if hasattr(obj, "isoformat"):
        try:
            return obj.isoformat()
        except Exception:
            pass

    if isinstance(obj, (list, tuple)):
        return [_to_primitive(x) for x in obj]

    if isinstance(obj, dict):
        return {k: _to_primitive(v) for k, v in obj.items()}

    if is_dataclass(obj):
        return {
            field.name: _to_primitive(getattr(obj, field.name))
            for field in fields(obj)
        }

    return obj


class JsonExporter:
    def export(self, bundle: ExportBundle) -> bytes:
        data = _to_primitive(bundle)
        return json.dumps(
            data,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        ).encode("utf-8")
