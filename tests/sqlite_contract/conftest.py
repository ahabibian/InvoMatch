from __future__ import annotations

from pathlib import Path

import pytest

from invomatch.services.run_store import SqliteRunStore


@pytest.fixture
def sqlite_contract_db_path(tmp_path: Path) -> Path:
    """
    Dedicated SQLite database path for each contract test.

    Using tmp_path keeps each test isolated and avoids cross-test leakage.
    """
    return tmp_path / "sqlite_contract.sqlite3"


@pytest.fixture
def run_store(sqlite_contract_db_path: Path) -> SqliteRunStore:
    """
    SQLite-backed RunStore fixture for contract binding.

    Important:
    This binds the contract suite to the current SQLite implementation,
    but it does NOT guarantee contract conformance.
    Real mismatches should now fail inside the tests meaningfully.
    """
    return SqliteRunStore(sqlite_contract_db_path)