from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ExportWriter:
    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or (Path("output") / "exports")
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def export_path_for(self, run_id: str, export_format: str) -> Path:
        return self._base_dir / f"run_{run_id}_export.{export_format}"

    def write_json(self, *, run_id: str, payload: dict[str, Any]) -> Path:
        path = self.export_path_for(run_id, "json")
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
        return path