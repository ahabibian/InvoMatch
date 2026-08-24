from __future__ import annotations

import json
from pathlib import Path
import sqlite3

import pytest

from invomatch.config.loaders import load_settings_from_environment
from invomatch.main import create_app
from invomatch.operations.pilot_state import (
    PilotStateError,
    create_backup,
    restore_backup,
    verify_state,
)


def _database(path: Path, value: str = "canonical-truth") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE evidence (value TEXT NOT NULL)")
        connection.execute("INSERT INTO evidence VALUES (?)", (value,))


def test_backup_restore_roundtrip_preserves_databases_and_artifacts(tmp_path: Path) -> None:
    state = tmp_path / "active"
    _database(state / "reconciliation_runs.sqlite3")
    artifact = state / "exports" / "tenant" / "evidence.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text('{"run_id":"run-34-3"}', encoding="utf-8")

    bundle = create_backup(
        state,
        tmp_path / "backups" / "backup-001",
        application_version="0.1.0",
        source_commit_sha="abc123",
        environment="production",
    )
    restored = restore_backup(bundle, tmp_path / "restored")

    assert verify_state(restored)["sqlite_files"] == ["reconciliation_runs.sqlite3"]
    assert (restored / "exports/tenant/evidence.json").read_text(encoding="utf-8") == artifact.read_text(encoding="utf-8")
    metadata = json.loads((bundle / "pilot-state-backup.json").read_text(encoding="utf-8"))
    assert metadata["source_commit_sha"] == "abc123"
    assert metadata["secrets_included"] is False
    assert "ci-pilot-credential" not in json.dumps(metadata)


def test_backup_fails_for_missing_state_and_existing_destination(tmp_path: Path) -> None:
    with pytest.raises(PilotStateError, match="does not exist"):
        create_backup(
            tmp_path / "missing", tmp_path / "bundle",
            application_version="0.1.0", source_commit_sha="abc", environment="production",
        )
    state = tmp_path / "state"
    _database(state / "store.sqlite3")
    destination = tmp_path / "exists"
    destination.mkdir()
    with pytest.raises(PilotStateError, match="already exists"):
        create_backup(
            state, destination,
            application_version="0.1.0", source_commit_sha="abc", environment="production",
        )


def test_restore_rejects_overwrite_corruption_and_missing_payload(tmp_path: Path) -> None:
    state = tmp_path / "state"
    _database(state / "store.sqlite3")
    bundle = create_backup(
        state, tmp_path / "bundle",
        application_version="0.1.0", source_commit_sha="abc", environment="production",
    )
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "keep").write_text("do-not-overwrite", encoding="utf-8")
    with pytest.raises(PilotStateError, match="not empty"):
        restore_backup(bundle, occupied)
    (bundle / "state/store.sqlite3").write_bytes(b"corrupt")
    with pytest.raises(PilotStateError, match="hash verification"):
        restore_backup(bundle, tmp_path / "corrupt-restore")
    (bundle / "pilot-state-backup.json").unlink()
    with pytest.raises(PilotStateError, match="metadata or state payload"):
        restore_backup(bundle, tmp_path / "missing-restore")


def test_create_app_injects_configured_match_store_and_ingestion_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state = tmp_path / "pilot-state"
    monkeypatch.setenv("INVOMATCH_ENV", "test")
    monkeypatch.setenv("INVOMATCH_MATCH_RECORD_STORE_PATH", str(state / "matches.sqlite3"))
    monkeypatch.setenv("INVOMATCH_INGESTION_BATCH_ROOT", str(state / "ingestion"))
    monkeypatch.setenv("INVOMATCH_RUN_STORE_PATH", str(state / "runs.sqlite3"))
    monkeypatch.setenv("INVOMATCH_REVIEW_STORE_PATH", str(state / "reviews.sqlite3"))
    monkeypatch.setenv("INVOMATCH_AUDIT_EVENT_DB_PATH", str(state / "audit.sqlite3"))
    monkeypatch.setenv("INVOMATCH_INPUT_SESSION_DB_PATH", str(state / "input.sqlite3"))
    monkeypatch.setenv("INVOMATCH_EXPORT_DIRECTORY", str(state / "exports"))

    app = create_app()

    assert app.state.persistence_dependencies.match_record_store.path == state / "matches.sqlite3"
    assert app.state.ingestion_run_runtime_adapter._batch_root == state / "ingestion"
    assert app.state.reconcile_and_save.keywords["match_record_store"].path == state / "matches.sqlite3"


def test_production_pilot_paths_are_all_under_state_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INVOMATCH_ENV", "production")
    monkeypatch.setenv("INVOMATCH_SECURITY_SEED_TOKENS_JSON", '[{"token":"safe"}]')
    settings = load_settings_from_environment()
    configured = (
        *settings.persistence.__dict__.values(),
        *settings.storage.__dict__.values(),
    )
    paths = [Path(value) for value in configured if isinstance(value, Path)]
    durable = [path for path in paths if path != Path("/tmp/invomatch") and path != Path("/var/log/invomatch")]
    assert all(path.is_relative_to(Path("/var/lib/invomatch")) for path in durable)
