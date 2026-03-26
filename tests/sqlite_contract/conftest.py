from pathlib import Path

import pytest

from invomatch.services.run_store import SqliteRunStore


@pytest.fixture
def run_store(tmp_path: Path):
    db = tmp_path / "contract.sqlite3"
    return SqliteRunStore(db)