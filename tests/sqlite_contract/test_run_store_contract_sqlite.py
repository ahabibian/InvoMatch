from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


_contract_path = Path(__file__).resolve().parents[1] / "test_run_store_contract.py"
_spec = importlib.util.spec_from_file_location("run_store_contract_module", _contract_path)
_contract = importlib.util.module_from_spec(_spec)
assert _spec is not None
assert _spec.loader is not None
_spec.loader.exec_module(_contract)

sample_run = _contract.sample_run

for _name, _value in vars(_contract).items():
    if _name.startswith("test_"):
        globals()[_name] = _value

pytestmark = pytest.mark.sqlite_contract